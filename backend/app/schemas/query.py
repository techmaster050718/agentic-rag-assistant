# backend/app/schemas/query.py
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class QueryRequest(BaseModel):
    session_id: Optional[UUID] = None
    query: str

class Citation(BaseModel):
    index: int
    source: str
    content_snippet: str

class QueryResponse(BaseModel):
    session_id: UUID
    answer: str
    citations: List[Citation]