import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import os

logger = logging.getLogger(__name__)


class SupabaseVectorStore:
    """Supabase pgvector-based vector store"""

    def __init__(self):
        # Initialize Supabase client internally from env
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client = create_client(supabase_url, supabase_key)
        self.table_name = "document_embeddings"

    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to vector store (new-style: list of dicts)."""
        for doc in documents:
            await self.client.table(self.table_name).insert({
                "document_id": doc.get("document_id"),
                "chunk_index": doc.get("chunk_index", 0),
                "content": doc.get("content"),
                "embedding": doc.get("embedding"),
                "metadata": doc.get("metadata", {})
            }).execute()

    async def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 4,
        document_id: Optional[str] = None
    ) -> List[Dict]:
        """Search for similar documents using pgvector cosine similarity."""
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        rpc_args = {
            "query_embedding": embedding_str,
            "match_threshold": 0.5,
            "match_count": k
        }
        if document_id:
            rpc_args["filter_document_id"] = document_id

        try:
            result = await self.client.rpc(
                "match_document_embeddings",
                rpc_args
            ).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    async def delete_by_metadata(self, key: str, value: str) -> None:
        """Delete documents by metadata key-value."""
        if key == "document_id":
            await self.client.table(self.table_name).delete().eq("document_id", value).execute()

    async def get_collection_count(self) -> int:
        """Get total number of embeddings."""
        result = await self.client.table(self.table_name).select("*", count="exact").execute()
        return result.count if result.count else 0

    # ------------------------------------------------------------------
    # Compatibility shim — keeps callers (ingest.py, nodes.py) working
    # without any changes to their code.
    # ------------------------------------------------------------------

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Alias for original ChromaDB-style search interface."""
        document_id = None
        if where and "document_id" in where:
            val = where["document_id"]
            if isinstance(val, dict) and "$in" in val:
                document_id = val["$in"][0] if val["$in"] else None
            else:
                document_id = val

        results = await self.similarity_search(
            query_embedding=query_embedding,
            k=top_k,
            document_id=document_id
        )

        return [
            {
                "id": str(r.get("id")),
                "content": r.get("content"),
                "metadata": r.get("metadata", {}),
                "score": float(r.get("similarity", 0.0)),
            }
            for r in results
        ]


# Single global instance — imported directly by callers
vector_store = SupabaseVectorStore()


def get_vector_store() -> SupabaseVectorStore:
    """Returns the initialized vector store instance."""
    return vector_store