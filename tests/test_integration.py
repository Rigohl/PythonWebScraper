import unittest
import asyncio
import os
import shutil
import tempfile
import threading
import csv
from http.server import HTTPServer, SimpleHTTPRequestHandler

import dataset
from playwright.async_api import async_playwright

from src.orchestrator import ScrapingOrchestrator
from src.database import DatabaseManager
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent

# --- Test Web Server Setup ---
class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Un manejador de peticiones que no imprime logs a la consola."""
    def log_message(self, format, *args):
        pass

def run_server(server):
    """Función para correr el servidor en un hilo."""
    server.serve_forever()

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """Tests de integración que simulan un crawling completo de extremo a extremo."""

    @classmethod
    def setUpClass(cls):
        """Configura un servidor web local para servir archivos de prueba."""
        cls.test_dir = tempfile.mkdtemp()
        cls.server_port = 8089  # Usar un puerto no estándar para evitar conflictos

        # Crear archivos HTML de prueba
        index_html = """
        <html><head><title>Index Page</title></head>
        <body>
            <h1>Welcome</h1>
            <a href="/page1.html">Go to Page 1</a>
            <a href="http://external.com/ignore">External Link</a>
        </body></html>
        """
        page1_html = """
        <html><head><title>Page 1</title></head>
        <body>
            <p>This is page 1.</p>
            <a href="page2.html">Go to Page 2</a>
            <a href="index.html">Go back to Index (should be ignored as seen)</a>
        </body></html>
        """
        page2_html = """
        <html><head><title>Page 2</title></head>
        <body><p>This is page 2, the end.</p></body></html>
        """

        with open(os.path.join(cls.test_dir, "index.html"), "w") as f: f.write(index_html)
        with open(os.path.join(cls.test_dir, "page1.html"), "w") as f: f.write(page1_html)
        with open(os.path.join(cls.test_dir, "page2.html"), "w") as f: f.write(page2_html)

        # Iniciar servidor en un hilo separado
        handler = lambda *args, **kwargs: QuietHTTPRequestHandler(*args, directory=cls.test_dir, **kwargs)
        cls.httpd = HTTPServer(("localhost", cls.server_port), handler)
        cls.server_thread = threading.Thread(target=run_server, args=(cls.httpd,))
        cls.server_thread.daemon = True
        cls.server_thread.start()

        cls.base_url = f"http://localhost:{cls.server_port}"

    @classmethod
    def tearDownClass(cls):
        """Detiene el servidor y limpia los archivos temporales."""
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join()
        shutil.rmtree(cls.test_dir)

    def setUp(self):
        """Configura una nueva BD en memoria y dependencias para cada test."""
        self.db_connection = dataset.connect('sqlite:///:memory:')
        self.db_manager = DatabaseManager(db_connection=self.db_connection)
        self.user_agent_manager = UserAgentManager(user_agents=["TestAgent/1.0"])
        # Usar mocks para LLM y RL ya que no son el foco de este test
        self.llm_extractor = LLMExtractor(api_key="fake")
        self.rl_agent = RLAgent()

    async def test_full_crawl_simulation(self):
        """
        Prueba una simulación de crawling completa en un sitio web local.
        Verifica que todas las páginas alcanzables son visitadas y guardadas.
        """
        start_url = f"{self.base_url}/index.html"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            orchestrator = ScrapingOrchestrator(
                start_urls=[start_url],
                db_manager=self.db_manager,
                user_agent_manager=self.user_agent_manager,
                llm_extractor=self.llm_extractor,
                rl_agent=self.rl_agent,
                concurrency=2
            )

            await orchestrator.run(browser)
            await browser.close()

        # --- Verificaciones ---
        results = list(self.db_manager.table.all())
        self.assertEqual(len(results), 3, "Deberían haberse guardado 3 páginas en la BD.")

        saved_urls = {r['url'] for r in results}
        expected_urls = {
            f"{self.base_url}/index.html",
            f"{self.base_url}/page1.html",
            f"{self.base_url}/page2.html"
        }
        self.assertEqual(saved_urls, expected_urls)

        page1_result = self.db_manager.get_result_by_url(f"{self.base_url}/page1.html")
        self.assertEqual(page1_result['title'], "Page 1")

    async def test_crawl_and_export_csv(self):
        """
        Prueba el flujo completo de crawling y luego exporta los resultados a CSV.
        """
        start_url = f"{self.base_url}/index.html"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            orchestrator = ScrapingOrchestrator(start_urls=[start_url], db_manager=self.db_manager, user_agent_manager=self.user_agent_manager, llm_extractor=self.llm_extractor, rl_agent=self.rl_agent)
            await orchestrator.run(browser)
            await browser.close()

        csv_path = os.path.join(self.test_dir, "integration_export.csv")
        self.db_manager.export_to_csv(csv_path)

        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        self.assertEqual(len(rows), 4, "El CSV debería contener 3 filas de datos más la cabecera.")

if __name__ == '__main__':
    unittest.main()
