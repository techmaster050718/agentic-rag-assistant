from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def rerank(
    results: list[dict[str, Any]],
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Re-rank retrieved chunks. Currently uses score-based sorting.
    Can be extended with a cross-encoder reranker (e.g., Cohere Rerank).

    Args:
        results: List of retrieval results with 'score' or 'hybrid_score'.
        query: The original query (used by cross-encoders).
        top_k: Number of results to return.

    Returns:
        Re-ranked list of results.
    """
    score_key = "hybrid_score" if "hybrid_score" in (results[0] if results else {}) else "score"
    ranked = sorted(results, key=lambda x: x.get(score_key, 0.0), reverse=True)
    return ranked[:top_k]