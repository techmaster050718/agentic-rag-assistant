from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    status: str


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
