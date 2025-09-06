"""
Tests for AdvancedScraper LLM processing and content validation.
"""

import pytest

from src.models.results import ScrapeResult
from src.scraper import AdvancedScraper


class DummyDB:
    """Mock database for testing."""

    def __init__(self):
        self.saved_apis = []
        self.cookies = {}

    def save_discovered_api(self, page_url, api_url, payload_hash):
        self.saved_apis.append((page_url, api_url, payload_hash))

    def load_cookies(self, domain):
        return self.cookies.get(domain)

    def save_cookies(self, domain, cj):
        self.cookies[domain] = cj


class DummyAdapter:
    """Mock browser adapter for testing."""

    def __init__(self):
        self._content = "<html><head><title>Title</title></head><body><p>Hello world</p></body></html>"
        self.cookies_were_set = False

    async def get_content(self):
        return self._content

    async def screenshot(self):
        # Return a small PNG bytes sequence or empty bytes to trigger 'unavailable'
        return b""


class DummyLLM:
    """Mock LLM for testing different scenarios."""

    def __init__(
        self,
        cleaned=None,
        extracted=None,
        should_fail=False,
        fail_on_clean=False,
        fail_on_extract=False,
    ):
        self.cleaned = cleaned
        self.extracted = extracted
        self.should_fail = should_fail
        self.fail_on_clean = fail_on_clean
        self.fail_on_extract = fail_on_extract

    async def clean_text_content(self, text):
        if self.fail_on_clean or self.should_fail:
            raise Exception("LLM processing failed")
        return self.cleaned or text

    async def extract_structured_data(self, html, schema):
        if self.fail_on_extract or self.should_fail:
            raise Exception("LLM extraction failed")
        return self.extracted


class TestAdvancedScraperLLM:
    """Test LLM processing in AdvancedScraper."""

    @pytest.mark.asyncio
    async def test_process_content_normalizes_llm_output(self):
        """Test that LLM output is properly normalized and stored."""
        db = DummyDB()
        adapter = DummyAdapter()
        # Ensure cleaned text length exceeds MIN_CONTENT_LENGTH in settings
        llm = DummyLLM(
            cleaned=("cleaned text " * 5).strip(), extracted={"key": {"value": "v"}}
        )
        scraper = AdvancedScraper(
            db_manager=db, browser_adapter=adapter, llm_extractor=llm
        )

        result = await scraper._process_content(  # type: ignore
            url="http://example.com",
            full_html=await adapter.get_content(),
            response=type("R", (), {"status": 200, "url": "http://example.com"})(),
            extraction_schema=None,
        )

        assert isinstance(result, ScrapeResult)
        # Result should reflect the cleaned text provided by the LLM
        assert result.content_text == llm.cleaned
        assert isinstance(result.extracted_data, dict) or result.extracted_data is None

    @pytest.mark.asyncio
    async def test_validate_content_quality_rejects_short_text(self):
        """Test content quality validation rejects text below minimum length."""
        db = DummyDB()
        adapter = DummyAdapter()
        llm = DummyLLM(cleaned="x")
        scraper = AdvancedScraper(
            db_manager=db, browser_adapter=adapter, llm_extractor=llm
        )

        with pytest.raises(Exception, match="contenido es demasiado corto"):
            await scraper._process_content(  # type: ignore
                url="http://example.com",
                full_html="<html><head><title></title></head><body><p>x</p></body></html>",
                response=type("R", (), {"status": 200, "url": "http://example.com"})(),
                extraction_schema=None,
            )

    @pytest.mark.asyncio
    async def test_llm_clean_text_content_error_handling(self):
        """Test error handling when LLM clean_text_content fails."""
        db = DummyDB()
        adapter = DummyAdapter()
        llm = DummyLLM(fail_on_clean=True)
        scraper = AdvancedScraper(
            db_manager=db, browser_adapter=adapter, llm_extractor=llm
        )

        with pytest.raises(Exception, match="LLM processing failed"):
            await scraper._process_content(  # type: ignore
                url="http://example.com",
                full_html=await adapter.get_content(),
                response=type("R", (), {"status": 200, "url": "http://example.com"})(),
                extraction_schema=None,
            )

    @pytest.mark.asyncio
    async def test_llm_extract_structured_data_error_handling(self):
        """Test error handling when LLM extract_structured_data fails."""
        db = DummyDB()
        adapter = DummyAdapter()
        llm = DummyLLM(cleaned="cleaned text content", fail_on_extract=True)
        scraper = AdvancedScraper(
            db_manager=db, browser_adapter=adapter, llm_extractor=llm
        )

        with pytest.raises(Exception, match="LLM extraction failed"):
            await scraper._process_content(  # type: ignore
                url="http://example.com",
                full_html=await adapter.get_content(),
                response=type("R", (), {"status": 200, "url": "http://example.com"})(),
                extraction_schema={"type": "object"},
            )

    @pytest.mark.asyncio
    async def test_llm_processing_with_schema(self):
        """Test LLM processing with extraction schema."""
        db = DummyDB()
        adapter = DummyAdapter()
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        # Make cleaned content long enough to pass validation
        llm = DummyLLM(
            cleaned="cleaned content that is long enough to pass validation requirements",
            extracted={"title": "Test Title"},
        )
        scraper = AdvancedScraper(
            db_manager=db, browser_adapter=adapter, llm_extractor=llm
        )

        result = await scraper._process_content(
            url="http://example.com",
            full_html=await adapter.get_content(),
            response=type("R", (), {"status": 200, "url": "http://example.com"})(),
            extraction_schema=schema,
        )

        assert isinstance(result, ScrapeResult)
        assert (
            result.content_text
            == "cleaned content that is long enough to pass validation requirements"
        )
        assert result.extracted_data == {"title": "Test Title"}

    @pytest.mark.asyncio
    async def test_llm_async_behavior(self):
        """Test that LLM methods are properly async."""
        llm = DummyLLM(cleaned="test", extracted={"key": "value"})

        # Test clean_text_content is awaitable
        result = await llm.clean_text_content("input text")
        assert result == "test"

        # Test extract_structured_data is awaitable
        result = await llm.extract_structured_data("<html></html>", {})
        assert result == {"key": "value"}
