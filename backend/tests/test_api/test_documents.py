# backend/tests/test_api/test_documents.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.api
class TestDocumentsEndpoint:
    """Tests for the /api/v1/documents/ endpoints."""

    async def test_list_documents_empty(self, client: AsyncClient):
        """Listing documents when none exist should return an empty list."""
        response = await client.get("/api/v1/documents/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_documents_after_ingest(self, client: AsyncClient, sample_txt_file):
        """Listing documents after ingestion should return the uploaded document."""
        with open(sample_txt_file, "rb") as f:
            await client.post(
                "/api/v1/ingest/",
                files={"file": ("test_policy.txt", f, "text/plain")},
            )
        
        response = await client.get("/api/v1/documents/")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) == 1
        assert docs[0]["title"] == "test_policy.txt"

    @patch("app.services.retrieval.vector_store.vector_store")
    async def test_delete_document_returns_204(
        self, mock_vs, client: AsyncClient, sample_txt_file
    ):
        """Deleting an existing document should return 204 No Content."""
        mock_vs.delete_by_metadata = AsyncMock()
        
        # First, ingest a document
        with open(sample_txt_file, "rb") as f:
            ingest_resp = await client.post(
                "/api/v1/ingest/",
                files={"file": ("test_policy.txt", f, "text/plain")},
            )
        doc_id = ingest_resp.json()["id"]
        
        # Delete it
        response = await client.delete(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        list_resp = await client.get("/api/v1/documents/")
        assert len(list_resp.json()) == 0

    async def test_delete_nonexistent_document_returns_404(self, client: AsyncClient):
        """Deleting a non-existent document should return 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.delete(f"/api/v1/documents/{fake_id}")
        assert response.status_code == 404