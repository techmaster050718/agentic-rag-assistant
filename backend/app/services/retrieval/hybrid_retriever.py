from __future__ import annotations

import logging
import math
from collections import defaultdict
from typing import Any

from rank_bm25 import BM25Okapi

from app.core.config import settings
from app.services.retrieval.retriever import retrieve as vector_retrieve

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


async def hybrid_retrieve(
    query: str,
    corpus: list[str],
    corpus_metadata: list[dict[str, Any]],
    top_k: int | None = None,
    alpha: float | None = None,
) -> list[dict[str, Any]]:
    """
    Hybrid retrieval combining dense vector search (alpha) and BM25 (1-alpha).

    Args:
        query: The user query.
        corpus: List of document text chunks for BM25.
        corpus_metadata: Metadata corresponding to corpus chunks.
        top_k: Number of results.
        alpha: Weight for vector search (0=BM25 only, 1=vector only).
    """
    k = top_k or settings.RETRIEVAL_TOP_K
    a = alpha if alpha is not None else settings.HYBRID_ALPHA

    # --- Dense retrieval ---
    vector_results = await vector_retrieve(query, top_k=k * 2)
    vector_scores: dict[str, float] = {
        r["content"]: r["score"] for r in vector_results
    }

    # --- BM25 ---
    if corpus:
        tokenized_corpus = [_tokenize(doc) for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_raw_scores = bm25.get_scores(_tokenize(query))
        max_bm25 = max(bm25_raw_scores) if max(bm25_raw_scores) > 0 else 1.0
        bm25_norm = [s / max_bm25 for s in bm25_raw_scores]
    else:
        bm25_norm = []

    # --- Merge ---
    merged: dict[str, dict[str, Any]] = {}

    for result in vector_results:
        content = result["content"]
        merged[content] = {
            **result,
            "hybrid_score": a * result["score"],
        }

    for i, text in enumerate(corpus):
        bm25_score = bm25_norm[i] if i < len(bm25_norm) else 0.0
        if text in merged:
            merged[text]["hybrid_score"] += (1 - a) * bm25_score
        else:
            merged[text] = {
                "content": text,
                "metadata": corpus_metadata[i] if i < len(corpus_metadata) else {},
                "score": bm25_score,
                "hybrid_score": (1 - a) * bm25_score,
            }

    ranked = sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)
    return ranked[:k]
