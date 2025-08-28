import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import urlparse, urlunparse

from playwright.async_api import Browser, Page, Response
import httpx

from src.orchestrator import ScrapingOrchestrator
from src.database import DatabaseManager
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent
from src.frontier_classifier import FrontierClassifier
from src.models.results import ScrapeResult
from src.settings import settings
from pydantic import BaseModel

# Define a custom exception for network errors
class NetworkError(Exception):
    pass

# Fixtures for mocked dependencies
@pytest.fixture
def mock_browser():
    return AsyncMock(spec=Browser)

@pytest.fixture
def mock_page_orchestrator():
    mock = AsyncMock(spec=Page)
    mock.context = AsyncMock()
    mock.context.cookies.return_value = []
    yield mock

@pytest.fixture
def mock_db_manager_orchestrator():
    mock = Mock(spec=DatabaseManager)
    mock.load_cookies.return_value = None
    mock.save_discovered_api.return_value = None
    mock.save_cookies.return_value = None
    mock.save_llm_extraction_schema.return_value = None
    mock.load_llm_extraction_schema.return_value = None
    mock.save_result.return_value = None
    mock.get_result_by_url.return_value = None
    yield mock

@pytest.fixture
def mock_user_agent_manager_orchestrator():
    mock = Mock(spec=UserAgentManager)
    mock.get_user_agent.return_value = "Test-Agent"
    mock.release_user_agent.return_value = None
    mock.block_user_agent.return_value = None
    yield mock

@pytest.fixture
def mock_llm_extractor_orchestrator():
    mock = AsyncMock(spec=LLMExtractor)
    mock.clean_text_content.side_effect = lambda x: x
    mock.extract_structured_data.return_value = None
    mock.summarize_content.return_value = "Summary"
    yield mock

@pytest.fixture
def mock_rl_agent_orchestrator():
    mock = Mock(spec=RLAgent)
    mock.get_action.return_value = {"adjust_backoff_factor": 1.0}
    mock.learn.return_value = None
    mock.save_model.return_value = None
    yield mock

@pytest.fixture
def mock_frontier_classifier_orchestrator():
    mock = Mock(spec=FrontierClassifier)
    mock.predict.return_value = 0.5 # Default promise score
    yield mock

# Patch external dependencies for Orchestrator tests
@pytest.fixture(autouse=True)
def patch_orchestrator_external_deps(mock_page_orchestrator):
    with (
        patch('playwright_stealth.Stealth.use_async', new=AsyncMock(return_value=AsyncMock())),
        patch('src.scraper.AdvancedScraper', new=Mock(return_value=AsyncMock())), # Mock the class itself
        patch('httpx.AsyncClient', new=Mock()),
        patch('src.orchestrator.urlparse', wraps=urlparse) as mock_urlparse,
        patch('src.orchestrator.urlunparse', wraps=urlunparse) as mock_urlunparse,
    ):
        # Configure the mock AdvancedScraper to return a successful result by default
        mock_scraper_instance = AsyncMock()
        mock_scraper_instance.scrape.return_value = ScrapeResult(status="SUCCESS", url="http://test.com", title="Test", content_text="Content")

        # Patch the AdvancedScraper class to return our configured mock instance
        with patch('src.scraper.AdvancedScraper', return_value=mock_scraper_instance) as mock_AdvancedScraper_class:
            yield

@pytest.fixture
def orchestrator(mock_db_manager_orchestrator, mock_user_agent_manager_orchestrator, mock_llm_extractor_orchestrator, mock_rl_agent_orchestrator, mock_frontier_classifier_orchestrator):
    return ScrapingOrchestrator(
        start_urls=["http://example.com"],
        db_manager=mock_db_manager_orchestrator,
        user_agent_manager=mock_user_agent_manager_orchestrator,
        llm_extractor=mock_llm_extractor_orchestrator,
        rl_agent=mock_rl_agent_orchestrator,
        frontier_classifier=mock_frontier_classifier_orchestrator,
        use_rl=False,
        stats_callback=Mock(),
        alert_callback=Mock()
    )

