"""
Advanced tests for AdvancedScraper class.

This module provides comprehensive tests for the AdvancedScraper class,
covering various scenarios including successful scraping, error handling,
content validation, and integration with other components.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, AsyncMock
from pydantic import BaseModel, Field

from src.scraper import AdvancedScraper
from src.models.results import ScrapeResult
from src.exceptions import ContentQualityError, NetworkError
from tests.fixtures_adapters import mock_browser_adapter, mock_llm_adapter, mock_db_manager, mock_product_schema


@pytest.mark.asyncio
async def test_successful_scrape_with_all_features(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test a successful scrape with all features enabled."""
    # Configure the mock browser adapter
    mock_browser_adapter.mock_content = """
    <html>
        <head>
            <title>Test Product Page</title>
        </head>
        <body>
            <h1>Test Product</h1>
            <p>This is a great product with many features.</p>
            <div class="price">$99.99</div>
            <a href="/related-product1">Related Product 1</a>
            <a href="/related-product2">Related Product 2</a>
            <button>Add to Cart</button>
        </body>
    </html>
    """
    mock_browser_adapter.mock_url = "http://example.com/product"
    mock_browser_adapter.mock_response = {"status": 200, "url": "http://example.com/product", "headers": {}}

    # Configure additional mock behaviors
    mock_llm_adapter.mock_responses["extract_data"] = {
        "name": "Test Product",
        "price": 99.99
    }

    # Create the scraper with mocks
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Run the scrape
    result = await scraper.scrape(
        url="http://example.com/product",
        extraction_schema=mock_product_schema
    )

    # Verify the result
    assert result.status == "SUCCESS"
    assert result.title == "Test Product Page"
    assert "great product" in result.content_text
    assert result.http_status_code == 200
    assert result.content_type == "PRODUCT"
    assert result.extracted_data is not None
    assert result.extracted_data["name"] == "Test Product"
    assert result.extracted_data["price"] == 99.99
    assert len(result.links) == 2
    assert result.visual_hash is not None
    assert result.content_hash is not None

    # Verify interactions with dependencies
    mock_db_manager.save_cookies.assert_called_once()


@pytest.mark.asyncio
async def test_network_error_handling(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test handling of network errors."""
    # Configure the mock to simulate a network error
    mock_browser_adapter.mock_response = {"status": 503, "url": "http://example.com/error", "headers": {}}
    mock_browser_adapter.should_raise_network_error = True

    # Create the scraper with mocks
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Run the scrape
    result = await scraper.scrape(url="http://example.com/error")

    # Verify the error result
    assert result.status == "RETRY"
    assert result.url == "http://example.com/error"
    assert result.error_message is not None
    assert result.retryable is True


@pytest.mark.asyncio
async def test_content_quality_validation(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test validation of content quality."""
    # Configure the mock with low quality content
    mock_browser_adapter.mock_content = """
    <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <h1>Page not found</h1>
            <p>The requested page could not be found.</p>
        </body>
    </html>
    """
    mock_browser_adapter.mock_response = {"status": 200, "url": "http://example.com/low-quality", "headers": {}}

    # Configure LLM to return very short content
    mock_llm_adapter.mock_responses["clean_text"] = "Too short"

    # Create the scraper with mocks
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Run the scrape
    result = await scraper.scrape(url="http://example.com/low-quality")

    # Verify the failure result
    assert result.status == "FAILED"
    assert "corto" in result.error_message or "short" in result.error_message


@pytest.mark.asyncio
async def test_response_listener_captures_apis(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test that the response listener captures API calls."""
    # Configure mock
    mock_browser_adapter.mock_content = """
    <html>
        <head><title>Test API Page</title></head>
        <body><h1>Test API</h1></body>
    </html>
    """
    mock_browser_adapter.mock_response = {"status": 200, "url": "http://example.com/api-test", "headers": {}}

    # Simulate an API response
    api_response = {
        "url": "http://example.com/api/data",
        "headers": {"content-type": "application/json"},
        "request": {"resource_type": "xhr"},
        "json": lambda: {"data": "test"}
    }
    mock_browser_adapter.mock_api_responses = [api_response]

    # Create the scraper
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Run the scrape
    await scraper.scrape(url="http://example.com/api-test")

    # Verify the API was saved
    mock_db_manager.save_discovered_api.assert_called_once()


@pytest.mark.asyncio
async def test_cookie_management(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test cookie loading and saving."""
    # Configure mocks
    mock_browser_adapter.mock_content = "<html><head><title>Cookie Test</title></head><body>Test</body></html>"
    mock_browser_adapter.mock_response = {"status": 200, "url": "http://example.com/cookie-test", "headers": {}}
    mock_browser_adapter.mock_cookies = [{"name": "test", "value": "value", "domain": "example.com"}]

    # Configure DB to return cookies
    test_cookies = [{"name": "session", "value": "abc123", "domain": "example.com"}]
    mock_db_manager.load_cookies.return_value = json.dumps(test_cookies)

    # Create the scraper
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Run the scrape
    await scraper.scrape(url="http://example.com/cookie-test")

    # Verify cookies were loaded and saved
    mock_db_manager.load_cookies.assert_called_once_with("example.com")
    mock_db_manager.save_cookies.assert_called_once()
    assert mock_browser_adapter.cookies_were_set


@pytest.mark.asyncio
async def test_content_classification(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test correct classification of different content types."""
    # Product page
    mock_browser_adapter.mock_content = """
    <html>
        <head><title>Buy Product</title></head>
        <body><h1>Product</h1><p>Price: $10</p></body>
    </html>
    """
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )
    result = await scraper.scrape(url="http://example.com/product")
    assert result.content_type == "PRODUCT"

    # Blog post
    mock_browser_adapter.mock_content = """
    <html>
        <head><title>Blog Post</title></head>
        <body><h1>Latest Blog</h1><p>Blog content here</p></body>
    </html>
    """
    result = await scraper.scrape(url="http://example.com/blog")
    assert result.content_type == "BLOG_POST"

    # Tutorial
    mock_browser_adapter.mock_content = """
    <html>
        <head><title>Tutorial: How to Code</title></head>
        <body><h1>Coding Tutorial</h1><p>Learn to code</p></body>
    </html>
    """
    result = await scraper.scrape(url="http://example.com/tutorial")
    assert result.content_type == "ARTICLE"