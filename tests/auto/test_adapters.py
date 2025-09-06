from unittest.mock import AsyncMock

import pytest

from src.adapters.httpx_adapter import HttpxAdapter


@pytest.mark.asyncio
async def test_httpx_adapter_basic():
    """Test basic HttpxAdapter initialization and methods."""
    adapter = HttpxAdapter()

    # Test that it has the expected methods
    assert hasattr(adapter, "fetch_html")
    assert hasattr(adapter, "fetch_json")
    assert hasattr(adapter, "close")

    await adapter.close()


@pytest.mark.asyncio
async def test_httpx_adapter_get():
    """Test HttpxAdapter fetch methods with mock."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.text = "<html><body>Test</body></html>"
    mock_response.status_code = 200
    mock_client.request.return_value = mock_response

    adapter = HttpxAdapter(client=mock_client)

    result = await adapter.fetch_html("http://example.com")
    assert result == "<html><body>Test</body></html>"

    await adapter.close()


def _import_browser_adapter():
    try:
        from src.adapters.browser_adapter import BrowserAdapter

        return BrowserAdapter
    except Exception:
        pytest.skip("BrowserAdapter not available")


def test_browser_adapter_abstract():
    BrowserAdapter = _import_browser_adapter()

    # Should not be instantiable directly
    with pytest.raises(TypeError):
        BrowserAdapter()


def _import_llm_adapter():
    try:
        from src.adapters.llm_adapter import LLMAdapter

        return LLMAdapter
    except Exception:
        pytest.skip("LLMAdapter not available")


def test_llm_adapter_abstract():
    LLMAdapter = _import_llm_adapter()

    # Should not be instantiable directly
    with pytest.raises(TypeError):
        LLMAdapter()
