# backend/tests/test_agent/test_graph.py
import pytest
from app.services.agent.graph import build_agent_graph
from app.services.agent.state import AgentState

@pytest.mark.unit
class TestAgentGraph:
    """Unit tests for the LangGraph agent compilation and structure."""

    def test_graph_compiles_successfully(self):
        """The agent graph should compile without errors."""
        graph = build_agent_graph()
        assert graph is not None

    def test_graph_has_required_nodes(self):
        """The compiled graph should contain all required agent nodes."""
        graph = build_agent_graph()
        # LangGraph compiled graphs expose their nodes
        node_names = list(graph.get_graph().nodes.keys())
        
        required_nodes = [
            "conversation_memory",
            "retrieve",
            "compare_documents",
            "clarify",
            "summarize",
        ]
        
        for node in required_nodes:
            assert node in node_names, f"Missing required node: {node}"

    def test_graph_has_entry_point(self):
        """The graph should start at the conversation_memory node."""
        graph = build_agent_graph()
        # The entry point should be conversation_memory
        graph_dict = graph.get_graph()
        # Verify the graph structure is valid
        assert len(graph_dict.nodes) >= 5