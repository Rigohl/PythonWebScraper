import pytest

from src.scraper import AdvancedScraper


class FakeResponse:
    def __init__(self, url, headers, resource_type="xhr", json_payload=None):
        self.url = url
        self.headers = headers
        self.request = type("Q", (), {"resource_type": resource_type})()
        self._json = json_payload

    async def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json


class DummyDB:
    def __init__(self):
        self.saved = []

    def save_discovered_api(self, page_url, api_url, payload_hash):
        self.saved.append((page_url, api_url, payload_hash))


class DummyAdapter:
    def __init__(self):
        self.listeners = []

    def add_response_listener(self, h):
        self.listeners.append(h)

    def remove_response_listener(self, h):
        self.listeners.remove(h)

    def get_current_url(self):
        return "http://example.com"


@pytest.mark.asyncio
async def test_response_listener_saves_json_api(monkeypatch):
    db = DummyDB()
    adapter = DummyAdapter()
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    # Emulate entering context manager
    async with scraper._response_listener():
        # Call handler directly via adapter.listeners
        handler = adapter.listeners[0]
        resp = FakeResponse(
            "http://api.example/1",
            {"content-type": "application/json"},
            json_payload={"a": 1},
        )
        await handler(resp)

    assert len(db.saved) == 1
