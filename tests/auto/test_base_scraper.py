from unittest.mock import AsyncMock

import pytest

from src.models.results import ScrapeResult
from src.scrapers.base import BaseScraper


class TestScraper(BaseScraper):
    """Concrete implementation for testing."""

    async def scrape(self, client, url):
        return ScrapeResult(
            status="SUCCESS",
            url=url,
            title="Test Title",
            content_text="Test content",
            content_html="<html></html>",
            links=[],
        )


def test_base_scraper_init():
    """Test BaseScraper initialization."""
    scraper = TestScraper("test_scraper")
    assert scraper.name == "test_scraper"


def test_base_scraper_str():
    """Test BaseScraper string representation."""
    scraper = TestScraper("test_scraper")
    assert str(scraper) == "Scraper(name=test_scraper)"


def test_base_scraper_get_info():
    """Test BaseScraper get_info method."""
    scraper = TestScraper("test_scraper")
    info = scraper.get_info()
    assert info["name"] == "test_scraper"
    assert info["type"] == "TestScraper"


@pytest.mark.asyncio
async def test_test_scraper_scrape():
    """Test the concrete test scraper implementation."""
    scraper = TestScraper("test_scraper")
    client = AsyncMock()

    result = await scraper.scrape(client, "https://example.com")

    assert isinstance(result, ScrapeResult)
    assert result.status == "SUCCESS"
    assert result.url == "https://example.com"
    assert result.title == "Test Title"
