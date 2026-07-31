from __future__ import annotations

from typing import Annotated, Any, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages


class AgentState(TypedDict):
    """State schema for the LangGraph RAG agent."""

    # Input
    query: str
    session_id: str
    document_ids: list[str]

    # Chat history (accumulated)
    chat_history: Annotated[list[AnyMessage], add_messages]

    # Retrieval results
    retrieved_chunks: list[dict[str, Any]]

    # Evaluation
    context_sufficient: bool
    clarification_question: Optional[str]

    # Output
    answer: str
    citations: list[dict[str, Any]]

    # Observability
    agent_steps: list[str]
    iteration: int