@pytest.mark.asyncio
async def test_orchestrator_init(orchestrator):
    assert orchestrator.concurrency == settings.CONCURRENCY
    assert orchestrator.start_urls == ["http://example.com"]
    assert orchestrator.db_manager is not None
    assert orchestrator.queue.empty()
    assert not orchestrator.seen_urls

@pytest.mark.asyncio
async def test_orchestrator_init_with_rl_agent(mock_db_manager_orchestrator, mock_user_agent_manager_orchestrator, mock_llm_extractor_orchestrator, mock_rl_agent_orchestrator, mock_frontier_classifier_orchestrator):
    orchestrator_rl = ScrapingOrchestrator(
        start_urls=["http://example.com"],
        db_manager=mock_db_manager_orchestrator,
        user_agent_manager=mock_user_agent_manager_orchestrator,
        llm_extractor=mock_llm_extractor_orchestrator,
        rl_agent=mock_rl_agent_orchestrator,
        frontier_classifier=mock_frontier_classifier_orchestrator,
        use_rl=True
    )
    assert orchestrator_rl.use_rl is True
    assert orchestrator_rl.rl_agent is mock_rl_agent_orchestrator

@pytest.mark.asyncio
async def test_orchestrator_init_rl_agent_missing_when_use_rl_true(mock_db_manager_orchestrator, mock_user_agent_manager_orchestrator, mock_llm_extractor_orchestrator, mock_frontier_classifier_orchestrator):
    with pytest.raises(ValueError, match="RLAgent must be provisto cuando use_rl es True."):
        ScrapingOrchestrator(
            start_urls=["http://example.com"],
            db_manager=mock_db_manager_orchestrator,
            user_agent_manager=mock_user_agent_manager_orchestrator,
            llm_extractor=mock_llm_extractor_orchestrator,
            frontier_classifier=mock_frontier_classifier_orchestrator,
            rl_agent=None,
            use_rl=True
        )

@pytest.mark.asyncio
async def test_calculate_priority(orchestrator, mock_frontier_classifier_orchestrator):
    mock_frontier_classifier_orchestrator.predict.return_value = 0.8 # High promise
    priority = orchestrator._calculate_priority("http://example.com/path/to/page")
    # path_depth = 2, promise_score = 0.8. priority = 2 + (-5 * 0.8) = 2 - 4 = -2
    assert priority == -2

    mock_frontier_classifier_orchestrator.predict.return_value = 0.1 # Low promise
    priority = orchestrator._calculate_priority("http://example.com/path/to/page")
    # path_depth = 2, promise_score = 0.1. priority = 2 + (-5 * 0.1) = 2 - 0.5 = 1.5 -> 1
    assert priority == 1

@pytest.mark.asyncio
async def test_has_repetitive_path(orchestrator):
    settings.REPETITIVE_PATH_THRESHOLD = 2
    assert orchestrator._has_repetitive_path("http://example.com/a/b/a/b") is True
    assert orchestrator._has_repetitive_path("http://example.com/calendar/2023/01/2023/01") is True
    assert orchestrator._has_repetitive_path("http://example.com/a/b/c/d") is False
    assert orchestrator._has_repetitive_path("http://example.com/a/b/a") is False # Not enough segments for 2*threshold

@pytest.mark.asyncio
async def test_prequalify_url_success(orchestrator, monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'text/html', 'content-length': '500'}
    mock_response.history = [] # No redirects

    mock_httpx_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(httpx.AsyncClient, "head", mock_httpx_get)

    is_qualified, reason = await orchestrator._prequalify_url("http://example.com/good")
    assert is_qualified is True
    assert reason == "OK"

@pytest.mark.asyncio
async def test_prequalify_url_invalid_content_type(orchestrator, monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'application/pdf'}
    mock_response.history = []

    mock_httpx_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(httpx.AsyncClient, "head", mock_httpx_get)

    is_qualified, reason = await orchestrator._prequalify_url("http://example.com/bad_type")
    assert is_qualified is False
    assert "Tipo de contenido no permitido" in reason

