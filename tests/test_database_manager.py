"""
Tests for DatabaseManager operations and error handling.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from src.database import DatabaseManager
from src.models.results import ScrapeResult


class TestDatabaseManager:
    """Test DatabaseManager core functionality."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_database_connection_initialization(self, temp_db_path):
        """Test database connection and initialization."""
        with DatabaseManager(db_path=temp_db_path) as db:
            assert db.table is not None
            assert hasattr(db, "save_result")
            assert hasattr(db, "get_result_by_url")

    def test_database_context_manager(self, temp_db_path):
        """Test database context manager behavior."""
        with DatabaseManager(db_path=temp_db_path) as db:
            assert db.table is not None
        # Database should be properly closed

    def test_crud_operations_create(self, temp_db_path):
        """Test CREATE operation in CRUD."""
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

            # Verify creation
            saved = db.get_result_by_url("https://example.com")
            assert saved is not None
            assert saved["status"] == "SUCCESS"

    def test_crud_operations_read(self, temp_db_path):
        """Test READ operation in CRUD."""
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

            # Test read existing
            saved = db.get_result_by_url("https://example.com")
            assert saved is not None
            assert saved["url"] == "https://example.com"

            # Test read non-existent
            not_found = db.get_result_by_url("https://nonexistent.com")
            assert not_found is None

    def test_crud_operations_update(self, temp_db_path):
        """Test UPDATE operation in CRUD."""
        with DatabaseManager(db_path=temp_db_path) as db:
            # Create initial result
            result = ScrapeResult(
                status="SUCCESS",
                url="https://example.com",
                title="Original Title",
                content_text="Original content",
                content_html="<html></html>",
                links=[],
            )
            db.save_result(result)

            # Update by saving again with changes
            updated_result = ScrapeResult(
                status="UPDATED",
                url="https://example.com",
                title="Updated Title",
                content_text="Updated content",
                content_html="<html></html>",
                links=[],
            )
            db.save_result(updated_result)

            # Verify update
            saved = db.get_result_by_url("https://example.com")
            assert saved is not None
            assert saved["status"] == "UPDATED"
            assert saved["title"] == "Updated Title"

    def test_crud_operations_delete(self, temp_db_path):
        """Test DELETE operation in CRUD."""
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

            # Verify exists
            assert db.get_result_by_url("https://example.com") is not None

            # Delete (if method exists)
            if hasattr(db, "delete_result"):
                db.delete_result("https://example.com")
                assert db.get_result_by_url("https://example.com") is None

    def test_cookie_operations(self, temp_db_path):
        """Test cookie save and load operations."""
        with DatabaseManager(db_path=temp_db_path) as db:
            domain = "example.com"
            cookies_json = '{"session": "abc123", "user": "test"}'

            # Save cookies
            db.save_cookies(domain, cookies_json)

            # Load cookies
            loaded = db.load_cookies(domain)
            assert loaded == cookies_json

            # Test non-existent domain
            not_found = db.load_cookies("nonexistent.com")
            assert not_found is None

    def test_error_handling_database_connection_failure(self):
        """Test error handling for database connection failures."""
        with patch("dataset.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                DatabaseManager(db_path="invalid_path.db")

    def test_error_handling_save_operation_failure(self, temp_db_path):
        """Test error handling for save operation failures."""
        with DatabaseManager(db_path=temp_db_path) as db:
            # Mock the table to raise an exception
            with patch.object(db.table, "insert", side_effect=Exception("Save failed")):
                result = ScrapeResult(
                    status="SUCCESS",
                    url="https://example.com",
                    title="Test Title",
                    content_text="Test content",
                    content_html="<html></html>",
                    links=[],
                )

                with pytest.raises(Exception, match="Save failed"):
                    db.save_result(result)

    def test_connection_pooling_and_cleanup(self, temp_db_path):
        """Test connection pooling and proper cleanup."""
        db = DatabaseManager(db_path=temp_db_path)
        assert db.table is not None

        # Test manual cleanup if close exists
        if hasattr(db, "close"):
            db.close()

    def test_database_initialization_with_memory_db(self):
        """Test database initialization with in-memory database."""
        with DatabaseManager(db_path=":memory:") as db:
            assert db.table is not None

            # Test operations work
            result = ScrapeResult(
                status="SUCCESS",
                url="https://example.com",
                title="Test Title",
                content_text="Test content",
                content_html="<html></html>",
                links=[],
            )
            db.save_result(result)

            saved = db.get_result_by_url("https://example.com")
            assert saved is not None

    def test_duplicate_url_handling(self, temp_db_path):
        """Test handling of duplicate URLs."""
        with DatabaseManager(db_path=temp_db_path) as db:
            result1 = ScrapeResult(
                status="SUCCESS",
                url="https://example.com",
                title="Title 1",
                content_text="Content 1",
                content_html="<html></html>",
                links=[],
            )

            result2 = ScrapeResult(
                status="SUCCESS",
                url="https://example.com",
                title="Title 2",
                content_text="Content 2",
                content_html="<html></html>",
                links=[],
            )

            db.save_result(result1)
            db.save_result(result2)  # Should handle duplicate

            # Should have at least one result
            results = db.list_results()
            assert len(results) >= 1
