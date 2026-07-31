from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.core.rate_limiter import limiter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent.graph import build_agent_graph
from app.services.agent.streaming import stream_agent_events

logger = logging.getLogger(__name__)
router = APIRouter()

_agent_graph = None


def get_agent_graph():
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_agent_graph()
    return _agent_graph


@router.post(
    "/query",
    response_model=ChatResponse,
    summary="Send a query and get a grounded answer",
)
@limiter.limit("30/minute")
async def query(
    request: Request,  # ← critical fix #4a: Request must be first for SlowAPI
    body: ChatRequest,
) -> ChatResponse:
    """Non-streaming chat endpoint: runs the full LangGraph agent and returns the final answer."""
    try:
        graph = get_agent_graph()
        result = await graph.ainvoke(
            {
                "query": body.query,
                "session_id": body.session_id or str(uuid.uuid4()),
                "chat_history": body.chat_history or [],
                "documents": body.document_ids or [],
            }
        )
        return ChatResponse(
            answer=result.get("answer", ""),
            citations=result.get("citations", []),
            session_id=result.get("session_id", ""),
            agent_steps=result.get("agent_steps", []),
        )
    except Exception as exc:
        logger.exception(f"Chat query failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.post(
    "/stream",
    summary="Stream a query response via SSE",
)
@limiter.limit("30/minute")
async def stream_query(
    request: Request,  # ← critical fix #4b: Request must be first for SlowAPI
    body: ChatRequest,
) -> StreamingResponse:
    """Streaming chat endpoint: returns Server-Sent Events (SSE) tokens in real-time."""

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            graph = get_agent_graph()
            session_id = body.session_id or str(uuid.uuid4())
            async for event in stream_agent_events(
                graph=graph,
                query=body.query,
                session_id=session_id,
                chat_history=body.chat_history or [],
                document_ids=body.document_ids or [],
            ):
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0)  # yield control to event loop
            yield "data: [DONE]\n\n"
        except Exception as exc:
            logger.exception(f"Streaming error: {exc}")
            error_payload = json.dumps({"error": str(exc)})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
