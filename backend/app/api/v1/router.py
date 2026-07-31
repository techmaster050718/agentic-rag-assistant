from fastapi import APIRouter

from app.api.v1.endpoints import health, ingest, chat, documents, aliases

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Document ingestion
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])

# Chat / Agent
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Document management
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Convenience aliases (no duplicate routes)
api_router.include_router(aliases.router, tags=["aliases"])
