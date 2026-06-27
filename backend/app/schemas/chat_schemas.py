"""
app/schemas/chat_schemas.py
============================
Pydantic schemas for the chat / Q&A API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.document_schemas import DocumentMetadata


class ChatRequest(BaseModel):
    """
    Request body for POST /chat/query.

    document_ids is optional — if omitted, all of the user's documents
    are searched.  Providing a subset lets users narrow the search scope.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="The natural-language question to ask about your documents.",
        examples=["What is the main finding of the paper?"],
    )
    # Optional list of document IDs to restrict the search to.
    # If None or empty, all uploaded documents are searched.
    document_ids: Optional[List[int]] = None


class ChatResponse(BaseModel):
    """
    Response from POST /chat/query.

    Contains the AI-generated answer and a list of source citations so the
    user can verify the information in the original document.
    """

    answer:  str                     # The full AI-generated response text
    sources: List[DocumentMetadata]  # Which pages/chunks the answer came from


class ChatHistoryResponse(BaseModel):
    """
    A single Q&A record returned by GET /chat/history.

    Returned newest-first so the most recent exchanges appear at the top.
    """

    id:         int
    question:   str
    answer:     str
    created_at: datetime

    class Config:
        from_attributes = True  # Read from SQLAlchemy ORM objects (Pydantic v2)
