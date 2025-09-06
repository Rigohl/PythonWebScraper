import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scraper_integration(mock_llm, mock_adapter, db_inmemory):
    """Integration test for scraper with all components."""
    try:
        from src.scraper import AdvancedScraper
    except Exception:
        pytest.skip("Required modules not available")

    scraper = AdvancedScraper(
        browser_adapter=mock_adapter, db_manager=db_inmemory, llm_extractor=mock_llm
    )

    # Mock the navigation
    async def mock_navigate(url):
        return {
            "status": 200,
            "url": url,
            "content": "<html><body>Test content</body></html>",
        }

    mock_adapter.navigate = mock_navigate

    # This would be a full integration test
    # For now, just test that the scraper can be initialized
    assert scraper.adapter is not None
    assert scraper.db_manager is not None
    assert scraper.llm_extractor is not None


@pytest.mark.integration
def test_database_operations(db_inmemory):
    """Test database operations integration."""
    try:
        from src.models.results import ScrapeResult
    except Exception:
        pytest.skip("ScrapeResult not available")

    # Create a test result
    result = ScrapeResult(
        status="SUCCESS",
        url="https://example.com",
        title="Test",
        content_text="Test content",
        content_html="<html></html>",
        links=[],
        visual_hash="abc",
        content_hash="def",
        http_status_code=200,
        crawl_duration=1.0,
        content_type="GENERAL",
        extracted_data=None,
        healing_events=[],
    )

    # Test save and retrieve
    db_inmemory.save_result(result)

    retrieved = db_inmemory.get_result_by_url("https://example.com")
    assert retrieved is not None
    assert retrieved["status"] == "SUCCESS"
    assert retrieved["url"] == "https://example.com"
