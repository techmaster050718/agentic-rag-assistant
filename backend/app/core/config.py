from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator, model_validator
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

    # Database — individual vars injected by docker-compose
    POSTGRES_USER: str = Field(default="raguser")
    POSTGRES_PASSWORD: str = Field(default="ragpassword")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="ragdb")
    # Assembled DSN — can be overridden directly via DATABASE_URL env var.
    # When blank, assembled from the POSTGRES_* vars above.
    DATABASE_URL: str = Field(default="")

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        # Auto-fix: if user set plain postgresql:// without driver, add asyncpg
        elif self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self

    # Google Gemini
    GOOGLE_API_KEY: str = ""
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    LLM_MODEL: str = "gemini-3.5-flash"
    LLM_TEMPERATURE: float = 0.1

    # LangSmith (optional tracing)
    LANGCHAIN_API_KEY: str = Field(default="")
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "agentic-rag"

    # Vector store
    SUPABASE_URL: str = Field(default="")
    SUPABASE_SERVICE_KEY: str = Field(default="")

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