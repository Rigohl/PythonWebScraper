import asyncio

from src.scrapers.base import BaseScraper


class DummyScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="dummy")

    async def scrape(self, client, url: str):
        # Minimal implementation for testing
        class _R:
            def __init__(self):
                self.status = "ok"

        return _R()


def test_get_info_contains_name_and_type():
    s = DummyScraper()
    info = s.get_info()
    assert isinstance(info, dict)
    assert "name" in info and "type" in info


def test_subclass_implements_scrape_event_loop():
    s = DummyScraper()
    # Ensure scrape is awaitable and callable
    coro = s.scrape(None, "http://example.com")
    assert asyncio.iscoroutine(coro)


"""
Tests for BaseScraper contract and functionality.
"""

import pytest
from httpx import AsyncClient

from src.scrapers.base import BaseScraper


class DummyScraper(BaseScraper):
    """Test implementation of BaseScraper for contract validation."""

    def __init__(self):
        super().__init__(name="dummy")

    async def scrape(self, client: AsyncClient, url: str):
        """Return a minimal ScrapeResult-like dict for testing."""
        return {"status": "ok", "url": url, "content": "test content"}


class TestBaseScraperContract:
    """Test BaseScraper abstract contract and behavior."""

    def test_base_scraper_get_info_contract(self):
        """Verify BaseScraper.get_info() returns required contract structure."""
        bs = DummyScraper()
        info = bs.get_info()
        assert isinstance(info, dict)
        assert info["name"] == "dummy"
        assert "type" in info
        # Note: BaseScraper.get_info() only returns name and type, not description
        assert info["type"] == "DummyScraper"

    def test_base_scraper_name_property(self):
        """Verify name property is accessible."""
        bs = DummyScraper()
        assert bs.name == "dummy"
        assert isinstance(bs.name, str)

    @pytest.mark.asyncio
    async def test_dummy_scrape_returns_expected_shape(self):
        """Verify scrape method returns proper structure."""
        dummy = DummyScraper()
        async with AsyncClient() as client:
            res = await dummy.scrape(client, "http://example.com")

        assert isinstance(res, dict)
        assert res["status"] == "ok"
        assert res["url"] == "http://example.com"
        assert "content" in res

    @pytest.mark.asyncio
    async def test_scrape_with_invalid_url(self):
        """Verify scrape handles invalid URLs gracefully."""
        dummy = DummyScraper()
        async with AsyncClient() as client:
            # Should not raise exception for invalid URL format
            res = await dummy.scrape(client, "not-a-url")

        assert isinstance(res, dict)
        assert "status" in res

    @pytest.mark.asyncio
    async def test_scrape_method_is_async(self):
        """Verify scrape method is properly async."""
        dummy = DummyScraper()

        async def run_scrape():
            async with AsyncClient() as client:
                return await dummy.scrape(client, "http://example.com")

        # Should be awaitable
        result = await run_scrape()
        assert isinstance(result, dict)

    def test_base_scraper_inheritance(self):
        """Verify DummyScraper properly inherits from BaseScraper."""
        dummy = DummyScraper()
        assert isinstance(dummy, BaseScraper)
        assert hasattr(dummy, "get_info")
        assert hasattr(dummy, "scrape")
        assert hasattr(dummy, "name")