@pytest.mark.asyncio
async def test_prequalify_url_too_many_redirects(orchestrator, monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'content-type': 'text/html'}
    mock_response.history = [Mock() for _ in range(settings.MAX_REDIRECTS + 1)] # Exceed max redirects

    mock_httpx_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(httpx.AsyncClient, "head", mock_httpx_get)

    is_qualified, reason = await orchestrator._prequalify_url("http://example.com/redirect_loop")
    assert is_qualified is False
    assert "Exceso de redirecciones" in reason

@pytest.mark.asyncio
async def test_prequalify_url_network_error(orchestrator, monkeypatch):
    monkeypatch.setattr(httpx.AsyncClient, "head", AsyncMock(side_effect=httpx.RequestError("Connection refused", request=Mock())))

    is_qualified, reason = await orchestrator._prequalify_url("http://example.com/error")
    assert is_qualified is False
    assert "Error de red" in reason

@pytest.mark.asyncio
async def test_block_unnecessary_requests_blocked(orchestrator, mock_page_orchestrator):
    mock_route = AsyncMock()
    mock_route.request.resource_type = "image"
    await orchestrator._block_unnecessary_requests(mock_route)
    mock_route.abort.assert_called_once()
    mock_route.continue_.assert_not_called()

@pytest.mark.asyncio
async def test_block_unnecessary_requests_allowed(orchestrator, mock_page_orchestrator):
    mock_route = AsyncMock()
    mock_route.request.resource_type = "document"
    await orchestrator._block_unnecessary_requests(mock_route)
    mock_route.abort.assert_not_called()
    mock_route.continue_.assert_called_once()

@pytest.mark.asyncio
async def test_add_links_to_queue(orchestrator, mock_frontier_classifier_orchestrator, monkeypatch):
    orchestrator.allowed_domain = "example.com"
    orchestrator.robot_rules = Mock()
    orchestrator.robot_rules.is_allowed.return_value = True

    links = [
        "http://example.com/page1",
        "http://another-domain.com/page2", # Should be filtered out
        "http://example.com/page1#section", # Should be cleaned and filtered as seen
        "http://example.com/page3?query=test", # Should be cleaned and added
        "http://example.com/a/b/a/b" # Repetitive path, should be filtered
    ]

    # Mock _prequalify_url to always return True for valid links
    monkeypatch.setattr(orchestrator, "_prequalify_url", AsyncMock(return_value=(True, "OK")))
    monkeypatch.setattr(orchestrator, "_has_repetitive_path", Mock(side_effect=lambda x: "/a/b/a/b" in x))

    await orchestrator._add_links_to_queue(links)

    assert orchestrator.queue.qsize() == 2
    queued_urls = set()
    for _ in range(orchestrator.queue.qsize()):
        _, url = await orchestrator.queue.get()
        queued_urls.add(url)

    assert "http://example.com/page1" in queued_urls
    assert "http://example.com/page3" in queued_urls
    assert "http://another-domain.com/page2" not in queued_urls
    assert "http://example.com/a/b/a/b" not in queued_urls

@pytest.mark.asyncio
async def test_run_no_start_urls(orchestrator):
    orchestrator.start_urls = []
    await orchestrator.run(AsyncMock())
    orchestrator.alert_callback.assert_called_once_with("No se proporcionaron URLs iniciales para el crawling.", level="error")

@pytest.mark.asyncio
async def test_run_fetches_robots_txt(orchestrator, mock_browser, monkeypatch):
    orchestrator.respect_robots_txt = True
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "User-agent: *\nDisallow: /admin"
    mock_httpx_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    await orchestrator.run(mock_browser)
    mock_httpx_get.assert_called_once()
    assert orchestrator.robot_rules is not None
    assert orchestrator.robot_rules.is_allowed("User-agent: *", "http://example.com/admin") is False

@pytest.mark.asyncio
async def test_run_skips_robots_txt(orchestrator, mock_browser, monkeypatch):
    orchestrator.respect_robots_txt = False
    mock_httpx_get = AsyncMock()
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    await orchestrator.run(mock_browser)
    mock_httpx_get.assert_not_called()
    orchestrator.alert_callback.assert_called_once_with("La comprobación de robots.txt está desactivada.", level="warning")

