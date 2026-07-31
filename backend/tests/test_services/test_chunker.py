# backend/tests/test_services/test_chunker.py
import pytest
from langchain_core.documents import Document
from app.services.ingestion.chunker import chunk_documents

@pytest.mark.unit
class TestChunker:
    """Unit tests for the document chunking service."""

    def test_chunk_short_document(self):
        """A document shorter than chunk_size should produce a single chunk."""
        docs = [Document(page_content="Short text.", metadata={"source": "test.txt"})]
        chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=200)
        
        assert len(chunks) == 1
        assert chunks[0].page_content == "Short text."

    def test_chunk_long_document(self):
        """A long document should be split into multiple overlapping chunks."""
        long_text = " ".join([f"Sentence number {i}." for i in range(200)])
        docs = [Document(page_content=long_text, metadata={"source": "test.txt"})]
        chunks = chunk_documents(docs, chunk_size=200, chunk_overlap=50)
        
        assert len(chunks) > 1
        # Verify overlap: consecutive chunks should share some content
        for i in range(len(chunks) - 1):
            current_words = set(chunks[i].page_content.split())
            next_words = set(chunks[i + 1].page_content.split())
            overlap = current_words & next_words
            assert len(overlap) > 0, "Chunks should have overlapping content"

    def test_chunk_preserves_metadata(self):
        """Chunking should preserve the original document metadata."""
        docs = [Document(
            page_content="Some content here.",
            metadata={"source": "policy.pdf", "page": 1}
        )]
        chunks = chunk_documents(docs)
        
        for chunk in chunks:
            assert chunk.metadata["source"] == "policy.pdf"
            assert chunk.metadata["page"] == 1

    def test_chunk_empty_document(self):
        """An empty document should produce zero chunks."""
        docs = [Document(page_content="", metadata={})]
        chunks = chunk_documents(docs)
        assert len(chunks) == 0

    def test_chunk_multiple_documents(self):
        """Multiple documents should all be chunked and combined."""
        docs = [
            Document(page_content="First document content.", metadata={"source": "a.txt"}),
            Document(page_content="Second document content.", metadata={"source": "b.txt"}),
        ]
        chunks = chunk_documents(docs, chunk_size=1000)
        assert len(chunks) == 2