# backend/tests/test_api/test_chat.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import uuid

@pytest.mark.api
class TestChatEndpoint:
    """Tests for the /api/v1/chat/ endpoints."""

    async def test_list_sessions_empty(self, client: AsyncClient):
        """Listing sessions when none exist should return an empty list."""
        response = await client.get("/api/v1/chat/sessions")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.api.v1.endpoints.chat.agent_graph")
    async def test_query_creates_session_and_returns_answer(
        self, mock_graph, client: AsyncClient
    ):
        """A query without session_id should create a new session and return an answer."""
        # Mock the agent graph response
        mock_graph.ainvoke = AsyncMock(return_value={
            "final_answer": "Employees may work remotely up to 3 days per week [1].",
            "citations": [
                {
                    "index": 1,
                    "source": "remote_policy.pdf",
                    "content_snippet": "Employees may work remotely up to 3 days..."
                }
            ],
            "messages": [],
            "needs_clarification": False,
        })
        
        response = await client.post(
            "/api/v1/chat/query",
            json={"query": "What is the remote work policy?"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "Employees may work remotely" in data["answer"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["source"] == "remote_policy.pdf"

    @patch("app.api.v1.endpoints.chat.agent_graph")
    async def test_query_with_existing_session(
        self, mock_graph, client: AsyncClient
    ):
        """A query with an existing session_id should reuse the session."""
        mock_graph.ainvoke = AsyncMock(return_value={
            "final_answer": "Yes, manager approval is required.",
            "citations": [],
            "messages": [],
            "needs_clarification": False,
        })
        
        # Create first query (creates session)
        first_resp = await client.post(
            "/api/v1/chat/query",
            json={"query": "What is the remote work policy?"},
        )
        session_id = first_resp.json()["session_id"]
        
        # Second query with same session
        second_resp = await client.post(
            "/api/v1/chat/query",
            json={
                "session_id": session_id,
                "query": "Do I need manager approval?",
            },
        )
        
        assert second_resp.status_code == 200
        assert second_resp.json()["session_id"] == session_id

    async def test_query_with_invalid_session_returns_404(self, client: AsyncClient):
        """A query with a non-existent session_id should return 404."""
        fake_id = str(uuid.uuid4())
        response = await client.post(
            "/api/v1/chat/query",
            json={
                "session_id": fake_id,
                "query": "What is the policy?",
            },
        )
        assert response.status_code == 404

    async def test_get_session_details(self, client: AsyncClient):
        """Retrieving a session should include its message history."""
        with patch("app.api.v1.endpoints.chat.agent_graph") as mock_graph:
            mock_graph.ainvoke = AsyncMock(return_value={
                "final_answer": "Test answer.",
                "citations": [],
                "messages": [],
                "needs_clarification": False,
            })
            
            # Create a session via query
            resp = await client.post(
                "/api/v1/chat/query",
                json={"query": "Test question?"},
            )
            session_id = resp.json()["session_id"]
        
        # Get session details
        detail_resp = await client.get(f"/api/v1/chat/sessions/{session_id}")
        assert detail_resp.status_code == 200
        data = detail_resp.json()
        assert data["id"] == session_id
        assert len(data["messages"]) == 2  # user + assistant
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"