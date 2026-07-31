from __future__ import annotations

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.services.agent.state import AgentState
from app.services.retrieval import vector_store  # ← critical fix #6: import vector_store

logger = logging.getLogger(__name__)

# Shared LLM and embedding instances
_llm = ChatGoogleGenerativeAI(
    model=settings.LLM_MODEL, 
    temperature=settings.LLM_TEMPERATURE, 
    google_api_key=settings.GOOGLE_API_KEY, 
    convert_system_message_to_human=True,
    streaming=True
)


async def memory_node(state: AgentState) -> dict[str, Any]:
    """Load relevant chat history from memory."""
    logger.debug(f"[memory_node] session={state['session_id']}")
    steps = state.get("agent_steps", [])
    steps.append("memory: loaded chat history")
    return {
        "agent_steps": steps,
        "iteration": state.get("iteration", 0) + 1,
    }


async def retrieve_node(state: AgentState) -> dict[str, Any]:
    """Embed the query and retrieve relevant chunks from the vector store."""
    logger.debug(f"[retrieve_node] query={state['query'][:80]}")

    steps = state.get("agent_steps", [])
    steps.append("retrieve: embedding query and searching vector store")

    try:
        store = vector_store.get_vector_store()
        results = await store.asimilarity_search_with_relevance_scores(
            query=state["query"],
            k=settings.RETRIEVAL_TOP_K,
        )
        chunks = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
            for doc, score in results
        ]
    except Exception as exc:
        logger.warning(f"[retrieve_node] Vector store error: {exc}. Using empty context.")
        chunks = []

    steps.append(f"retrieve: found {len(chunks)} chunks")
    return {"retrieved_chunks": chunks, "agent_steps": steps}


async def compare_node(state: AgentState) -> dict[str, Any]:
    """Evaluate whether retrieved context is sufficient to answer the query."""
    logger.debug("[compare_node] evaluating context sufficiency")

    steps = state.get("agent_steps", [])
    chunks = state.get("retrieved_chunks", [])

    if not chunks:
        steps.append("compare: no context found — will clarify")
        return {
            "context_sufficient": False,
            "clarification_question": "Could you provide more details or upload a relevant document?",
            "agent_steps": steps,
        }

    # Build context for LLM evaluation
    context = "\n\n".join(c["content"][:500] for c in chunks[:3])
    prompt = f"""Evaluate if the following context is sufficient to answer the query.
Query: {state['query']}
Context:
{context}

Respond with exactly one word: SUFFICIENT or INSUFFICIENT."""

    response = await _llm.ainvoke(prompt)
    verdict = response.content.strip().upper()
    is_sufficient = "SUFFICIENT" in verdict

    steps.append(f"compare: context is {'sufficient' if is_sufficient else 'insufficient'}")
    return {
        "context_sufficient": is_sufficient,
        "agent_steps": steps,
    }


async def summarize_node(state: AgentState) -> dict[str, Any]:
    """Generate a grounded answer with inline citations."""
    logger.debug("[summarize_node] generating answer")

    steps = state.get("agent_steps", [])
    chunks = state.get("retrieved_chunks", [])

    # Build numbered context
    context_parts = []
    citations = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[{i}] {chunk['content']}")
        citations.append(
            {
                "id": i,
                "source": chunk["metadata"].get("source", "unknown"),
                "page": chunk["metadata"].get("page", None),
                "text": chunk["content"][:200],
                "score": chunk.get("score", 0.0),
            }
        )

    context = "\n\n".join(context_parts)
    prompt = f"""You are an expert document analyst. Answer the query using ONLY the provided context.
Use inline citations in the format [1], [2] etc. Be concise and accurate.

Query: {state['query']}

Context:
{context}

Answer:"""

    response = await _llm.ainvoke(prompt)
    answer = response.content.strip()
    steps.append("summarize: generated grounded answer with citations")

    return {
        "answer": answer,
        "citations": citations,
        "agent_steps": steps,
    }


async def clarify_node(state: AgentState) -> dict[str, Any]:
    """Generate a clarifying question when context is insufficient."""
    logger.debug("[clarify_node] generating clarification question")

    steps = state.get("agent_steps", [])
    clarification = state.get(
        "clarification_question",
        "I don't have enough context to answer your question. Could you upload a relevant document or rephrase your query?",
    )

    if not clarification:
        prompt = f"""The user asked: {state['query']}
No relevant documents were found. Generate a helpful clarifying question to guide the user."""
        response = await _llm.ainvoke(prompt)
        clarification = response.content.strip()

    steps.append("clarify: generated clarification question")
    return {
        "answer": clarification,
        "citations": [],
        "agent_steps": steps,
    }
