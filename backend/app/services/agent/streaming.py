from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from langgraph.graph import StateGraph

from app.services.agent.state import AgentState

logger = logging.getLogger(__name__)


async def stream_agent_events(
    graph: StateGraph,
    query: str,
    session_id: str,
    chat_history: list,
    document_ids: list[str],
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Stream LangGraph agent events as SSE-compatible dicts.
    Yields token deltas, step transitions, and the final answer.
    """
    initial_state: AgentState = {
        "query": query,
        "session_id": session_id,
        "document_ids": document_ids,
        "chat_history": chat_history,
        "retrieved_chunks": [],
        "context_sufficient": False,
        "clarification_question": None,
        "answer": "",
        "citations": [],
        "agent_steps": [],
        "iteration": 0,
    }

    async for event in graph.astream_events(initial_state, version="v2"):
        event_type = event.get("event", "")
        data = event.get("data", {})
        node_name = event.get("name", "")

        if event_type == "on_chat_model_stream":
            chunk = data.get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                yield {"type": "token", "content": chunk.content}

        elif event_type == "on_chain_start":
            if node_name in ("memory", "retrieve", "compare", "summarize", "clarify"):
                yield {"type": "step_start", "node": node_name}

        elif event_type == "on_chain_end":
            if node_name in ("memory", "retrieve", "compare", "summarize", "clarify"):
                output = data.get("output", {})
                steps = output.get("agent_steps", [])
                yield {"type": "step_end", "node": node_name, "steps": steps}

        elif event_type == "on_chain_end" and node_name == "LangGraph":
            # Final state
            output = data.get("output", {})
            yield {
                "type": "final",
                "answer": output.get("answer", ""),
                "citations": output.get("citations", []),
                "agent_steps": output.get("agent_steps", []),
                "session_id": session_id,
            }
