"""
app/schemas/document_schemas.py
================================
Pydantic schemas for the documents API.

Covers upload responses, document listings, summary responses,
and the source citation metadata attached to chat answers.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """
    A single document record returned by the listing and upload endpoints.
    The filename includes the UUID prefix added on upload.
    """

    id: int
    filename: str
    upload_date: datetime

    class Config:
        from_attributes = True  # Read from SQLAlchemy ORM objects (Pydantic v2)


class DocumentMetadata(BaseModel):
    """
    Source citation attached to a chat answer.

    Each citation tells the user exactly where in which document the
    answer came from so they can verify the information themselves.
    """

    document:   str    # Filename of the source document
    page:       int    # Page number within that document (1-indexed)
    chunk_id:   int    # Which chunk on that page (useful for debugging)
    similarity: float  # Cosine similarity score (0 to 1; higher = more relevant)



class UploadResponse(BaseModel):
    """Top-level response returned by POST /documents/upload."""

    document: DocumentUploadResponse
    message:  str  # e.g. "Upload successful. Your document is now searchable."


class DocumentSummaryResponse(BaseModel):
    """
    Structured AI summary returned by POST /documents/{id}/summary.

    The LLM is prompted to return a summary paragraph plus two bullet-point
    lists; we parse and expose them separately for easy UI rendering.
    """

    document_id: int
    summary:     str        # Full executive summary paragraph
    key_points:  List[str]  # Parsed bullet list of key points
    findings:    List[str]  # Parsed bullet list of important findings
