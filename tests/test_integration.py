import asyncio
import os
import tempfile
import csv

from urllib.parse import urlparse
import dataset
from playwright.async_api import async_playwright

from src.orchestrator import ScrapingOrchestrator
from src.database import DatabaseManager
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent
from src.settings import settings
import pytest

class TestIntegration:
    """Tests de integración que simulan un crawling completo de extremo a extremo."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configura una nueva BD en memoria y dependencias para cada test."""
        self.db_connection = dataset.connect('sqlite:///:memory:')
        self.db_manager = DatabaseManager(db_connection=self.db_connection)
        self.user_agent_manager = UserAgentManager(user_agents=["TestAgent/1.0"])
        self.llm_extractor = LLMExtractor()

    @pytest.mark.asyncio
    async def test_full_crawl_simulation(self, http_server):
        """
        Prueba una simulación de crawling completa en un sitio web local.
        Verifica que todas las páginas alcanzables son visitadas y guardadas.
        """
        start_url = f"{http_server}/index.html"
        # Corregir la inicialización para que coincida con la TUI
        rl_agent = RLAgent(model_path=settings.RL_MODEL_PATH)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            orchestrator = ScrapingOrchestrator(
                start_urls=[start_url],
                db_manager=self.db_manager,
                user_agent_manager=self.user_agent_manager,
                llm_extractor=self.llm_extractor,
                rl_agent=rl_agent,
                concurrency=2
            )

            await orchestrator.run(browser)
            await browser.close()

        # --- Verificaciones ---
        results = list(self.db_manager.table.all())
        assert len(results) == 3, "Deberían haberse guardado 3 páginas en la BD."

        saved_urls = {r['url'] for r in results}
        expected_urls = {
            f"{http_server}/index.html",
            f"{http_server}/page1.html",
            f"{http_server}/page2.html"
        }
        assert saved_urls == expected_urls

        page1_result = self.db_manager.get_result_by_url(f"{http_server}/page1.html")
        assert page1_result['title'] == "Page 1"

    @pytest.mark.asyncio
    async def test_duplicate_content_is_not_reprocessed(self, http_server):
        """
        Verifica que si dos URLs tienen el mismo contenido, la segunda se marca
        como DUPLICATE y sus enlaces no se añaden a la cola.
        El servidor de prueba tiene /page1.html y /page1_clone.html con idéntico contenido.
        """
        start_url = f"{http_server}/index_with_clone.html"
        rl_agent = RLAgent(model_path=settings.RL_MODEL_PATH)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            orchestrator = ScrapingOrchestrator(
                start_urls=[start_url],
                db_manager=self.db_manager,
                user_agent_manager=self.user_agent_manager,
                llm_extractor=self.llm_extractor,
                rl_agent=rl_agent,
                concurrency=2
            )
            await orchestrator.run(browser)
            await browser.close()

        # Se deben procesar 3 URLs: index, page1, y page1_clone. page2 no debe ser alcanzada.
        results = list(self.db_manager.table.all())
        assert len(results) == 3, "Deberían haberse procesado 3 URLs."
        clone_result = self.db_manager.get_result_by_url(f"{http_server}/page1_clone.html")
        assert clone_result['status'] == 'DUPLICATE', "La página clonada debería marcarse como duplicada."
