import pytest
import asyncio
from unittest.mock import AsyncMock, patch, Mock

from src.runner import run_crawler
from src.orchestrator import ScrapingOrchestrator
from src.database import DatabaseManager
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent
from src.frontier_classifier import FrontierClassifier

@pytest.fixture
def mock_orchestrator_init():
    with patch('src.orchestrator.ScrapingOrchestrator.__init__', return_value=None) as mock_init:
        yield mock_init

@pytest.fixture
def mock_orchestrator_run():
    with patch('src.orchestrator.ScrapingOrchestrator.run', new_callable=AsyncMock) as mock_run:
        yield mock_run

@pytest.fixture
def mock_async_playwright():
    with patch('playwright.async_api.async_playwright') as mock_pw:
        mock_pw_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser
        mock_pw.return_value.__aenter__.return_value = mock_pw_instance
        yield mock_pw

@pytest.mark.asyncio
async def test_run_crawler_basic_execution(mock_orchestrator_init, mock_orchestrator_run, mock_async_playwright):
    start_urls = ["http://test.com"]
    db_path = "test.db"
    concurrency = 5
    respect_robots_txt = True
    use_rl = False

    await run_crawler(
        start_urls=start_urls,
        db_path=db_path,
        concurrency=concurrency,
        respect_robots_txt=respect_robots_txt,
        use_rl=use_rl
    )

    # Verify ScrapingOrchestrator was initialized correctly
    mock_orchestrator_init.assert_called_once()
    args, kwargs = mock_orchestrator_init.call_args
    assert kwargs['start_urls'] == start_urls
    assert isinstance(kwargs['db_manager'], DatabaseManager)
    assert isinstance(kwargs['user_agent_manager'], UserAgentManager)
    assert isinstance(kwargs['llm_extractor'], LLMExtractor)
    assert kwargs['rl_agent'] is None
    assert kwargs['concurrency'] == concurrency
    assert kwargs['respect_robots_txt'] == respect_robots_txt
    assert kwargs['use_rl'] == use_rl

    # Verify Playwright was launched and browser closed
    mock_async_playwright.assert_called_once()
    mock_async_playwright.return_value.__aenter__.return_value.chromium.launch.assert_called_once_with(headless=True)
    mock_async_playwright.return_value.__aenter__.return_value.chromium.launch.return_value.close.assert_called_once()

    # Verify orchestrator.run was called
    mock_orchestrator_run.assert_called_once()
    assert mock_orchestrator_run.call_args[0][0] is mock_async_playwright.return_value.__aenter__.return_value.chromium.launch.return_value

@pytest.mark.asyncio
async def test_run_crawler_with_rl(mock_orchestrator_init, mock_orchestrator_run, mock_async_playwright):
    start_urls = ["http://test.com"]
    db_path = "test.db"
    concurrency = 5
    respect_robots_txt = True
    use_rl = True

    await run_crawler(
        start_urls=start_urls,
        db_path=db_path,
        concurrency=concurrency,
        respect_robots_txt=respect_robots_txt,
        use_rl=use_rl
    )

    # Verify RLAgent was initialized and passed to orchestrator
    mock_orchestrator_init.assert_called_once()
    args, kwargs = mock_orchestrator_init.call_args
    assert isinstance(kwargs['rl_agent'], RLAgent)
    assert kwargs['use_rl'] == use_rl

@pytest.mark.asyncio
async def test_run_crawler_browser_close_on_exception(mock_orchestrator_init, mock_orchestrator_run, mock_async_playwright):
    mock_orchestrator_run.side_effect = Exception("Orchestrator failed")

    start_urls = ["http://test.com"]
    db_path = "test.db"
    concurrency = 5
    respect_robots_txt = True
    use_rl = False

    with pytest.raises(Exception, match="Orchestrator failed"):
        await run_crawler(
            start_urls=start_urls,
            db_path=db_path,
            concurrency=concurrency,
            respect_robots_txt=respect_robots_txt,
            use_rl=use_rl
        )

    # Verify browser.close() is still called even if orchestrator.run fails
    mock_async_playwright.return_value.__aenter__.return_value.chromium.launch.return_value.close.assert_called_once()
