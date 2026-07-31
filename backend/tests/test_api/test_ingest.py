# backend/tests/test_api/test_ingest.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.api
class TestIngestEndpoint:
    """Tests for the /api/v1/ingest/ endpoint."""

    async def test_ingest_txt_file_returns_202(self, client: AsyncClient, sample_txt_file):
        """Uploading a valid TXT file should return 202 Accepted."""
        with open(sample_txt_file, "rb") as f:
            response = await client.post(
                "/api/v1/ingest/",
                files={"file": ("test_policy.txt", f, "text/plain")},
            )
        
        assert response.status_code == 202
        data = response.json()
        assert data["title"] == "test_policy.txt"
        assert data["file_type"] == "txt"
        assert data["status"] == "processing"
        assert "id" in data

    async def test_ingest_rejects_unsupported_file_type(self, client: AsyncClient, tmp_path):
        """Uploading an unsupported file type should return 400."""
        bad_file = tmp_path / "image.png"
        bad_file.write_bytes(b"\x89PNG\r\n\x1a\n")
        
        with open(bad_file, "rb") as f:
            response = await client.post(
                "/api/v1/ingest/",
                files={"file": ("image.png", f, "image/png")},
            )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    async def test_ingest_rejects_missing_file(self, client: AsyncClient):
        """Request without a file should return 422 Unprocessable Entity."""
        response = await client.post("/api/v1/ingest/")
        assert response.status_code == 422

    @patch("app.api.v1.endpoints.ingest.process_document", new_callable=AsyncMock)
    async def test_ingest_creates_db_record(
        self, mock_process, client: AsyncClient, sample_txt_file
    ):
        """Ingestion should create a document record in the database."""
        with open(sample_txt_file, "rb") as f:
            response = await client.post(
                "/api/v1/ingest/",
                files={"file": ("test_policy.txt", f, "text/plain")},
            )
        
        assert response.status_code == 202
        data = response.json()
        
        # Verify the document appears in the list
        list_response = await client.get("/api/v1/documents/")
        assert list_response.status_code == 200
        docs = list_response.json()
        assert len(docs) >= 1
        assert any(d["id"] == data["id"] for d in docs)