import chromadb
import time
from chromadb.config import Settings
from app.core.config import settings
from app.core.logging import get_logger
from typing import List, Dict, Any

logger = get_logger(__name__)

class VectorStore:
    def __init__(self):
        max_retries = 30
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self.client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                    settings=Settings(allow_reset=True),
                )
                self.client.list_collections()
                self.collection = self.client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(
                    "Initialized ChromaDB vector store",
                    collection=settings.CHROMA_COLLECTION_NAME,
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error("Failed to connect to ChromaDB after retries", error=str(e))
                    raise
                logger.warning(
                    "ChromaDB not ready, retrying...",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                )
                time.sleep(retry_delay)

    def add_documents(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]]):
        self.collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        logger.info("Added documents to vector store", count=len(ids))

    def search(self, query_embedding: List[float], top_k: int = 5, where: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where, include=["metadatas", "documents", "distances"])
        formatted_results = []
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i] if results['distances'] else 0.0
                formatted_results.append({"id": doc_id, "content": results['documents'][0][i], "metadata": results['metadatas'][0][i], "score": max(0.0, 1.0 - distance)})
        return formatted_results

    def delete_by_metadata(self, key: str, value: str):
        self.collection.delete(where={key: value})
        logger.info("Deleted documents from vector store by metadata", key=key, value=value)

vector_store = VectorStore()

def get_vector_store():
    """Returns the initialized VectorStore instance."""
    return vector_store
