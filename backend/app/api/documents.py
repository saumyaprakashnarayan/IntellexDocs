import hashlib
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user
from app.core.config import settings
from app.db.models import Document, DocumentChunk, User
from app.db.session import get_session
from app.schemas.document_schemas import DocumentUploadResponse, DocumentSummaryResponse, UploadResponse
from app.rag.pipeline import generate_document_summary, ingest_document

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF uploads are supported.")

    contents = await file.read()
    sha256_digest = hashlib.sha256(contents).hexdigest()
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    target_path = settings.uploads_dir / filename
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(contents)

    document = Document(user_id=current_user.id, filename=filename, content_hash=sha256_digest)
    session.add(document)
    await session.commit()
    await session.refresh(document)

    await ingest_document(document.id, target_path, current_user.id, session)

    return UploadResponse(document=document, message="Upload successful.")

@router.get("/", response_model=list[DocumentUploadResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[DocumentUploadResponse]:
    statement = select(Document).filter(Document.user_id == current_user.id).order_by(Document.upload_date.desc())
    results = await session.scalars(statement)
    return results.all()

@router.post("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def document_summary(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DocumentSummaryResponse:
    statement = select(Document).filter(Document.id == document_id, Document.user_id == current_user.id)
    document = await session.scalar(statement)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    summary = await generate_document_summary(document_id, current_user.id, session)
    return summary
