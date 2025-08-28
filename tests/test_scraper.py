import pytest
from unittest.mock import AsyncMock, MagicMock
import os
from src.scraper import AdvancedScraper
from src.models.results import ScrapeResult

# Mock Playwright Page and its methods
@pytest.fixture
def mock_page():
    page = AsyncMock()
    # Mock the goto method to return a mock response
    mock_response = MagicMock()
    mock_response.status = 200
    page.goto.return_value = mock_response
    # Mock wait_for_load_state
    page.wait_for_load_state.return_value = None
    # Mock screenshot method
    page.screenshot.return_value = b'mock_screenshot_bytes'
    return page

# Mock DatabaseManager
@pytest.fixture
def mock_db_manager():
    db_manager = MagicMock()
    db_manager.get_result_by_url.return_value = None # Or a default value if needed
    return db_manager

# Mock LLMExtractor
@pytest.fixture
def mock_llm_extractor():
    llm_extractor = AsyncMock()
    llm_extractor.clean_text_content.return_value = "cleaned text content" # Mock cleaned text
    return llm_extractor

@pytest.mark.asyncio
async def test_extract_title_from_local_html(html_file, mock_page, mock_db_manager, mock_llm_extractor):
    """
    Tests if the AdvancedScraper correctly extracts the title from a local HTML file
    using mocked Playwright Page and other dependencies.
    """
    # Read the content of the test HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Configure the mock_page.content() to return the HTML content
    mock_page.content.return_value = html_content

    # Instantiate AdvancedScraper with mocked dependencies
    scraper = AdvancedScraper(page=mock_page, db_manager=mock_db_manager, llm_extractor=mock_llm_extractor)

    # Construct a file URL for the local HTML file (though scraper will use mock_page.content)
    file_url = f"file:///{os.path.abspath(html_file).replace(os.sep, '/')}"

    # Call the async scrape method
    result: ScrapeResult = await scraper.scrape(url=file_url)

    # Assert that the extracted title is correct
    assert result.status == "SUCCESS"
    assert result.title == "Test Title"

    # Verify that page.goto and page.content were called
    mock_page.goto.assert_called_once_with(file_url, wait_until="domcontentloaded", timeout=30000)
    mock_page.content.assert_called_once()
