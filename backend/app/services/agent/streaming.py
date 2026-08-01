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

    final_state: dict[str, Any] = {}

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
            # ── BUG FIX: the LangGraph terminal event MUST be checked first,
            # because both conditions share the same event_type. The previous code
            # had an unreachable `elif` that silently swallowed the final answer.
            if node_name == "LangGraph":
                output = data.get("output", {})
                final_state = output  # capture for fallback below
                yield {
                    "type": "final",
                    "answer": output.get("answer", ""),
                    "citations": output.get("citations", []),
                    "agent_steps": output.get("agent_steps", []),
                    "session_id": session_id,
                }
            elif node_name in ("memory", "retrieve", "compare", "summarize", "clarify"):
                output = data.get("output", {})
                steps = output.get("agent_steps", [])
                yield {"type": "step_end", "node": node_name, "steps": steps}

    # Safety-net: if no LangGraph on_chain_end was caught (version skew / edge case),
    # emit whatever the final_state had so the frontend always gets an answer.
    if not final_state and query:
        logger.warning("[stream_agent_events] No LangGraph terminal event received — emitting empty final.")
        yield {
            "type": "final",
            "answer": "",
            "citations": [],
            "agent_steps": [],
            "session_id": session_id,
        }
