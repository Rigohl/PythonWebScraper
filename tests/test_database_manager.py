"""
Comprehensive tests for the DatabaseManager class.

This module contains tests for the DatabaseManager class to verify proper
saving, retrieval, and deduplication of scrape results as well as proper
handling of cookies and discovered APIs.
"""

import os
import json
import tempfile
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from src.database import DatabaseManager
from src.models.results import ScrapeResult


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_db.sqlite")
        yield db_path


@pytest.fixture
def db_manager(temp_db_path):
    """Create a database manager instance with a temporary database."""
    manager = DatabaseManager(db_path=temp_db_path)
    yield manager
    # Context manager ensures clean closure of connections


def test_init_with_path(temp_db_path):
    """Test initialization with a file path."""
    db = DatabaseManager(db_path=temp_db_path)
    assert db.db is not None
    assert os.path.exists(temp_db_path)


def test_init_with_existing_connection():
    """Test initialization with an existing database connection."""
    import dataset
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "test_db.sqlite")
        connection = dataset.connect(f"sqlite:///{path}")
        db = DatabaseManager(db_connection=connection)
        assert db.db is not None


def test_init_without_params():
    """Test initialization without required parameters."""
    with pytest.raises(ValueError):
        DatabaseManager()


def test_context_manager(temp_db_path):
    """Test using DatabaseManager as a context manager."""
    with DatabaseManager(db_path=temp_db_path) as db:
        assert db.db is not None
    # Connections should be closed after context exit


@pytest.mark.parametrize("url, title, content_text, status", [
    ("http://example.com/page1", "Test Page 1", "This is test content for page 1", "SUCCESS"),
    ("http://example.com/page2", "Test Page 2", "This is test content for page 2", "FAILED"),
    ("http://example.com/page3", "Test Page 3", "This is test content for page 3", "RETRY"),
])
def test_save_and_retrieve_result(db_manager, url, title, content_text, status):
    """Test saving and retrieving a ScrapeResult."""
    # Create a test result
    result = ScrapeResult(
        url=url,
        title=title,
        content_text=content_text,
        content_html=f"<html><body>{content_text}</body></html>",
        status=status,
        links=["http://example.com/link1", "http://example.com/link2"],
        visual_hash="abc123",
        content_hash="def456",
        http_status_code=200,
        crawl_duration=1.5,
        content_type="GENERAL",
        extracted_data={"field1": "value1", "field2": 42},
        healing_events=[{"type": "test", "message": "Test healing"}]
    )

    # Save the result
    db_manager.save_result(result)

    # Retrieve and verify the result
    saved = db_manager.get_result_by_url(url)
    assert saved is not None
    assert saved["url"] == url
    assert saved["title"] == title
    assert saved["content_text"] == content_text
    assert saved["status"] == status
    assert isinstance(saved["links"], list)
    assert len(saved["links"]) == 2
    assert isinstance(saved["extracted_data"], dict)
    assert saved["extracted_data"]["field1"] == "value1"
    assert saved["extracted_data"]["field2"] == 42
    assert isinstance(saved["healing_events"], list)


def test_exact_duplicate_detection(db_manager):
    """Test exact duplicate detection by content hash."""
    # Create first result
    result1 = ScrapeResult(
        url="http://example.com/original",
        title="Original Content",
        content_text="This is the original content",
        content_hash="same_hash",
        status="SUCCESS"
    )

    # Create second result with same content hash but different URL
    result2 = ScrapeResult(
        url="http://example.com/duplicate",
        title="Duplicate Content",
        content_text="This is the duplicate content",
        content_hash="same_hash",
        status="SUCCESS"
    )

    # Save both results
    db_manager.save_result(result1)
    db_manager.save_result(result2)

    # The second result should be marked as DUPLICATE
    saved2 = db_manager.get_result_by_url("http://example.com/duplicate")
    assert saved2 is not None
    assert saved2["status"] == "DUPLICATE"


def test_fuzzy_duplicate_detection(db_manager):
    """Test fuzzy duplicate detection using normalized hash."""
    # This test patch the _check_fuzzy_duplicates method to simulate a fuzzy match
    with patch.object(db_manager, '_check_fuzzy_duplicates') as mock_check:
        def side_effect(result, normalized_hash):
            if result.url == "http://example.com/fuzzy_duplicate":
                result.status = "DUPLICATE"

        mock_check.side_effect = side_effect

        # Create results
        result1 = ScrapeResult(
            url="http://example.com/original",
            title="Original Content",
            content_text="This is the original content with some words",
            status="SUCCESS"
        )

        result2 = ScrapeResult(
            url="http://example.com/fuzzy_duplicate",
            title="Similar Content",
            content_text="This is similar content with some words",
            status="SUCCESS"
        )

        # Save both results
        db_manager.save_result(result1)
        db_manager.save_result(result2)

        # Verify the second was marked as duplicate
        saved2 = db_manager.get_result_by_url("http://example.com/fuzzy_duplicate")
        assert saved2 is not None
        assert saved2["status"] == "DUPLICATE"


def test_save_and_load_cookies(db_manager):
    """Test saving and loading cookies for a domain."""
    domain = "example.com"
    cookies = [{"name": "session", "value": "abc123", "domain": domain}]
    cookies_json = json.dumps(cookies)

    # Save cookies
    db_manager.save_cookies(domain, cookies_json)

    # Load cookies
    loaded = db_manager.load_cookies(domain)

    # Verify cookies were saved and loaded correctly
    assert loaded == cookies_json
    assert json.loads(loaded) == cookies

    # Test loading for a non-existent domain
    assert db_manager.load_cookies("nonexistent.com") is None


