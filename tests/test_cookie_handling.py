import pytest

from src.scraper import AdvancedScraper


class DummyDB:
    def __init__(self):
        self.cookies = {}
        self.cookies_saved = False

    def load_cookies(self, domain):
        return self.cookies.get(domain)

    def save_cookies(self, domain, cookies):
        self.cookies[domain] = cookies
        self.cookies_saved = True


class DummyAdapter:
    def __init__(self):
        self.cookies_set = False
        self.cookies_data = {}

    async def set_cookies(self, cookies):
        self.cookies_set = True
        self.cookies_data = cookies

    async def get_cookies(self):
        return self.cookies_data


class DummyLLM:
    async def clean_text_content(self, text):
        return text

    async def extract_structured_data(self, html, schema):
        return {}


@pytest.mark.asyncio
async def test_apply_cookies_loads_and_sets_from_db():
    """Validar que _apply_cookies() carga cookies del db_manager y las setea en el adapter"""
    db = DummyDB()
    adapter = DummyAdapter()
    llm = DummyLLM()

    # Simular cookies existentes en DB
    test_cookies = [{"name": "session", "value": "abc123", "domain": "example.com"}]
    db.cookies["example.com"] = test_cookies

    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    await scraper._apply_cookies("example.com")

    # Verificar que adapter.set_cookies fue llamado
    assert adapter.cookies_set is True
    assert adapter.cookies_data == test_cookies


@pytest.mark.asyncio
async def test_persist_cookies_saves_when_modified():
    """Validar que _persist_cookies() guarda cookies cuando cookies_were_set es True"""
    db = DummyDB()
    adapter = DummyAdapter()
    llm = DummyLLM()

    # Simular que cookies fueron modificadas
    adapter.cookies_were_set = True
    new_cookies = [{"name": "new_session", "value": "xyz789", "domain": "example.com"}]
    adapter.cookies_data = new_cookies

    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    await scraper._persist_cookies("example.com")

    # Verificar que db_manager.save_cookies fue llamado
    assert db.cookies_saved is True
    assert db.cookies["example.com"] == new_cookies


@pytest.mark.asyncio
async def test_cookie_workflow_integration():
    """Test completo del workflow de cookies: cargar -> usar -> persistir"""
    db = DummyDB()
    adapter = DummyAdapter()
    llm = DummyLLM()

    # 1. Cargar cookies iniciales
    initial_cookies = [{"name": "initial", "value": "value1", "domain": "example.com"}]
    db.cookies["example.com"] = initial_cookies

    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    # 2. Aplicar cookies (debería cargar del DB)
    await scraper._apply_cookies("example.com")
    assert adapter.cookies_set is True
    assert adapter.cookies_data == initial_cookies

    # 3. Simular modificación de cookies durante scraping
    adapter.cookies_were_set = True
    modified_cookies = [
        {"name": "modified", "value": "value2", "domain": "example.com"}
    ]
    adapter.cookies_data = modified_cookies

    # 4. Persistir cookies (debería guardar en DB)
    await scraper._persist_cookies("example.com")
    assert db.cookies_saved is True
    assert db.cookies["example.com"] == modified_cookies
