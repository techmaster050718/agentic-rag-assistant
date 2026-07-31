from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    document_ids: Optional[list[str]] = None
    chat_history: Optional[list[dict[str, Any]]] = None


class Citation(BaseModel):
    id: int
    source: str
    page: Optional[int] = None
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = []
    session_id: str
    agent_steps: list[str] = []