def test_save_discovered_api(db_manager):
    """Test saving discovered API information."""
    page_url = "http://example.com/page"
    api_url = "http://api.example.com/data"
    payload_hash = "abcdef123456"

    # Save API discovery
    db_manager.save_discovered_api(page_url, api_url, payload_hash)

    # Verify API was saved (requires direct DB access)
    api_rows = list(db_manager.apis_table.find(
        page_url=page_url,
        api_url=api_url,
        payload_hash=payload_hash
    ))
    assert len(api_rows) == 1
    assert api_rows[0]["page_url"] == page_url
    assert api_rows[0]["api_url"] == api_url


def test_save_and_load_llm_extraction_schema(db_manager):
    """Test saving and loading LLM extraction schemas."""
    domain = "example.com"
    schema = {
        "properties": {
            "title": {"type": "string"},
            "price": {"type": "number"}
        },
        "required": ["title"]
    }
    schema_json = json.dumps(schema)

    # Save schema
    db_manager.save_llm_extraction_schema(domain, schema_json)

    # Load schema
    loaded = db_manager.load_llm_extraction_schema(domain)

    # Verify schema was saved and loaded correctly
    assert loaded == schema_json
    assert json.loads(loaded) == schema


def test_search_results(db_manager):
    """Test searching for results by content or title."""
    # Create and save test results
    results = [
        ScrapeResult(
            url="http://example.com/page1",
            title="Apple Products",
            content_text="Information about various Apple products including iPhone and iPad.",
            status="SUCCESS"
        ),
        ScrapeResult(
            url="http://example.com/page2",
            title="Android Phones",
            content_text="Information about Android phones and tablets.",
            status="SUCCESS"
        ),
        ScrapeResult(
            url="http://example.com/page3",
            title="Windows Laptops",
            content_text="Information about Windows laptops and tablets.",
            status="SUCCESS"
        )
    ]

    for result in results:
        db_manager.save_result(result)

    # Search for "Apple" in title or content
    found_apple = db_manager.search_results("Apple")
    assert len(found_apple) == 1
    assert found_apple[0]["url"] == "http://example.com/page1"

    # Search for "tablets" in content
    found_tablets = db_manager.search_results("tablets")
    assert len(found_tablets) == 2
    urls = [r["url"] for r in found_tablets]
    assert "http://example.com/page2" in urls
    assert "http://example.com/page3" in urls


def test_list_results(db_manager):
    """Test listing all results."""
    # Create and save test results
    results = [
        ScrapeResult(
            url=f"http://example.com/page{i}",
            title=f"Test Page {i}",
            content_text=f"Test content for page {i}",
            status="SUCCESS"
        ) for i in range(1, 4)
    ]

    for result in results:
        db_manager.save_result(result)

    # List all results
    all_results = db_manager.list_results()

    # Verify correct number of results
    assert len(all_results) == 3

    # Verify URLs are present
    urls = [r["url"] for r in all_results]
    for i in range(1, 4):
        assert f"http://example.com/page{i}" in urls


@pytest.mark.parametrize("export_func, file_ext", [
    ("export_to_csv", "csv"),
    ("export_to_json", "json"),
    ("export_to_markdown", "md")
])
def test_export_functions(db_manager, export_func, file_ext, temp_db_path):
    """Test export functions (CSV, JSON, and Markdown)."""
    # Create a directory for export files
    export_dir = os.path.dirname(temp_db_path)
    export_file = os.path.join(export_dir, f"export_test.{file_ext}")

    # Create and save successful test results
    results = [
        ScrapeResult(
            url=f"http://example.com/page{i}",
            title=f"Test Page {i}",
            content_text=f"Test content for page {i}",
            status="SUCCESS",
            content_hash=f"hash{i}",
            links=[f"http://example.com/link{j}" for j in range(1, 3)],
            extracted_data={"field1": f"value{i}", "field2": i * 10}
        ) for i in range(1, 4)
    ]

    for result in results:
        db_manager.save_result(result)

    # Call the export function
    export_method = getattr(db_manager, export_func)
    export_method(export_file)

    # Verify file exists and is not empty
    assert os.path.exists(export_file)
    assert os.path.getsize(export_file) > 0


def test_export_to_csv_with_no_success_results(db_manager, temp_db_path):
    """Test CSV export behavior when there are no SUCCESS results."""
    # Create a directory for export files
    export_dir = os.path.dirname(temp_db_path)
    export_file = os.path.join(export_dir, "empty_export.csv")

    # Create and save non-successful test results
    results = [
        ScrapeResult(
            url=f"http://example.com/page{i}",
            title=f"Test Page {i}",
            content_text=f"Test content for page {i}",
            status="FAILED"  # Not SUCCESS
        ) for i in range(1, 4)
    ]

    for result in results:
        db_manager.save_result(result)

    # Call the export function
    db_manager.export_to_csv(export_file)

    # Verify file doesn't exist (no SUCCESS results)
    assert not os.path.exists(export_file)


def test_save_scrape_result_compatibility(db_manager):
    """Test backwards compatibility with older save_scrape_result method."""
    result = ScrapeResult(
        url="http://example.com/compat",
        title="Compatibility Test",
        content_text="Testing backwards compatibility",
        status="SUCCESS"
    )

    # Use the older method name
    db_manager.save_scrape_result(result)

    # Verify result was saved correctly
    saved = db_manager.get_result_by_url("http://example.com/compat")
    assert saved is not None
    assert saved["title"] == "Compatibility Test"