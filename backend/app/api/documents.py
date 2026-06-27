"""
app/api/documents.py
====================
Routes for uploading, listing, and summarising PDF documents.
Every endpoint requires authentication — the current_user dependency
verifies the JWT and loads the User from Postgres on each request.
"""

import hashlib
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.config import settings
from app.db.models import Document, DocumentChunk, User
from app.db.session import get_session
from app.schemas.document_schemas import (
    DocumentUploadResponse,
    DocumentSummaryResponse,
    UploadResponse,
)
from app.rag.pipeline import generate_document_summary, ingest_document

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UploadResponse:
    """
    Saves a PDF to disk and runs the full RAG ingestion pipeline on it.
    Ingestion (chunking + embedding) runs synchronously so the client receives
    confirmation only after the document is actually searchable.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    contents = await file.read()

    # SHA-256 of the raw bytes lets the application detect if the same PDF is
    # re-uploaded later, without storing the file twice
    sha256_digest = hashlib.sha256(contents).hexdigest()

    # UUID prefix guarantees uniqueness even when two users upload a file with
    # the same filename (e.g. both upload "thesis.pdf")
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    target_path = settings.uploads_dir / unique_filename

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(contents)

    # The Document row is inserted first so it has a primary key that the
    # DocumentChunk rows can reference as a foreign key during ingestion
    document = Document(
        user_id=current_user.id,
        filename=unique_filename,
        content_hash=sha256_digest,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)

    await ingest_document(document.id, target_path, current_user.id, session)
    return UploadResponse(document=document, message="Upload successful. Your document is now searchable.")


@router.get("/", response_model=list[DocumentUploadResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[DocumentUploadResponse]:
    """
    Returns all documents owned by the authenticated user, newest first.
    The user_id filter prevents one user from listing another user's documents.
    """
    statement = (
        select(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.upload_date.desc())
    )
    results = await session.scalars(statement)
    return results.all()


@router.post("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def document_summary(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DocumentSummaryResponse:
    """
    Generates an AI executive summary for one document.
    Filtering by both document_id AND user_id prevents a user from triggering
    summarisation on another user's document by guessing the integer ID.
    """
    document = await session.scalar(
        select(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    summary = await generate_document_summary(document_id, current_user.id, session)
    return summary
