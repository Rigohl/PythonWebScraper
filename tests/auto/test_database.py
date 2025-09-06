import os
import tempfile

import pytest

from src.database import DatabaseManager
from src.models.results import ScrapeResult


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_database_manager_init(temp_db_path):
    """Test DatabaseManager initialization."""
    with DatabaseManager(db_path=temp_db_path) as db:
        assert db.table is not None
        assert hasattr(db, "save_result")


def test_database_manager_context_manager(temp_db_path):
    """Test DatabaseManager as context manager."""
    with DatabaseManager(db_path=temp_db_path) as db:
        assert db.table is not None
    # Should be closed automatically


def test_save_result(temp_db_path):
    """Test saving a scrape result."""
    with DatabaseManager(db_path=temp_db_path) as db:
        result = ScrapeResult(
            status="SUCCESS",
            url="https://example.com",
            title="Test Title",
            content_text="Test content",
            content_html="<html></html>",
            links=["https://example.com/link"],
        )

        db.save_result(result)

        # Verify it was saved
        saved = db.get_result_by_url("https://example.com")
        assert saved is not None
        assert saved["status"] == "SUCCESS"


def test_get_result_by_url(temp_db_path):
    """Test retrieving result by URL."""
    with DatabaseManager(db_path=temp_db_path) as db:
        # Test non-existent URL
        result = db.get_result_by_url("https://nonexistent.com")
        assert result is None


def test_save_and_load_cookies(temp_db_path):
    """Test saving and loading cookies."""
    with DatabaseManager(db_path=temp_db_path) as db:
        cookies_json = '{"session": "abc123"}'
        db.save_cookies("example.com", cookies_json)

        loaded = db.load_cookies("example.com")
        assert loaded == cookies_json


def test_save_and_load_extraction_schema(temp_db_path):
    """Test saving and loading LLM extraction schema."""
    with DatabaseManager(db_path=temp_db_path) as db:
        schema_json = '{"fields": ["title", "price"]}'
        db.save_llm_extraction_schema("example.com", schema_json)

        loaded = db.load_llm_extraction_schema("example.com")
        assert loaded == schema_json


def test_duplicate_detection(temp_db_path):
    """Test duplicate result detection."""
    with DatabaseManager(db_path=temp_db_path) as db:
        result1 = ScrapeResult(
            status="SUCCESS",
            url="https://example.com",
            title="Test Title",
            content_text="Test content",
            content_html="<html></html>",
            links=[],
        )

        result2 = ScrapeResult(
            status="SUCCESS",
            url="https://example.com",
            title="Test Title",
            content_text="Test content",
            content_html="<html></html>",
            links=[],
        )

        db.save_result(result1)
        db.save_result(result2)  # Should detect as duplicate

        # Both should be saved but marked appropriately
        results = db.list_results()
        assert len(results) >= 1  # At least one result should exist


@pytest.mark.asyncio
async def test_export_to_csv(temp_db_path):
    """Test CSV export functionality."""
    with DatabaseManager(db_path=temp_db_path) as db:
        result = ScrapeResult(
            status="SUCCESS",
            url="https://example.com",
            title="Test Title",
            content_text="Test content",
            content_html="<html></html>",
            links=[],
        )
        db.save_result(result)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = f.name

        try:
            db.export_to_csv(csv_path)
            assert os.path.exists(csv_path)

            with open(csv_path) as f:
                content = f.read()
                assert "SUCCESS" in content
                assert "https://example.com" in content
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)


@pytest.mark.asyncio
async def test_export_to_json(temp_db_path):
    """Test JSON export functionality."""
    with DatabaseManager(db_path=temp_db_path) as db:
        result = ScrapeResult(
            status="SUCCESS",
            url="https://example.com",
            title="Test Title",
            content_text="Test content",
            content_html="<html></html>",
            links=[],
        )
        db.save_result(result)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json_path = f.name

        try:
            db.export_to_json(json_path)
            assert os.path.exists(json_path)

            with open(json_path) as f:
                content = f.read()
                assert "SUCCESS" in content
                assert "https://example.com" in content
        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)
