# backend/tests/test_services/test_parser.py
import pytest
from app.services.ingestion.parser import parse_document

@pytest.mark.unit
class TestParser:
    """Unit tests for the document parsing service."""

    def test_parse_txt_file(self, sample_txt_file):
        """Parsing a TXT file should return a list of Documents."""
        docs = parse_document(str(sample_txt_file), "txt")
        
        assert len(docs) >= 1
        assert "Remote Work Policy" in docs[0].page_content
        assert docs[0].metadata["source"] == str(sample_txt_file)

    def test_parse_unsupported_type_raises(self, tmp_path):
        """Parsing an unsupported file type should raise ValueError."""
        fake_file = tmp_path / "data.csv"
        fake_file.write_text("col1,col2\n1,2\n")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_document(str(fake_file), "csv")

    def test_parse_nonexistent_file_raises(self):
        """Parsing a non-existent file should raise an exception."""
        with pytest.raises(Exception):
            parse_document("/nonexistent/path/file.txt", "txt")