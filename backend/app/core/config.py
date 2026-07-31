from __future__ import annotations

from typing import Any

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "Agentic RAG Document Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=False)

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://raguser:ragpassword@localhost:5432/ragdb"
    )

    # Google Gemini
    GOOGLE_API_KEY: str = ""
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.1

    # LangSmith (optional tracing)
    LANGCHAIN_API_KEY: str = Field(default="")
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "agentic-rag"

    # Vector store
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "documents"

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Retrieval
    RETRIEVAL_TOP_K: int = 5
    HYBRID_ALPHA: float = 0.5  # 0 = BM25 only, 1 = vector only

    # Storage (GCS)
    GCS_BUCKET_NAME: str = Field(default="rag-documents")
    GCS_PROJECT_ID: str = Field(default="")
    USE_GCS: bool = False

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # File upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".txt", ".docx", ".md", ".csv"]


settings = Settings()
