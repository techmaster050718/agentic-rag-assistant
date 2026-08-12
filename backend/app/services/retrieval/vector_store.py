"""
Supabase pgvector-backed vector store.

IMPORTANT: The supabase-py client (v2.x) is SYNCHRONOUS by default.
All .execute() calls are blocking — we wrap them in asyncio.to_thread()
to keep the FastAPI async event loop free.
"""
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)


def _make_client() -> Optional[Client]:
    """Create the Supabase client, returning None if credentials are missing."""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        logger.warning(
            "SUPABASE_URL or SUPABASE_SERVICE_KEY not set — "
            "vector store will be unavailable."
        )
        return None
    try:
        return create_client(url, key)
    except Exception as exc:
        logger.error(f"Failed to create Supabase client: {exc}")
        return None


class SupabaseVectorStore:
    """Supabase pgvector-based vector store with async wrappers."""

    TABLE = "document_embeddings"

    def __init__(self) -> None:
        self._client: Optional[Client] = _make_client()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_client(self) -> Client:
        if self._client is None:
            raise RuntimeError(
                "Supabase client is not initialized. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables."
            )
        return self._client

    # ------------------------------------------------------------------
    # Public async API (new-style: list of dicts)
    # ------------------------------------------------------------------

    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Insert a batch of document chunks into the vector store."""
        client = self._require_client()
        rows = [
            {
                "document_id": doc.get("document_id"),
                "chunk_index": doc.get("chunk_index", 0),
                "content": doc.get("content"),
                "embedding": doc.get("embedding"),
                "metadata": doc.get("metadata", {}),
            }
            for doc in documents
        ]
        await asyncio.to_thread(
            lambda: client.table(self.TABLE).insert(rows).execute()
        )
        logger.info(f"Inserted {len(rows)} chunks into vector store.")

    async def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Dict]:
        """Cosine similarity search via the match_document_embeddings RPC."""
        client = self._require_client()
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        rpc_args: Dict[str, Any] = {
            "query_embedding": embedding_str,
            "match_threshold": 0.5,
            "match_count": k,
        }
        if document_id:
            rpc_args["filter_document_id"] = document_id

        try:
            result = await asyncio.to_thread(
                lambda: client.rpc("match_document_embeddings", rpc_args).execute()
            )
            return result.data or []
        except Exception as exc:
            logger.error(f"similarity_search failed: {exc}")
            return []

    async def delete_by_metadata(self, key: str, value: str) -> None:
        """Delete all chunks belonging to a document."""
        client = self._require_client()
        if key == "document_id":
            await asyncio.to_thread(
                lambda: client.table(self.TABLE).delete().eq("document_id", value).execute()
            )
            logger.info(f"Deleted embeddings for document_id={value}")

    async def get_collection_count(self) -> int:
        """Return total number of embedding rows."""
        client = self._require_client()
        result = await asyncio.to_thread(
            lambda: client.table(self.TABLE).select("id", count="exact").execute()
        )
        return result.count or 0

    # ------------------------------------------------------------------
    # Compatibility shim — keeps ingest.py / nodes.py unchanged
    # ------------------------------------------------------------------

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        ChromaDB-style search interface used by nodes.py.
        Translates 'where' filter into document_id for similarity_search().
        """
        document_id: Optional[str] = None
        if where and "document_id" in where:
            val = where["document_id"]
            if isinstance(val, dict) and "$in" in val:
                ids = val["$in"]
                document_id = ids[0] if ids else None
            else:
                document_id = str(val)

        results = await self.similarity_search(
            query_embedding=query_embedding,
            k=top_k,
            document_id=document_id,
        )
        return [
            {
                "id": str(r.get("id", "")),
                "content": r.get("content", ""),
                "metadata": r.get("metadata", {}),
                "score": float(r.get("similarity", 0.0)),
            }
            for r in results
        ]


# ---------------------------------------------------------------------------
# Module-level singleton — imported directly by callers
# ---------------------------------------------------------------------------
vector_store = SupabaseVectorStore()


def get_vector_store() -> SupabaseVectorStore:
    """Dependency-injection helper used by nodes.py and retriever.py."""
    return vector_store