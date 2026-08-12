# backend/tests/conftest.py
import os
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Set test environment variables BEFORE importing app modules
os.environ["APP_ENV"] = "testing"
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"

from app.main import app
from app.db.session import Base, get_db
from app.services.retrieval.vector_store import VectorStoreAdapter


# --- Database Fixtures ---

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_engine) -> AsyncSession:
    """Create a test database session."""
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db_session: AsyncSession):
    """Create an async HTTP test client with overridden DB dependency."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# --- Mock Fixtures ---

@pytest.fixture
def mock_embeddings():
    """Mock the OpenAI embeddings service."""
    with patch("app.services.ingestion.embedder.get_embeddings") as mock:
        embedder = AsyncMock()
        embedder.aembed_documents = AsyncMock(
            return_value=[[0.1] * 1536, [0.2] * 1536]
        )
        embedder.aembed_query = AsyncMock(
            return_value=[0.15] * 1536
        )
        mock.return_value = embedder
        yield embedder


@pytest.fixture
def mock_vector_store():
    """Mock the Supabase vector store."""
    with patch("app.services.retrieval.vector_store.vector_store") as mock:
        mock.add_documents = AsyncMock()
        mock.search = AsyncMock(return_value=[
            {
                "id": "chunk-1",
                "content": "Employees may work remotely up to 3 days per week.",
                "metadata": {"source": "remote_policy.pdf", "document_id": "doc-1"},
                "score": 0.92,
            },
            {
                "id": "chunk-2",
                "content": "Remote work requires manager approval and a dedicated workspace.",
                "metadata": {"source": "remote_policy.pdf", "document_id": "doc-1"},
                "score": 0.85,
            },
        ])
        mock.delete_by_metadata = AsyncMock()
        yield mock


@pytest.fixture
def mock_llm():
    """Mock the OpenAI LLM used in agent nodes."""
    with patch("app.services.agent.nodes.llm") as mock:
        mock_response = MagicMock()
        mock_response.content = '{"sufficient": true}'
        mock.ainvoke = AsyncMock(return_value=mock_response)
        
        # Support chaining with prompt templates (prompt | llm)
        mock_chain = AsyncMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock.__or__ = MagicMock(return_value=mock_chain)
        
        yield mock


@pytest.fixture
def sample_pdf_file(tmp_path):
    """Create a minimal test PDF file."""
    file_path = tmp_path / "test_policy.pdf"
    # Minimal valid PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Test Policy Document) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000360 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
441
%%EOF"""
    file_path.write_bytes(pdf_content)
    return file_path


@pytest.fixture
def sample_txt_file(tmp_path):
    """Create a test TXT file."""
    file_path = tmp_path / "test_policy.txt"
    file_path.write_text(
        "Company Remote Work Policy\n\n"
        "1. Employees are eligible for remote work after 90 days of employment.\n"
        "2. Remote work is permitted up to 3 days per week.\n"
        "3. Employees must maintain a dedicated, quiet workspace.\n"
        "4. All remote work arrangements require written manager approval.\n"
        "5. Company equipment must be used for all work-related tasks.\n",
        encoding="utf-8"
    )
    return file_path