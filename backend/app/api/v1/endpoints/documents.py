import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from app.api.deps import DBSession
from app.models.document import Document
from app.schemas.document import DocumentListResponse, DocumentResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List all ingested documents",
)
async def list_documents(db: DBSession) -> DocumentListResponse:
    """Return metadata for all ingested documents."""
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    docs = result.scalars().all()
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in docs],
        total=len(docs),
    )


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
    response_class=Response,
    summary="Delete a document",
)
async def delete_document(document_id: str) -> None:
    """Delete a document and its embeddings."""
    # TODO: Remove from vector store and DB
    return None
