import pytest

from src.models.results import ScrapeResult
from src.scraper import AdvancedScraper


class DummyAdapter:
    async def get_content(self):
        return (
            "<html><head><title>t</title></head><body><p>"
            + ("long content " * 10)
            + "</p></body></html>"
        )

    async def screenshot(self):
        return b""


class DummyDB:
    def load_cookies(self, domain):
        return None

    def save_cookies(self, domain, cj):
        pass

    def save_discovered_api(self, page_url, api_url, payload_hash):
        pass


class PydanticLike:
    def __init__(self, data):
        self._d = data

    def model_dump(self):
        return self._d


@pytest.mark.asyncio
async def test_scraper_accepts_llm_dict_and_model():
    db = DummyDB()
    adapter = DummyAdapter()

    # LLM returns dict
    async def clean1(self, t):
        return t

    async def extract1(self, h, s):
        return {"a": 1}

    llm1 = type(
        "L1", (), {"clean_text_content": clean1, "extract_structured_data": extract1}
    )()
    scraper1 = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=llm1
    )
    r1 = await scraper1._process_content(
        "http://x", await adapter.get_content(), type("R", (), {"status": 200})()
    )
    assert isinstance(r1, ScrapeResult)

    # LLM returns pydantic-like
    async def clean2(self, t):
        return t

    async def extract2(self, h, s):
        return PydanticLike({"b": 2})

    llm2 = type(
        "L2", (), {"clean_text_content": clean2, "extract_structured_data": extract2}
    )()
    scraper2 = AdvancedScraper(
        db_manager=db, browser_adapter=adapter, llm_extractor=llm2
    )
    r2 = await scraper2._process_content(
        "http://x", await adapter.get_content(), type("R", (), {"status": 200})()
    )
    assert isinstance(r2, ScrapeResult)
    assert isinstance(r2.extracted_data, dict) or r2.extracted_data is None