@pytest.mark.asyncio
async def test_worker_success(orchestrator, mock_browser, mock_page_orchestrator, mock_db_manager_orchestrator, mock_llm_extractor_orchestrator, mock_user_agent_manager_orchestrator, monkeypatch):
    # Mock page creation and scraper instance
    mock_browser.new_page.return_value = mock_page_orchestrator
    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.scrape.return_value = ScrapeResult(status="SUCCESS", url="http://test.com/page", content_text="Test content")
    monkeypatch.setattr('src.scraper.AdvancedScraper', Mock(return_value=mock_scraper_instance))

    orchestrator.queue.put_nowait((1, "http://test.com/page"))

    # Run one iteration of the worker
    await asyncio.wait_for(orchestrator._worker(mock_browser, 1), timeout=1)

    mock_browser.new_page.assert_called_once()
    mock_user_agent_manager_orchestrator.get_user_agent.assert_called_once()
    mock_scraper_instance.scrape.assert_called_once_with("http://test.com/page", extraction_schema=None)
    mock_db_manager_orchestrator.save_result.assert_called_once()
    mock_llm_extractor_orchestrator.summarize_content.assert_called_once()
    orchestrator.stats_callback.assert_called_once()
    mock_user_agent_manager_orchestrator.release_user_agent.assert_called_once()
    mock_page_orchestrator.close.assert_called_once()

@pytest.mark.asyncio
async def test_worker_network_error_retry(orchestrator, mock_browser, mock_page_orchestrator, mock_db_manager_orchestrator, mock_llm_extractor_orchestrator, mock_user_agent_manager_orchestrator, monkeypatch):
    mock_browser.new_page.return_value = mock_page_orchestrator
    mock_scraper_instance = AsyncMock()
    # First scrape attempt fails with NetworkError, second succeeds
    mock_scraper_instance.scrape.side_effect = [NetworkError("Connection lost"), ScrapeResult(status="SUCCESS", url="http://test.com/page", content_text="Test content")]
    monkeypatch.setattr('src.scraper.AdvancedScraper', Mock(return_value=mock_scraper_instance))

    orchestrator.queue.put_nowait((1, "http://test.com/page"))

    await asyncio.wait_for(orchestrator._worker(mock_browser, 1), timeout=5) # Increased timeout for sleep

    assert mock_scraper_instance.scrape.call_count == 2
    mock_db_manager_orchestrator.save_result.assert_called_once()
    orchestrator.stats_callback.assert_called_once()
    mock_user_agent_manager_orchestrator.release_user_agent.assert_called_once()

@pytest.mark.asyncio
async def test_worker_network_error_max_retries(orchestrator, mock_browser, mock_page_orchestrator, mock_db_manager_orchestrator, mock_llm_extractor_orchestrator, mock_user_agent_manager_orchestrator, monkeypatch):
    mock_browser.new_page.return_value = mock_page_orchestrator
    mock_scraper_instance = AsyncMock()
    # All scrape attempts fail with NetworkError
    mock_scraper_instance.scrape.side_effect = [NetworkError("Connection lost")] * (settings.MAX_RETRIES + 1)
    monkeypatch.setattr('src.scraper.AdvancedScraper', Mock(return_value=mock_scraper_instance))

    orchestrator.queue.put_nowait((1, "http://test.com/page"))

    await asyncio.wait_for(orchestrator._worker(mock_browser, 1), timeout=10) # Increased timeout for sleep

    assert mock_scraper_instance.scrape.call_count == settings.MAX_RETRIES + 1
    mock_db_manager_orchestrator.save_result.assert_called_once() # Result with status RETRY is saved
    orchestrator.alert_callback.assert_called_once_with("Fallo de red persistente para http://test.com/page. Descartando.", level="error")
    mock_user_agent_manager_orchestrator.block_user_agent.assert_called_once()

@pytest.mark.asyncio
async def test_worker_unexpected_exception(orchestrator, mock_browser, mock_page_orchestrator, mock_db_manager_orchestrator, mock_llm_extractor_orchestrator, mock_user_agent_manager_orchestrator, monkeypatch):
    mock_browser.new_page.return_value = mock_page_orchestrator
    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.scrape.side_effect = Exception("Unexpected error")
    monkeypatch.setattr('src.scraper.AdvancedScraper', Mock(return_value=mock_scraper_instance))

    orchestrator.queue.put_nowait((1, "http://test.com/page"))

    await asyncio.wait_for(orchestrator._worker(mock_browser, 1), timeout=1)

    mock_db_manager_orchestrator.save_result.assert_called_once() # Result with status FAILED is saved
    orchestrator.alert_callback.assert_called_once_with("Error inesperado al procesar http://test.com/page: Unexpected error", level="error")
    mock_user_agent_manager_orchestrator.block_user_agent.assert_called_once()

