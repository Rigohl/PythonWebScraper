"""
Tests for response listener API discovery functionality.
"""

import json
from unittest.mock import MagicMock

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


@pytest.mark.asyncio
async def test_response_listener_ignores_non_json_responses():
    """Test that non-JSON responses are ignored."""
    db = DummyDB()
    adapter = DummyAdapter()
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    async with scraper._response_listener():
        handler = adapter.listeners[0]
        # Test HTML response
        resp = FakeResponse("http://example.com/page", {"content-type": "text/html"})
        await handler(resp)

        # Test plain text response
        resp = FakeResponse("http://example.com/data", {"content-type": "text/plain"})
        await handler(resp)

    # Verify no APIs were saved
    assert len(db.saved) == 0


@pytest.mark.asyncio
async def test_response_listener_ignores_non_xhr_responses():
    """Test that non-XHR/fetch responses are ignored."""
    db = DummyDB()
    adapter = DummyAdapter()
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    async with scraper._response_listener():
        handler = adapter.listeners[0]
        # Test document response
        resp = FakeResponse(
            "http://example.com/page",
            {"content-type": "application/json"},
            resource_type="document",
            json_payload={"data": "test"},
        )
        await handler(resp)

        # Test stylesheet response
        resp = FakeResponse(
            "http://example.com/style.css",
            {"content-type": "application/json"},
            resource_type="stylesheet",
            json_payload={"data": "test"},
        )
        await handler(resp)

    # Verify no APIs were saved
    assert len(db.saved) == 0


@pytest.mark.asyncio
async def test_response_listener_handles_invalid_json():
    """Test that invalid JSON payloads are handled gracefully."""
    db = DummyDB()
    adapter = DummyAdapter()
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    async with scraper._response_listener():
        handler = adapter.listeners[0]
        # Test response that raises exception on json()
        resp = FakeResponse(
            "http://api.example.com/data",
            {"content-type": "application/json"},
            json_payload=ValueError("Invalid JSON"),
        )
        await handler(resp)

    # Verify no API was saved due to invalid JSON
    assert len(db.saved) == 0


@pytest.mark.asyncio
async def test_response_listener_captures_fetch_responses():
    """Test that fetch responses with JSON are also captured."""
    db = DummyDB()
    adapter = DummyAdapter()
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    async with scraper._response_listener():
        handler = adapter.listeners[0]
        resp = FakeResponse(
            "http://api.example.com/fetch",
            {"content-type": "application/json"},
            resource_type="fetch",
            json_payload={"result": "success"},
        )
        await handler(resp)

    # Verify API was saved
    assert len(db.saved) == 1
    page_url, api_url, payload_hash = db.saved[0]
    assert api_url == "http://api.example.com/fetch"


@pytest.mark.asyncio
async def test_response_listener_handles_adapter_url_failure():
    """Test graceful handling when adapter URL retrieval fails."""
    db = DummyDB()
    adapter = DummyAdapter()
    # Make get_current_url raise exception
    adapter.get_current_url = MagicMock(side_effect=RuntimeError("URL unavailable"))
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    async with scraper._response_listener():
        handler = adapter.listeners[0]
        resp = FakeResponse(
            "http://api.example.com/data",
            {"content-type": "application/json"},
            json_payload={"data": "test"},
        )
        await handler(resp)

    # Verify API was still saved with None page_url
    assert len(db.saved) == 1
    page_url, api_url, payload_hash = db.saved[0]
    assert page_url is None  # Should be None due to URL retrieval failure
    assert api_url == "http://api.example.com/data"


@pytest.mark.asyncio
async def test_response_listener_calculates_correct_payload_hash():
    """Test that payload hash is calculated correctly from JSON."""
    db = DummyDB()
    adapter = DummyAdapter()
    scraper = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=object()
    )

    json_payload = {"items": [1, 2, 3], "data": "test"}
    expected_payload_str = json.dumps(json_payload, sort_keys=True)
    expected_hash = (
        __import__("hashlib").sha256(expected_payload_str.encode("utf-8")).hexdigest()
    )

    async with scraper._response_listener():
        handler = adapter.listeners[0]
        resp = FakeResponse(
            "http://api.example.com/data",
            {"content-type": "application/json"},
            json_payload=json_payload,
        )
        await handler(resp)

    # Verify hash is correct
    assert len(db.saved) == 1
    page_url, api_url, payload_hash = db.saved[0]
    assert payload_hash == expected_hash
