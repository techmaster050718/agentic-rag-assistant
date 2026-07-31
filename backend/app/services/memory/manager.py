from __future__ import annotations

import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)

_MAX_HISTORY = 20  # max messages per session


class MemoryManager:
    """In-process session memory store (swap for Redis in production)."""

    def __init__(self) -> None:
        self._store: dict[str, deque[dict[str, Any]]] = {}

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._store.get(session_id, []))

    def add_turn(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        if session_id not in self._store:
            self._store[session_id] = deque(maxlen=_MAX_HISTORY)
        self._store[session_id].append({"role": role, "content": content})

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


# Singleton
memory_manager = MemoryManager()
