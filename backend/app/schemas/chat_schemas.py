from datetime import datetime
from typing import List
from pydantic import BaseModel
from app.schemas.document_schemas import DocumentMetadata

class ChatRequest(BaseModel):
    question: str
    document_ids: list[int] | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[DocumentMetadata]

class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True
