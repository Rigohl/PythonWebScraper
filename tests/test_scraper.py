import pytest
import os
from src.scraper import AdvancedScraper
from src.models.results import ScrapeResult
from tests.fixtures_adapters import mock_browser_adapter, mock_llm_adapter, mock_db_manager


@pytest.mark.asyncio
async def test_extract_title_from_local_html(html_file, mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """
    Tests if the AdvancedScraper correctly extracts the title from a local HTML file
    using mocked adapters.
    """
    # Read the content of the test HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Configure the mock browser adapter to return the HTML content
    mock_browser_adapter.mock_content = html_content

    # Instantiate AdvancedScraper with mocked adapters
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Construct a file URL for the local HTML file
    file_url = f"file:///{os.path.abspath(html_file).replace(os.sep, '/')}"

    # Call the async scrape method
    result: ScrapeResult = await scraper.scrape(url=file_url)

    # Assert that the extracted title is correct
    assert result.status == "SUCCESS"
    assert result.title == "Test Title"
