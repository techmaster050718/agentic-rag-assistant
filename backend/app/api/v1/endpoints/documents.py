from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.schemas.document import DocumentResponse, DocumentListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List all ingested documents",
)
async def list_documents() -> DocumentListResponse:
    """Return metadata for all ingested documents."""
    # In a full implementation, this queries PostgreSQL for document metadata
    return DocumentListResponse(documents=[], total=0)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get a single document by ID",
)
async def get_document(document_id: str) -> DocumentResponse:
    """Return metadata for a single document."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document {document_id} not found",
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
async def delete_document(document_id: str) -> None:
    """Delete a document and its embeddings."""
    # TODO: Remove from vector store and DB
    return None
