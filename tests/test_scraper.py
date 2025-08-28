import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.scraper import AdvancedScraper
from src.models.results import ScrapeResult
from src.exceptions import NetworkError, ParsingError, ContentQualityError
from playwright.async_api import Response, Request, Page
from pydantic import BaseModel
import json

# Fixture for AdvancedScraper instance
@pytest.fixture
def advanced_scraper(mock_page, mock_db_manager, mock_llm_extractor):
    return AdvancedScraper(page=mock_page, db_manager=mock_db_manager, llm_extractor=mock_llm_extractor)

@pytest.mark.asyncio
async def test_scrape_success(advanced_scraper, mock_page, mock_db_manager, mock_llm_extractor):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><head><title>Test Title</title></head><body><a href=\"/link1\">Link1</a></body></html>"
    mock_page.screenshot.return_value = b"dummy_screenshot_bytes"
    mock_llm_extractor.clean_text_content.return_value = "Cleaned content."

    result = await advanced_scraper.scrape("http://example.com")

    assert result.status == "SUCCESS"
    assert result.url == "http://example.com"
    assert result.title == "Test Title"
    assert result.content_text == "Cleaned content."
    assert "/link1" in result.links[0] # urljoin should resolve it
    assert result.visual_hash == "mock_visual_hash"
    assert result.http_status_code == 200
    assert result.content_type == "UNKNOWN" # Default classification
    mock_page.goto.assert_called_once_with("http://example.com", wait_until="domcontentloaded", timeout=30000)
    mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=15000)
    mock_page.content.assert_called_once()
    mock_llm_extractor.clean_text_content.assert_called_once()
    mock_page.screenshot.assert_called_once()

@pytest.mark.asyncio
async def test_scrape_network_error(advanced_scraper, mock_page):
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")

    result = await advanced_scraper.scrape("http://example.com")

    assert result.status == "RETRY"
    assert result.retryable is True
    assert "Timeout" in result.error_message

@pytest.mark.asyncio
async def test_scrape_retryable_status_code(advanced_scraper, mock_page, mock_settings_retryable_status_codes):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=500)

    result = await advanced_scraper.scrape("http://example.com")

    assert result.status == "RETRY"
    assert result.retryable is True
    assert "Estado reintentable: 500" in result.error_message

@pytest.mark.asyncio
async def test_scrape_content_quality_error_empty_text(advanced_scraper, mock_page, mock_llm_extractor):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><body></body></html>"
    mock_llm_extractor.clean_text_content.return_value = ""

    result = await advanced_scraper.scrape("http://example.com")

    assert result.status == "FAILED"
    assert "contenido extraído está vacío" in result.error_message

@pytest.mark.asyncio
async def test_scrape_content_quality_error_too_short(advanced_scraper, mock_page, mock_llm_extractor, mock_settings_min_content_length):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><body>Short</body></html>"
    mock_llm_extractor.clean_text_content.return_value = "Short"
    mock_settings_min_content_length.return_value = 100 # Set a high min length for test

    result = await advanced_scraper.scrape("http://example.com")

    assert result.status == "FAILED"
    assert "contenido es demasiado corto" in result.error_message

@pytest.mark.asyncio
async def test_scrape_content_quality_error_forbidden_phrase(advanced_scraper, mock_page, mock_llm_extractor, mock_settings_forbidden_phrases):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><body>Acceso Denegado</body></html>"
    mock_llm_extractor.clean_text_content.return_value = "Acceso Denegado"
    mock_settings_forbidden_phrases.return_value = ["acceso denegado"]

    result = await advanced_scraper.scrape("http://example.com")

    assert result.status == "FAILED"
    assert "página de error (contiene: 'acceso denegado')" in result.error_message

