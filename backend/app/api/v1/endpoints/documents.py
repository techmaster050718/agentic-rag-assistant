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
async def delete_document(document_id: str, db: DBSession) -> None:
    """Delete a document and its embeddings."""
    from app.services.retrieval.vector_store import vector_store

    # 1. Fetch document from Postgres
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # 2. Delete vector chunks from Supabase
    try:
        await vector_store.delete_by_metadata(key="document_id", value=str(document_id))
    except Exception as e:
        logger.error(f"Error deleting vectors for {document_id}: {e}")

    # 3. Delete from Postgres
    await db.delete(doc)
    await db.commit()

    return None
