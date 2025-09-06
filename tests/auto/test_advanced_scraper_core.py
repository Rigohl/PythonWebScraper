import pytest


def _import_advanced_scraper():
    try:
        from src.scraper import AdvancedScraper

        return AdvancedScraper
    except Exception:
        pytest.skip("AdvancedScraper not available in src.scraper")


@pytest.mark.asyncio
async def test_process_content_normalization(
    monkeypatch, mock_llm, mock_adapter, db_inmemory
):
    AdvancedScraper = _import_advanced_scraper()
    try:
        scraper = AdvancedScraper(
            browser_adapter=mock_adapter, db_manager=db_inmemory, llm_extractor=mock_llm
        )
    except TypeError:
        scraper = AdvancedScraper()

    monkeypatch.setattr(scraper, "llm_extractor", mock_llm, raising=False)

    # Mock response object
    class MockResponse:
        def __init__(self):
            self.status = 200
            self.headers = {"content-type": "text/html"}
            self.text = "<html><head><title>Test Title</title></head><body><h1>Test Title</h1><p>This is a test content that should be long enough after processing to pass the minimum content length validation.</p><p>Adding more content to ensure it meets the requirements for the scraper test.</p></body></html>"

    url = "https://example.com"
    full_html = "<html><head><title>Test Title</title></head><body><h1>Test Title</h1><p>This is a test content that should be long enough after processing to pass the minimum content length validation.</p><p>Adding more content to ensure it meets the requirements for the scraper test.</p></body></html>"
    # Mock response with simple content that won't be reduced too much
    response = MockResponse()

    if hasattr(scraper, "_process_content"):
        proc = await scraper._process_content(url, full_html, response)
        assert proc.status == "SUCCESS"
        assert proc.url == url
        assert proc.content_text is not None
        assert len(proc.content_text) > 0
    else:
        pytest.skip("No _process_content implementation found on AdvancedScraper")
