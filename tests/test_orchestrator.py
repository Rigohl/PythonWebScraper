import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from src.orchestrator import ScrapingOrchestrator
from src.settings import settings
from src.models.results import ScrapeResult

class TestScrapingOrchestrator(unittest.TestCase):

    def setUp(self):
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
            use_rl=False
        )

    def test_calculate_priority_based_on_depth(self):
        url_root = "http://example.com/page.html"
        url_depth1 = "http://example.com/path1/page.html"
        url_depth2 = "http://example.com/path1/path2/page.html"
        p_root = self.orchestrator._calculate_priority(url_root)
        p_depth1 = self.orchestrator._calculate_priority(url_depth1)
        p_depth2 = self.orchestrator._calculate_priority(url_depth2)
        self.assertLess(p_root, p_depth1)
        self.assertLess(p_depth1, p_depth2)

    def test_has_repetitive_path(self):
        self.assertTrue(self.orchestrator._has_repetitive_path("/a/b/a/b"))
        self.assertTrue(self.orchestrator._has_repetitive_path("/calendar/2023/01/2023/01"))
        self.assertFalse(self.orchestrator._has_repetitive_path("/a/b/c/d"))
        self.assertFalse(self.orchestrator._has_repetitive_path("/a/b/a"))

    def test_update_domain_metrics_and_anomalies(self):
        domain = "example.com"
        self.orchestrator.domain_metrics[domain]["total_scraped"] = 20
        self.orchestrator.domain_metrics[domain]["low_quality"] = 10 # 50% low quality

        with patch.object(self.orchestrator.logger, 'warning') as mock_log:
            self.orchestrator._check_for_anomalies(domain)
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            self.assertIn("Anomalía detectada", call_args)

# Using IsolatedAsyncioTestCase for async methods
class TestOrchestratorAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_db_manager = Mock()
        self.mock_ua_manager = Mock()
        self.mock_llm_extractor = Mock()
        self.mock_rl_agent = Mock()
        self.orchestrator = ScrapingOrchestrator(
            start_urls=["http://example.com"],
            db_manager=self.mock_db_manager,
            user_agent_manager=self.mock_ua_manager,
            llm_extractor=self.mock_llm_extractor,
            rl_agent=self.mock_rl_agent
        )

    @patch('httpx.AsyncClient.head')
    async def test_prequalify_url(self, mock_head):
        # Mock settings for prequalification
        with patch.dict(settings, {"PREQUALIFICATION_ENABLED": True, "ALLOWED_CONTENT_TYPES": ['text/html'], "MAX_CONTENT_LENGTH_BYTES": 1000}):
            # Case 1: Valid URL
            mock_head.return_value = Mock(headers={'content-type': 'text/html', 'content-length': '500'})
            is_qualified, reason = await self.orchestrator._prequalify_url("http://example.com/good")
            self.assertTrue(is_qualified)

            # Case 2: Invalid content type
            mock_head.return_value = Mock(headers={'content-type': 'application/pdf'})
            is_qualified, reason = await self.orchestrator._prequalify_url("http://example.com/bad_type")
            self.assertFalse(is_qualified)
            self.assertIn("Content-Type no permitido", reason)

            # Case 3: Content too large
            mock_head.return_value = Mock(headers={'content-type': 'text/html', 'content-length': '2000'})
            is_qualified, reason = await self.orchestrator._prequalify_url("http://example.com/large")
            self.assertFalse(is_qualified)
            self.assertIn("Content-Length excede el límite", reason)

    async def test_add_links_to_queue(self):
        self.orchestrator.allowed_domain = "example.com"
        self.orchestrator.robot_rules = Mock()
        self.orchestrator.robot_rules.is_allowed.return_value = True

        links = [
            "http://example.com/page1",
            "http://another-domain.com/page2", # Should be filtered out
            "http://example.com/page1", # Should be filtered as seen
            "http://example.com/page3#section" # Should be cleaned and added
        ]

        with patch('src.orchestrator.ScrapingOrchestrator._prequalify_url', new_callable=AsyncMock) as mock_prequalify:
            mock_prequalify.return_value = (True, "")
            await self.orchestrator._add_links_to_queue(links)

            self.assertEqual(self.orchestrator.queue.qsize(), 2)
            # Get items to verify them
            item1 = await self.orchestrator.queue.get()
            item2 = await self.orchestrator.queue.get()
            # URLs are stored as (_, url)
            queued_urls = {item1[1], item2[1]}
            self.assertIn("http://example.com/page1", queued_urls)
            self.assertIn("http://example.com/page3", queued_urls)
