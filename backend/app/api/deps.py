from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

logger = logging.getLogger(__name__)

# Re-usable DB session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_session_id(session_id: str | None = None) -> str | None:
    """Extract session_id from query params (can be extended with auth)."""
    return session_id
