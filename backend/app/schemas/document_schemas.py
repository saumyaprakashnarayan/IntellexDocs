from datetime import datetime
from typing import List
from pydantic import BaseModel

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime

    class Config:
        orm_mode = True

class DocumentSummaryResponse(BaseModel):
    document_id: int
    summary: str
    key_points: List[str]
    findings: List[str]

class DocumentMetadata(BaseModel):
    document: str
    page: int
    chunk_id: int
    similarity: float

class SearchResult(BaseModel):
    content: str
    metadata: DocumentMetadata

class UploadResponse(BaseModel):
    document: DocumentUploadResponse
    message: str
