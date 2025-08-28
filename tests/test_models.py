import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from src.models.results import ScrapeResult, RetryableError
from src.settings import settings

def test_scrape_result_basic_instantiation():
    """Test basic instantiation of ScrapeResult with required fields."""
    result = ScrapeResult(status="SUCCESS", url="http://example.com/page")
    assert result.status == "SUCCESS"
    assert result.url == "http://example.com/page"
    assert isinstance(result.scraped_at, datetime)
    assert result.scraped_at.tzinfo == timezone.utc
    assert result.scraper_version == settings.SCRAPER_VERSION
    assert result.links == []
    assert result.title is None

def test_scrape_result_with_all_fields():
    """Test instantiation with all fields provided."""
    now = datetime.now(timezone.utc)
    result = ScrapeResult(
        status="FAILURE",
        url="http://example.com/error",
        scraped_at=now,
        scraper_version="v1.1",
        title="Error Page",
        content_text="Some error occurred.",
        content_html="<html>Error</html>",
        links=["http://example.com/link1"],
        extracted_data={"key": "value"},
        healing_events=[{"event": "retry"}],
        content_hash="abc",
        visual_hash="def",
        error_message="Failed to scrape",
        retryable=True,
        http_status_code=500,
        content_type="ERROR_PAGE",
        crawl_duration=1.5,
        llm_summary="Summary",
        llm_extracted_data={"llm_key": "llm_value"}
    )
    assert result.status == "FAILURE"
    assert result.url == "http://example.com/error"
    assert result.scraped_at == now
    assert result.scraper_version == "v1.1"
    assert result.title == "Error Page"
    assert result.content_text == "Some error occurred."
    assert result.content_html == "<html>Error</html>"
    assert result.links == ["http://example.com/link1"]
    assert result.extracted_data == {"key": "value"}
    assert result.healing_events == [{"event": "retry"}]
    assert result.content_hash == "abc"
    assert result.visual_hash == "def"
    assert result.error_message == "Failed to scrape"
    assert result.retryable is True
    assert result.http_status_code == 500
    assert result.content_type == "ERROR_PAGE"
    assert result.crawl_duration == 1.5
    assert result.llm_summary == "Summary"
    assert result.llm_extracted_data == {"llm_key": "llm_value"}

def test_scrape_result_invalid_status_type():
    """Test that ValidationError is raised for invalid status type."""
    with pytest.raises(ValidationError):
        ScrapeResult(status=123, url="http://example.com")

def test_scrape_result_missing_required_fields():
    """Test that ValidationError is raised for missing required fields."""
    with pytest.raises(ValidationError):
        ScrapeResult(url="http://example.com") # Missing status
    with pytest.raises(ValidationError):
        ScrapeResult(status="SUCCESS") # Missing url

def test_retryable_error_exception():
    """Test the custom RetryableError exception."""
    with pytest.raises(RetryableError, match="This is a retryable error"):
        raise RetryableError("This is a retryable error")
