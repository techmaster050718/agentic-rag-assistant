# backend/tests/test_api/test_streaming.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import json

@pytest.mark.api
class TestStreamingEndpoint:
    """Tests for the /api/v1/chat/query/stream endpoint."""

    @patch("app.api.v1.endpoints.chat.agent_graph")
    async def test_stream_returns_sse_format(self, mock_graph, client: AsyncClient):
        """Streaming endpoint should return proper SSE format."""
        # Mock astream_events to yield test events
        async def mock_events(*args, **kwargs):
            yield {
                "event": "on_chain_start",
                "metadata": {"langgraph_node": "retrieve"},
                "data": {},
            }
            yield {
                "event": "on_chat_model_stream",
                "metadata": {"langgraph_node": "summarize"},
                "data": {"chunk": MagicMock(content="Hello ")},
            }
            yield {
                "event": "on_chat_model_stream",
                "metadata": {"langgraph_node": "summarize"},
                "data": {"chunk": MagicMock(content="world")},
            }
            yield {
                "event": "on_chain_end",
                "metadata": {"langgraph_node": "summarize"},
                "data": {"output": {"citations": []}},
            }

        mock_graph.astream_events = mock_events

        response = await client.post(
            "/api/v1/chat/query/stream",
            json={"query": "Test question?"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        # Parse SSE events
        content = response.text
        events = [line for line in content.split("\n") if line.startswith("data: ")]
        assert len(events) >= 3

        # Verify first event is a state update
        first_event = json.loads(events[0].replace("data: ", ""))
        assert first_event["type"] == "state"
        assert first_event["state"] == "retrieve"

    @patch("app.api.v1.endpoints.chat.agent_graph")
    async def test_stream_creates_session_if_missing(self, mock_graph, client: AsyncClient):
        """Streaming should create a session if none is provided."""
        async def mock_events(*args, **kwargs):
            yield {
                "event": "on_chat_model_stream",
                "metadata": {"langgraph_node": "summarize"},
                "data": {"chunk": MagicMock(content="Test")},
            }
            yield {
                "event": "on_chain_end",
                "metadata": {"langgraph_node": "summarize"},
                "data": {"output": {"citations": []}},
            }

        mock_graph.astream_events = mock_events

        response = await client.post(
            "/api/v1/chat/query/stream",
            json={"query": "Hello?"},
        )

        assert response.status_code == 200

        # Verify session was created in DB
        sessions_resp = await client.get("/api/v1/chat/sessions")
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()
        assert len(sessions) >= 1