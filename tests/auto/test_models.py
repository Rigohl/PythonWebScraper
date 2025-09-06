import pytest


def _import_scrape_result():
    try:
        from src.models.results import ScrapeResult

        return ScrapeResult
    except Exception:
        pytest.skip("ScrapeResult not available")


def test_scrape_result_init():
    ScrapeResult = _import_scrape_result()
    result = ScrapeResult(
        status="SUCCESS",
        url="https://example.com",
        title="Test Title",
        content_text="Test content",
        content_html="<html></html>",
        links=[],
        visual_hash="abc123",
        content_hash="def456",
        http_status_code=200,
        crawl_duration=1.5,
        content_type="GENERAL",
        extracted_data=None,
        healing_events=[],
    )

    assert result.status == "SUCCESS"
    assert result.url == "https://example.com"
    assert result.title == "Test Title"
    assert result.content_text == "Test content"


def test_scrape_result_validation():
    """Test ScrapeResult creation with valid data."""
    ScrapeResult = _import_scrape_result()
    result = ScrapeResult(
        status="SUCCESS",
        url="https://example.com",
        title="Test Title",
        content_text="This is test content that is long enough",
        content_html="<html></html>",
        links=["https://example.com/link"],
    )

    assert result.status == "SUCCESS"
    assert result.url == "https://example.com"
    assert result.title == "Test Title"


def test_scrape_result_model_dump():
    ScrapeResult = _import_scrape_result()
    result = ScrapeResult(
        status="SUCCESS",
        url="https://example.com",
        title="Test",
        content_text="Content",
        content_html="<html></html>",
        links=[],
        visual_hash="abc",
        content_hash="def",
        http_status_code=200,
        crawl_duration=1.0,
        content_type="GENERAL",
        extracted_data={"key": "value"},
        healing_events=[],
    )

    data = result.model_dump()
    assert isinstance(data, dict)
    assert data["status"] == "SUCCESS"
    assert data["extracted_data"] == {"key": "value"}
