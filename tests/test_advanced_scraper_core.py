import pytest

from src.models.results import ScrapeResult
from src.scraper import AdvancedScraper


class DummyDB:
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
    def __init__(self):
        self._content = "<html><head><title>Title</title></head><body><p>Hello world</p></body></html>"
        self.cookies_were_set = False

    async def get_content(self):
        return self._content

    async def screenshot(self):
        # Return a small PNG bytes sequence or empty bytes to trigger 'unavailable'
        return b""


class DummyLLM:
    def __init__(self, cleaned=None, extracted=None):
        self.cleaned = cleaned
        self.extracted = extracted

    async def clean_text_content(self, text):
        return self.cleaned or text

    async def extract_structured_data(self, html, schema):
        return self.extracted


@pytest.mark.asyncio
async def test_process_content_normalizes_llm_output(tmp_path):
    db = DummyDB()
    adapter = DummyAdapter()
    # ensure cleaned text length exceeds MIN_CONTENT_LENGTH in settings
    llm = DummyLLM(
        cleaned=("cleaned text " * 5).strip(), extracted={"key": {"value": "v"}}
    )
    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    result = await scraper._process_content(
        url="http://example.com",
        full_html=await adapter.get_content(),
        response=type("R", (), {"status": 200, "url": "http://example.com"})(),
        extraction_schema=None,
    )

    assert isinstance(result, ScrapeResult)
    # result should reflect the cleaned text provided by the LLM
    assert result.content_text == llm.cleaned
    assert isinstance(result.extracted_data, dict) or result.extracted_data is None


@pytest.mark.asyncio
async def test_validate_content_quality_rejects_short_text():
    db = DummyDB()
    adapter = DummyAdapter()
    llm = DummyLLM(cleaned="x")
    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    with pytest.raises(Exception):
        await scraper._process_content(
            url="http://example.com",
            full_html="<html><head><title></title></head><body><p>x</p></body></html>",
            response=type("R", (), {"status": 200, "url": "http://example.com"})(),
            extraction_schema=None,
        )
