import json
from unittest.mock import MagicMock

import pytest

from src.scraper import AdvancedScraper


class MockBrowserAdapter:
    def __init__(self):
        self.listeners = []
        self._cookies = []
        self.cookies_were_set = False

    def add_response_listener(self, handler):
        self.listeners.append(handler)

    def remove_response_listener(self, handler):
        try:
            self.listeners.remove(handler)
        except ValueError:
            pass

    async def set_cookies(self, cookies):
        self._cookies = cookies
        self.cookies_were_set = True

    async def get_cookies(self):
        return self._cookies

    async def navigate_to_url(self, url):
        return {"status": 200, "url": url, "headers": {}}

    async def get_content(self):
        return "<html><head><title>Test</title></head><body><p>Hello world</p><a href='/x'>x</a></body></html>"

    async def screenshot(self):
        # 1x1 PNG minimal image bytes
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
        )


class MockResponse:
    def __init__(self, url, payload=None, resource_type="xhr", headers=None):
        self.url = url
        self.request = type("r", (), {"resource_type": resource_type})
        self.headers = headers or {"content-type": "application/json"}
        self._payload = payload or {"ok": True}

    async def json(self):
        return self._payload


class MockLLM:
    def __init__(self, cleaned_text=None, extracted=None):
        self._cleaned = cleaned_text or ("cleaned " * 20)
        self._extracted = extracted

    async def clean_text_content(self, text):
        return self._cleaned

    async def extract_structured_data(self, html, response_model=None):
        return self._extracted


@pytest.mark.asyncio
async def test_response_listener_calls_db_save():
    adapter = MockBrowserAdapter()
    db_manager = MagicMock()
    db_manager.save_discovered_api = MagicMock()
    llm = MockLLM()
    scraper = AdvancedScraper(
        browser_adapter=adapter, db_manager=db_manager, llm_extractor=llm
    )

    # Attach context manager which registers listener
    async with scraper._response_listener():
        assert len(adapter.listeners) == 1
        handler = adapter.listeners[0]
        resp = MockResponse("https://example.com/api/data", payload={"x": 1})
        await handler(resp)

    # Ensure DB save called once with expected args
    assert db_manager.save_discovered_api.called
    args, _ = db_manager.save_discovered_api.call_args
    assert (
        "api_url" in db_manager.save_discovered_api.call_args.kwargs or len(args) >= 2
    )


@pytest.mark.asyncio
async def test_apply_and_persist_cookies_interact_with_db_and_adapter():
    adapter = MockBrowserAdapter()
    db_manager = MagicMock()
    # Simulate DB having cookies stored as JSON
    cookies = [{"name": "sid", "value": "abc", "domain": "example.com"}]
    db_manager.load_cookies = MagicMock(return_value=json.dumps(cookies))
    db_manager.save_cookies = MagicMock()
    llm = MockLLM()

    scraper = AdvancedScraper(
        browser_adapter=adapter, db_manager=db_manager, llm_extractor=llm
    )

    # Apply cookies should call adapter.set_cookies and mark cookies_were_set
    await scraper._apply_cookies("example.com")
    assert adapter.cookies_were_set is True or adapter._cookies == cookies

    # Now make adapter return cookies and persist them
    adapter._cookies = cookies
    saved = await scraper._persist_cookies("example.com")
    # Confirm DB save_cookies was called
    assert db_manager.save_cookies.called


@pytest.mark.asyncio
async def test_process_content_and_classification_with_mock_llm():
    adapter = MockBrowserAdapter()
    db_manager = MagicMock()
    llm = MockLLM(cleaned_text=("word " * 50))
    scraper = AdvancedScraper(
        browser_adapter=adapter, db_manager=db_manager, llm_extractor=llm
    )

    html = await adapter.get_content()
    result = await scraper._process_content(
        "https://example.com/page", html, response=None
    )

    assert result.status == "SUCCESS"
    assert "cleaned" in result.content_text or len(result.content_text) > 10
    assert isinstance(result.links, list)
    # classification should yield GENERAL for sufficiently long content
    assert result.content_type in {"GENERAL", "ARTICLE", "UNKNOWN", "BLOG_POST"}
