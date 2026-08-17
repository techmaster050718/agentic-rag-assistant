from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.rate_limiter import limiter
from app.db.session import engine, Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    setup_logging()
    logger.info("Starting Agentic RAG Document Assistant API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created.")

    yield

    logger.info("Shutting down API...")
    await engine.dispose()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="Agentic RAG Document Assistant — multi-step LangGraph agent with inline citations.",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # Rate limiter state
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

        # CORS - FINAL FIXED VERSION
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # <-- YEH FALSE HONA ZAROORI HAI JAB "*" USE KAR RAHE HO
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Compression
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    # Request timing middleware
    @application.middleware("http")
    async def add_process_time_header(request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response

    # Include routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    @application.get("/", include_in_schema=False)
    async def root() -> JSONResponse:
        return JSONResponse({"message": "Agentic RAG Document Assistant API", "version": settings.VERSION})

    return application


app = create_application()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)