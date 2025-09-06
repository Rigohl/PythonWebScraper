import asyncio

import pytest

from src.adapters.browser_adapter import MockBrowserAdapter
from src.adapters.httpx_adapter import HttpxAdapter
from src.adapters.llm_adapter import MockLLMAdapter, OfflineLLMAdapter


@pytest.mark.asyncio
async def test_mock_browser_adapter_navigation_and_content():
    adapter = MockBrowserAdapter()
    resp = await adapter.navigate_to_url("http://example.com")
    assert resp["status"] == 200
    content = await adapter.get_content()
    assert "Test content" in content


@pytest.mark.asyncio
async def test_offline_llm_clean_and_summarize():
    llm = OfflineLLMAdapter()
    cleaned = await llm.clean_text("   Hola   mundo   \n")
    assert cleaned == "Hola mundo"
    summary = await llm.summarize_content("one two three four five", max_words=3)
    assert summary.split()[0] == "one"


def test_mock_llm_adapter_sync_and_counts():
    mock = MockLLMAdapter({"clean_text": "ok"})
    loop = asyncio.get_event_loop()
    cleaned = loop.run_until_complete(mock.clean_text("x"))
    assert cleaned == "ok"
    assert mock.call_count >= 1


# Basic smoke test for HttpxAdapter using a mocked client
@pytest.mark.asyncio
async def test_httpx_adapter_request_mock(monkeypatch):
    class DummyResponse:
        status_code = 200
        text = "<html></html>"

        def json(self):
            return {"ok": True}

    class DummyClient:
        async def request(self, method, url, timeout):
            return DummyResponse()

        async def aclose(self):
            pass

    adapter = HttpxAdapter(client=DummyClient())
    html = await adapter.fetch_html("http://test")
    assert "<html" in html
    data = await adapter.fetch_json("http://test")
    assert data.get("ok") is True
