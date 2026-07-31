from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", summary="API health check")
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "agentic-rag-backend"})