@pytest.mark.asyncio
async def test_worker_dynamic_llm_schema_loading(orchestrator, mock_browser, mock_page_orchestrator, mock_db_manager_orchestrator, mock_llm_extractor_orchestrator, mock_user_agent_manager_orchestrator, monkeypatch):
    mock_browser.new_page.return_value = mock_page_orchestrator
    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.scrape.return_value = ScrapeResult(status="SUCCESS", url="http://test.com/page", content_text="Test content")
    monkeypatch.setattr('src.scraper.AdvancedScraper', Mock(return_value=mock_scraper_instance))

    # Mock a stored LLM schema
    mock_db_manager_orchestrator.load_llm_extraction_schema.return_value = json.dumps({"name": [str, ...], "price": [float, ...]})

    orchestrator.queue.put_nowait((1, "http://test.com/page"))

    await asyncio.wait_for(orchestrator._worker(mock_browser, 1), timeout=1)

    # Verify that scrape was called with the dynamically created schema
    args, kwargs = mock_scraper_instance.scrape.call_args
    assert "extraction_schema" in kwargs
    assert issubclass(kwargs["extraction_schema"], BaseModel) # Check if it's a Pydantic model
    assert hasattr(kwargs["extraction_schema"], "name")
    assert hasattr(kwargs["extraction_schema"], "price")

@pytest.mark.asyncio
async def test_update_domain_metrics(orchestrator):
    orchestrator._update_domain_metrics(ScrapeResult(status="SUCCESS", url="http://example.com/1"))
    orchestrator._update_domain_metrics(ScrapeResult(status="LOW_QUALITY", url="http://example.com/2"))
    orchestrator._update_domain_metrics(ScrapeResult(status="FAILED", url="http://example.com/3"))

    metrics = orchestrator.domain_metrics["example.com"]
    assert metrics["total_scraped"] == 3
    assert metrics["low_quality"] == 1
    assert metrics["failed"] == 1
    orchestrator.stats_callback.assert_called_with({
        "processed": 1,
        "queue_size": 0, # Queue is empty after processing
        "status": "FAILED", # Last status processed
        "domain_metrics": orchestrator.domain_metrics
    })

@pytest.mark.asyncio
async def test_check_for_anomalies_increase_backoff(orchestrator):
    domain = "example.com"
    orchestrator.domain_metrics[domain]["total_scraped"] = 20
    orchestrator.domain_metrics[domain]["low_quality"] = 10 # 50% low quality
    orchestrator.domain_metrics[domain]["empty"] = 0
    orchestrator.domain_metrics[domain]["current_backoff_factor"] = 1.0

    orchestrator._check_for_anomalies(domain)
    assert orchestrator.domain_metrics[domain]["current_backoff_factor"] == 1.5 # 1.0 * 1.5
    orchestrator.alert_callback.assert_called_once()
    assert "Anomalía detectada" in orchestrator.alert_callback.call_args[0][0]

@pytest.mark.asyncio
async def test_check_for_anomalies_decrease_backoff(orchestrator):
    domain = "example.com"
    orchestrator.domain_metrics[domain]["total_scraped"] = 20
    orchestrator.domain_metrics[domain]["low_quality"] = 1 # 5% low quality
    orchestrator.domain_metrics[domain]["empty"] = 0
    orchestrator.domain_metrics[domain]["current_backoff_factor"] = 2.0

    orchestrator._check_for_anomalies(domain)
    assert orchestrator.domain_metrics[domain]["current_backoff_factor"] == pytest.approx(2.0 / 1.2) # 2.0 / 1.2
    orchestrator.alert_callback.assert_not_called()

