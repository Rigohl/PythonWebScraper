import asyncio
import json
import pytest

from src.adapters.httpx_adapter import HttpxAdapter, HTTPX_AVAILABLE

pytestmark = pytest.mark.asyncio

if not HTTPX_AVAILABLE:  # pragma: no cover - entorno sin httpx
    pytest.skip("httpx no disponible", allow_module_level=True)

import httpx


def _build_client(responses_map):
    def handler(request: httpx.Request) -> httpx.Response:  # noqa: D401
        data = responses_map.get(str(request.url))
        if data is None:
            return httpx.Response(404, text="not found")
        body, status, headers = data
        return httpx.Response(status, content=body, headers=headers)
    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(transport=transport, follow_redirects=True)


async def test_fetch_html_success():
    client = _build_client({
        "https://example.com/": (b"<html><body>OK</body></html>", 200, {"Content-Type": "text/html"})
    })
    adapter = HttpxAdapter(client=client)
    html = await adapter.fetch_html("https://example.com/")
    assert "OK" in html
    await adapter.close()


async def test_fetch_json_success():
    payload = {"value": 123}
    client = _build_client({
        "https://api.example.com/data": (json.dumps(payload).encode(), 200, {"Content-Type": "application/json"})
    })
    adapter = HttpxAdapter(client=client)
    data = await adapter.fetch_json("https://api.example.com/data")
    assert data["value"] == 123
    await adapter.close()


async def test_retries_and_failure():
    # 500 then 500 then 200 should still return result within retries
    sequence = [500, 500, 200]
    def handler(request: httpx.Request) -> httpx.Response:  # noqa: D401
        status = sequence.pop(0)
        body = b"{\"ok\": true}" if status == 200 else b"err"
        return httpx.Response(status, content=body, headers={"Content-Type": "application/json"})
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = HttpxAdapter(client=client)
    data = await adapter.fetch_json("https://api.example.com/ping", max_retries=3)
    assert data["ok"] is True
    await adapter.close()


async def test_exhaust_retries():
    def handler(request: httpx.Request) -> httpx.Response:  # noqa: D401
        return httpx.Response(503, content=b"down")
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = HttpxAdapter(client=client)
    with pytest.raises(RuntimeError):
        await adapter.fetch_html("https://unstable.example.com/", max_retries=1)
    await adapter.close()
