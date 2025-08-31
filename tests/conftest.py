"""
pytest configuration file for shared fixtures.

This file defines fixtures that are used across multiple test files.
"""
import os
import asyncio
from unittest.mock import Mock, AsyncMock

import pytest
from playwright.async_api import Page, Response
from src.database import DatabaseManager
from src.llm_extractor import LLMExtractor


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
