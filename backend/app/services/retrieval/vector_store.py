from typing import List, Dict, Any, Optional
from supabase import Client
import asyncio

class SupabaseVectorStore:
    """Supabase pgvector-based vector store"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table_name = "document_embeddings"
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to vector store"""
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
        """Search for similar documents"""
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        try:
            result = await self.client.rpc(
                "match_document_embeddings",
                {
                    "query_embedding": embedding_str,
                    "match_threshold": 0.5,
                    "match_count": k
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    async def delete_by_metadata(self, key: str, value: str) -> None:
        """Delete documents by metadata key-value"""
        if key == "document_id":
            await self.client.table(self.table_name).delete().eq("document_id", value).execute()
    
    async def get_collection_count(self) -> int:
        """Get total number of embeddings"""
        result = await self.client.table(self.table_name).select("*", count="exact").execute()
        return result.count if result.count else 0