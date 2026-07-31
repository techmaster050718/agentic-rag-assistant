from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.services.agent.nodes import (
    clarify_node,
    compare_node,
    memory_node,
    retrieve_node,
    summarize_node,
)
from app.services.agent.state import AgentState

logger = logging.getLogger(__name__)


def _route_after_compare(state: AgentState) -> Literal["summarize", "clarify"]:
    """Conditional edge: route to summarize if context is sufficient, else clarify."""
    if state.get("context_sufficient", False):
        return "summarize"
    return "clarify"


def build_agent_graph() -> StateGraph:
    """Construct and compile the LangGraph agent state machine."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("memory", memory_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("compare", compare_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("clarify", clarify_node)

    # Define edges
    workflow.add_edge(START, "memory")
    workflow.add_edge("memory", "retrieve")
    workflow.add_edge("retrieve", "compare")

    # Conditional routing after compare
    workflow.add_conditional_edges(
        "compare",
        _route_after_compare,
        {
            "summarize": "summarize",
            "clarify": "clarify",
        },
    )

    workflow.add_edge("summarize", END)
    workflow.add_edge("clarify", END)

    compiled = workflow.compile()
    logger.info("LangGraph agent graph compiled successfully.")
    return compiled
