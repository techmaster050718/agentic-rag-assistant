# backend/tests/test_agent/test_nodes.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from app.services.agent.nodes import (
    conversation_memory_node,
    retrieve_node,
    compare_documents_node,
    clarify_node,
    summarize_node,
    route_after_compare,
)

@pytest.mark.unit
class TestAgentNodes:
    """Unit tests for individual LangGraph agent nodes."""

    async def test_conversation_memory_extracts_query(self):
        """The memory node should extract the latest human message as the query."""
        state = {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there!"),
                HumanMessage(content="What is the remote work policy?"),
            ],
            "query": "",
            "retrieved_context": [],
            "needs_clarification": False,
            "final_answer": "",
            "citations": [],
        }
        
        result = await conversation_memory_node(state)
        assert result["query"] == "What is the remote work policy?"

    async def test_conversation_memory_empty_messages(self):
        """The memory node should handle empty message history gracefully."""
        state = {
            "messages": [],
            "query": "",
            "retrieved_context": [],
            "needs_clarification": False,
            "final_answer": "",
            "citations": [],
        }
        
        result = await conversation_memory_node(state)
        assert result["query"] == ""

    @patch("app.services.agent.nodes.retriever")
    async def test_retrieve_node_returns_context(self, mock_retriever):
        """The retrieve node should return document chunks from the retriever."""
        mock_retriever.retrieve = AsyncMock(return_value=[
            {"id": "c1", "content": "Remote work policy text", "metadata": {}, "score": 0.9}
        ])
        
        state = {
            "messages": [],
            "query": "remote work",
            "retrieved_context": [],
            "needs_clarification": False,
            "final_answer": "",
            "citations": [],
        }
        
        result = await retrieve_node(state)
        assert len(result["retrieved_context"]) == 1
        assert result["retrieved_context"][0]["content"] == "Remote work policy text"

    @patch("app.services.agent.nodes.retriever")
    async def test_retrieve_node_handles_failure(self, mock_retriever):
        """The retrieve node should return empty context on failure."""
        mock_retriever.retrieve = AsyncMock(side_effect=Exception("Connection error"))
        
        state = {
            "messages": [],
            "query": "test",
            "retrieved_context": [],
            "needs_clarification": False,
            "final_answer": "",
            "citations": [],
        }
        
        result = await retrieve_node(state)
        assert result["retrieved_context"] == []

    def test_route_after_compare_sufficient(self):
        """Router should direct to 'summarize' when context is sufficient."""
        state = {"needs_clarification": False}
        assert route_after_compare(state) == "summarize"

    def test_route_after_compare_insufficient(self):
        """Router should direct to 'clarify' when context is insufficient."""
        state = {"needs_clarification": True}
        assert route_after_compare(state) == "clarify"

    @patch("app.services.agent.nodes.llm")
    async def test_summarize_node_generates_answer(self, mock_llm):
        """The summarize node should generate a grounded answer with citations."""
        mock_response = MagicMock()
        mock_response.content = "Employees can work remotely 3 days per week [1]."
        
        mock_chain = AsyncMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm.__or__ = MagicMock(return_value=mock_chain)
        
        state = {
            "messages": [HumanMessage(content="What is the remote policy?")],
            "query": "What is the remote policy?",
            "retrieved_context": [
                {
                    "id": "c1",
                    "content": "Employees may work remotely up to 3 days per week.",
                    "metadata": {"source": "policy.pdf"},
                    "score": 0.95,
                }
            ],
            "needs_clarification": False,
            "final_answer": "",
            "citations": [],
        }
        
        result = await summarize_node(state)
        assert "remotely" in result["final_answer"].lower()
        assert len(result["citations"]) == 1
        assert result["citations"][0]["source"] == "policy.pdf"
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)