@pytest.mark.asyncio
async def test_scrape_llm_extraction_schema(advanced_scraper, mock_page, mock_llm_extractor):
    class ProductSchema(BaseModel):
        name: str
        price: float

    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html>...</html>"
    mock_llm_extractor.clean_text_content.return_value = "Cleaned content."
    mock_llm_extractor.extract_structured_data.return_value = ProductSchema(name="Test", price=10.0)

    result = await advanced_scraper.scrape("http://example.com", extraction_schema=ProductSchema)

    assert result.status == "SUCCESS"
    assert result.extracted_data == {"name": "Test", "price": 10.0}
    mock_llm_extractor.extract_structured_data.assert_called_once_with(mock_page.content.return_value, ProductSchema)

@pytest.mark.asyncio
async def test_scrape_cookie_loading_and_saving(advanced_scraper, mock_page, mock_db_manager):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><body></body></html>"
    mock_page.screenshot.return_value = b"dummy_screenshot_bytes"

    # Mock stored cookies
    mock_db_manager.load_cookies.return_value = json.dumps([{"name": "test_cookie", "value": "123"}])
    mock_page.context.cookies.return_value = [{"name": "new_cookie", "value": "456"}]

    await advanced_scraper.scrape("http://example.com")

    mock_db_manager.load_cookies.assert_called_once_with("example.com")
    mock_page.context.add_cookies.assert_called_once()
    mock_db_manager.save_cookies.assert_called_once()

@pytest.mark.asyncio
async def test_scrape_api_discovery(advanced_scraper, mock_page, mock_db_manager):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><body></body></html>"
    mock_page.screenshot.return_value = b"dummy_screenshot_bytes"

    # Simulate a response with JSON payload
    mock_response_obj = MagicMock(spec=Response)
    mock_response_obj.request.resource_type = "xhr"
    mock_response_obj.headers = {"content-type": "application/json"}
    mock_response_obj.url = "http://example.com/api/data"
    mock_response_obj.json.return_value = {"data": "test"}

    # Manually trigger the response handler
    # Playwright's page.on('response') adds a listener, which is hard to test directly without a real browser.
    # We'll simulate the call to the handler.
    await advanced_scraper.scrape("http://example.com")
    await advanced_scraper.page.listeners("response")[0](mock_response_obj) # Call the registered handler

    mock_db_manager.save_discovered_api.assert_called_once()
    args, kwargs = mock_db_manager.save_discovered_api.call_args
    assert kwargs['api_url'] == "http://example.com/api/data"
    assert kwargs['payload_hash'] is not None

@pytest.mark.asyncio
async def test_scrape_content_classification(advanced_scraper, mock_page, mock_llm_extractor):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><head><title>Producto XYZ</title></head><body>Comprar ahora!</body></html>"
    mock_llm_extractor.clean_text_content.return_value = "Producto XYZ. Comprar ahora!"
    mock_page.screenshot.return_value = b"dummy_screenshot_bytes"

    result = await advanced_scraper.scrape("http://example.com/product")
    assert result.content_type == "PRODUCT"

    mock_page.content.return_value = "<html><head><title>Blog Post</title></head><body>Leer más.</body></html>"
    mock_llm_extractor.clean_text_content.return_value = "Blog Post. Leer más."
    result = await advanced_scraper.scrape("http://example.com/blog")
    assert result.content_type == "BLOG_POST"

@pytest.mark.asyncio
async def test_scrape_removes_response_listener_in_finally(advanced_scraper, mock_page):
    mock_page.goto.return_value = AsyncMock(spec=Response, status=200)
    mock_page.content.return_value = "<html><body></body></html>"
    mock_page.screenshot.return_value = b"dummy_screenshot_bytes"

    # Ensure a listener is added
    await advanced_scraper.scrape("http://example.com")
    assert mock_page.on.called # Listener was added

    # Simulate an exception after adding listener
    mock_page.goto.side_effect = Exception("Test Exception")
    result = await advanced_scraper.scrape("http://example.com/error")

    # Verify remove_listener was called
    mock_page.remove_listener.assert_called_once()
    assert result.status == "FAILED"
