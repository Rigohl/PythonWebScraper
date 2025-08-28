import unittest
from unittest.mock import Mock, patch
from src.orchestrator import ScrapingOrchestrator
from src import config

class TestScrapingOrchestrator(unittest.TestCase):

    def setUp(self):
        # Mock (simular) las dependencias para probar el orquestador de forma aislada
        self.mock_db_manager = Mock()
        self.mock_ua_manager = Mock()
        self.mock_llm_extractor = Mock()
        self.mock_rl_agent = Mock()

        self.orchestrator = ScrapingOrchestrator(
            start_urls=["http://example.com"],
            db_manager=self.mock_db_manager,
            user_agent_manager=self.mock_ua_manager,
            llm_extractor=self.mock_llm_extractor,
            rl_agent=self.mock_rl_agent,
            use_rl=False # Desactivar RL para tests unitarios
        )

    def test_calculate_priority_based_on_depth(self):
        """Prueba que la prioridad es mayor (número más bajo) para URLs menos profundas."""
        # Un número más bajo significa mayor prioridad
        url_root = "http://example.com/page.html"
        url_depth1 = "http://example.com/path1/page.html"
        url_depth2 = "http://example.com/path1/path2/page.html"

        p_root = self.orchestrator._calculate_priority(url_root)
        p_depth1 = self.orchestrator._calculate_priority(url_depth1)
        p_depth2 = self.orchestrator._calculate_priority(url_depth2)

        self.assertLess(p_root, p_depth1, "La raíz debe tener más prioridad que la profundidad 1")
        self.assertLess(p_depth1, p_depth2, "La profundidad 1 debe tener más prioridad que la profundidad 2")

    @patch.dict(config.CONTENT_TYPE_PRIORITIES, {
        "HTML": 5,
        "PDF": 2,      # Mayor prioridad (número más bajo)
        "IMAGE": 10,   # Menor prioridad
        "UNKNOWN": 5
    })
    def test_calculate_priority_based_on_content_type(self):
        """Prueba que la prioridad cambia según el tipo de contenido del padre."""
        url = "http://example.com/path1/page.html"

        p_html = self.orchestrator._calculate_priority(url, "HTML")
        p_pdf = self.orchestrator._calculate_priority(url, "PDF")
        p_image = self.orchestrator._calculate_priority(url, "IMAGE")

        self.assertLess(p_pdf, p_html, "Los enlaces de un PDF deben tener más prioridad que los de un HTML")
        self.assertLess(p_html, p_image, "Los enlaces de un HTML deben tener más prioridad que los de una imagen")
