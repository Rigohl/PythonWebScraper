import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm():
    class DummyLLM:
        async def clean_text_content(self, text: str) -> str:
            return (text or "").strip()

        async def clean_text_content_async(self, text: str) -> str:
            return (text or "").strip()

        async def extract_structured_data(self, text: str):
            return {"title": "dummy", "items": []}

        async def extract_structured_data_async(self, text: str):
            return {"title": "dummy", "items": []}

    return DummyLLM()


@pytest.fixture
def db_inmemory(tmp_path):
    try:
        from src.database import DatabaseManager
    except Exception:
        pytest.skip("src.database.DatabaseManager not available")
    db_path = tmp_path / "test.db"
    return DatabaseManager(str(db_path))


@pytest.fixture
def mock_adapter():
    class DummyAdapter:
        def __init__(self):
            self.cookies = []
            self.saved_requests = []

        def set_cookies(self, cookies):
            self.cookies = list(cookies)

        def get_cookies(self):
            return list(self.cookies)

        async def navigate(self, url):
            return {"status": 200, "url": url, "content": "<html>ok</html>"}

        def record_request(self, req):
            self.saved_requests.append(req)

    return DummyAdapter()