@pytest.mark.asyncio
async def test_check_for_visual_changes_alert(orchestrator, mock_db_manager_orchestrator, monkeypatch):
    new_result = ScrapeResult(status="SUCCESS", url="http://test.com", visual_hash="hash_new")
    old_result_data = {'url': "http://test.com", 'visual_hash': "hash_old"}
    mock_db_manager_orchestrator.get_result_by_url.return_value = old_result_data

    mock_old_hash = Mock()
    mock_new_hash = Mock()
    mock_old_hash.__sub__.return_value = settings.VISUAL_CHANGE_THRESHOLD + 1 # Distance exceeds threshold
    monkeypatch.setattr('imagehash.hex_to_hash', lambda x: mock_old_hash if x == "hash_old" else mock_new_hash)

    orchestrator._check_for_visual_changes(new_result)
    orchestrator.alert_callback.assert_called_once()
    assert "ALERTA DE REDISEÑO" in orchestrator.alert_callback.call_args[0][0]

@pytest.mark.asyncio
async def test_fetch_robot_rules_success(orchestrator, monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "User-agent: *\nDisallow: /admin"
    mock_httpx_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    orchestrator.start_urls = ["http://example.com"]
    orchestrator.allowed_domain = "example.com"

    await orchestrator._fetch_robot_rules()
    mock_httpx_get.assert_called_once_with("http://example.com/robots.txt", follow_redirects=True)
    assert orchestrator.robot_rules is not None
    assert orchestrator.robot_rules.is_allowed("User-agent: *", "http://example.com/admin") is False

@pytest.mark.asyncio
async def test_fetch_robot_rules_failure(orchestrator, monkeypatch):
    mock_httpx_get = AsyncMock(side_effect=httpx.RequestError("Connection refused", request=Mock()))
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    orchestrator.start_urls = ["http://example.com"]
    orchestrator.allowed_domain = "example.com"

    await orchestrator._fetch_robot_rules()
    orchestrator.alert_callback.assert_called_once()
    assert "Error al cargar/parsear robots.txt" in orchestrator.alert_callback.call_args[0][0]

@pytest.mark.asyncio
async def test_rl_agent_integration_apply_actions(orchestrator, mock_rl_agent_orchestrator):
    orchestrator.use_rl = True
    domain = "test.com"
    orchestrator.domain_metrics[domain]["current_backoff_factor"] = 1.0
    mock_rl_agent_orchestrator.get_action.return_value = {"adjust_backoff_factor": 1.5}

    await orchestrator._apply_rl_actions(domain)

    mock_rl_agent_orchestrator.get_action.assert_called_once()
    assert orchestrator.domain_metrics[domain]["current_backoff_factor"] == 1.5
    assert orchestrator.domain_metrics[domain]["last_state_dict"] is not None
    assert orchestrator.domain_metrics[domain]["last_action_dict"] == {"adjust_backoff_factor": 1.5}

@pytest.mark.asyncio
async def test_rl_agent_integration_perform_learning(orchestrator, mock_rl_agent_orchestrator):
    orchestrator.use_rl = True
    domain = "test.com"
    # Set up previous state and action for learning
    orchestrator.domain_metrics[domain]["last_state_dict"] = {"low_quality_ratio": 0.1, "failure_ratio": 0.1, "current_backoff": 1.0}
    orchestrator.domain_metrics[domain]["last_action_dict"] = {"adjust_backoff_factor": 1.0}

    result = ScrapeResult(status="SUCCESS", url="http://test.com/page")
    orchestrator._perform_rl_learning(result)

    mock_rl_agent_orchestrator.learn.assert_called_once()
    args, kwargs = mock_rl_agent_orchestrator.learn.call_args
    assert args[0] == {"low_quality_ratio": 0.1, "failure_ratio": 0.1, "current_backoff": 1.0}
    assert args[1] == {"adjust_backoff_factor": 1.0}
    assert args[2] == 1.0 # Reward for SUCCESS
    assert args[3] == {"low_quality_ratio": 0.0, "failure_ratio": 0.0, "current_backoff": 1.0} # Next state

    assert orchestrator.domain_metrics[domain]["last_state_dict"] is None
    assert orchestrator.domain_metrics[domain]["last_action_dict"] is None
