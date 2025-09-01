"""
pytest configuration file for shared fixtures.

This file defines fixtures that are used across multiple test files.
"""
import os
import sys
import asyncio
from unittest.mock import Mock, AsyncMock

# Ensure the project root is on sys.path so `src` imports work under pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from playwright.async_api import Page, Response
from src.db.database import DatabaseManager
from src.intelligence.llm_extractor import LLMExtractor


@pytest.fixture
def mock_page():
    """A mock Playwright Page object that simulates page interactions."""
    mock = AsyncMock(spec=Page)

    # Ensure event registration methods behave like sync functions (no coroutine)
    from unittest.mock import Mock as SyncMock
    mock.on = SyncMock()
    mock.remove_listener = SyncMock()

    # Mock the response object that page.goto() returns
    mock_response = AsyncMock(spec=Response)
    mock_response.ok = True
    mock_response.status = 200
    mock_response.headers = {'content-type': 'text/html'}

    # Make response.text/body awaitable and return concrete values
    mock_response.text = AsyncMock(return_value="<html><body>Mocked HTML content</body></html>")
    mock_response.body = AsyncMock(return_value=b"<html><body>Mocked HTML content</body></html>")

    mock.goto = AsyncMock(return_value=mock_response)

    # Keep the previous fixes for screenshot and content as awaitable values
    mock.screenshot = AsyncMock(return_value=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    mock.content = AsyncMock(return_value="<html><body>Mocked HTML content</body></html>")

    # Provide a context object with async methods used by the scraper
    mock_context = SyncMock()
    mock_context.add_cookies = AsyncMock(return_value=None)
    mock_context.cookies = AsyncMock(return_value=[])
    mock.context = mock_context

    yield mock

@pytest.fixture
def mock_db_manager():
    """A mock DatabaseManager."""
    mock = Mock(spec=DatabaseManager)
    mock.load_cookies.return_value = None
    mock.save_cookies.return_value = None
    mock.save_discovered_api.return_value = None
    yield mock


@pytest.fixture
def mock_llm_extractor():
    """A mock LLMExtractor."""
    mock = AsyncMock(spec=LLMExtractor)
    mock.clean_text_content.side_effect = lambda x: x
    mock.extract_structured_data.return_value = None
    yield mock


@pytest.fixture
def html_file():
    """Fixture that provides the path to the test HTML file."""
    return os.path.join(os.path.dirname(__file__), "test_page.html")


@pytest.fixture
def http_server():
    """A local HTTP server fixture for integration tests."""
    import asyncio
    import aiohttp
    from aiohttp import web

    async def create_server():
        async def index_handler(request):
            return web.Response(text="""
            <!DOCTYPE html>
            <html>
            <head><title>Test Site</title></head>
            <body>
                <h1>Test Index</h1>
                <a href="/page1.html">Page 1</a>
                <a href="/page2.html">Page 2</a>
            </body>
            </html>
            """, content_type='text/html')

        async def page1_handler(request):
            return web.Response(text="""
            <!DOCTYPE html>
            <html>
            <head><title>Page 1</title></head>
            <body>
                <h1>Page 1</h1>
                <p>This is page 1 content.</p>
            </body>
            </html>
            """, content_type='text/html')

        async def page2_handler(request):
            return web.Response(text="""
            <!DOCTYPE html>
            <html>
            <head><title>Page 2</title></head>
            <body>
                <h1>Page 2</h1>
                <p>This is page 2 content.</p>
            </body>
            </html>
            """, content_type='text/html')

        async def index_with_clone_handler(request):
            return web.Response(text="""
            <!DOCTYPE html>
            <html>
            <head><title>Test Site with Clone</title></head>
            <body>
                <h1>Test Index with Clone</h1>
                <a href="/page1.html">Page 1</a>
                <a href="/page1_clone.html">Page 1 Clone</a>
            </body>
            </html>
            """, content_type='text/html')

        async def page1_clone_handler(request):
            return web.Response(text="""
            <!DOCTYPE html>
            <html>
            <head><title>Page 1 Clone</title></head>
            <body>
                <h1>Page 1 Clone</h1>
                <p>This is identical content to page 1.</p>
            </body>
            </html>
            """, content_type='text/html')

        app = web.Application()
        app.router.add_get('/', index_handler)
        app.router.add_get('/index.html', index_handler)
        app.router.add_get('/page1.html', page1_handler)
        app.router.add_get('/page2.html', page2_handler)
        app.router.add_get('/index_with_clone.html', index_with_clone_handler)
        app.router.add_get('/page1_clone.html', page1_clone_handler)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, 'localhost', 0)  # Use port 0 for auto-assignment
        await site.start()

        # Get the actual port
        port = site._server.sockets[0].getsockname()[1]
        base_url = f"http://localhost:{port}"

        return base_url, runner

    # Run the async server creation
    base_url, runner = asyncio.run(create_server())

    yield base_url

    # Cleanup
    asyncio.run(runner.cleanup())
