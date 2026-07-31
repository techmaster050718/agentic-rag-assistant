# backend/tests/test_api/test_health.py
import pytest
from httpx import AsyncClient

@pytest.mark.api
class TestHealthEndpoint:
    """Tests for the /api/v1/health/ endpoint."""

    async def test_health_check_returns_200(self, client: AsyncClient):
        """Health endpoint should return 200 with app metadata."""
        response = await client.get("/api/v1/health/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "agentic-rag-assistant"
        assert "version" in data
        assert "env" in data

    async def test_health_check_returns_testing_env(self, client: AsyncClient):
        """Health endpoint should reflect the testing environment."""
        response = await client.get("/api/v1/health/")
        data = response.json()
        assert data["env"] == "testing"