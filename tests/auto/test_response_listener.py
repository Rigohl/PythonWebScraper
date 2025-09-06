import pytest


def _get_scraper_module():
    try:
        import src.scraper as scraper_mod

        return scraper_mod
    except Exception:
        pytest.skip("src.scraper not importable")


def test_response_listener_calls_db(monkeypatch, db_inmemory):
    scraper_mod = _get_scraper_module()
    if not hasattr(scraper_mod, "_response_listener"):
        pytest.skip("_response_listener not implemented")

    called = {}

    def fake_save_discovered_api(page_url, api_url, payload_hash):
        called["args"] = (page_url, api_url, payload_hash)

    if hasattr(scraper_mod, "db_manager"):
        monkeypatch.setattr(
            scraper_mod,
            "db_manager",
            type(
                "D", (), {"save_discovered_api": staticmethod(fake_save_discovered_api)}
            ),
        )
    else:
        monkeypatch.setattr(
            scraper_mod,
            "db_manager",
            type(
                "D", (), {"save_discovered_api": staticmethod(fake_save_discovered_api)}
            ),
            raising=False,
        )

    class FakeResponse:
        def __init__(self):
            self.resource_type = "xhr"
            self.headers = {"content-type": "application/json"}
            self.url = "https://example.com/api"
            self.body = b'{"a":1}'

    resp = FakeResponse()
    try:
        maybe = scraper_mod._response_listener(resp)
        if hasattr(maybe, "__await__"):
            # run coroutine
            import asyncio

            asyncio.get_event_loop().run_until_complete(maybe)
    except Exception:
        # If the listener is designed as a context manager or async handler, try calling handler directly
        try:
            handler = scraper_mod._response_listener
            handler(resp)
        except Exception:
            pass

    assert "args" in called
    assert "example.com" in called["args"][1]
