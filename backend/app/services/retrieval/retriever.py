from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.services.retrieval.vector_store import get_vector_store

logger = logging.getLogger(__name__)


async def retrieve(
    query: str,
    document_ids: list[str] | None = None,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant chunks for a query.

    Args:
        query: The user's natural language query.
        document_ids: Optional list of document IDs to filter by.
        top_k: Number of results to return. Defaults to settings.RETRIEVAL_TOP_K.

    Returns:
        List of dicts with 'content', 'metadata', and 'score'.
    """
    k = top_k or settings.RETRIEVAL_TOP_K
    store = get_vector_store()

    search_kwargs: dict[str, Any] = {"k": k}
    if document_ids:
        search_kwargs["filter"] = {"document_id": {"$in": document_ids}}

    results = await store.asimilarity_search_with_relevance_scores(
        query=query, **search_kwargs
    )

    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),
        }
        for doc, score in results
    ]
