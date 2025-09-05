"""Crawler execution runner with dependency injection and proper error handling."""

import logging
from typing import Callable, Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright

from .database import DatabaseManager
from .llm_extractor import LLMExtractor
from .orchestrator import ScrapingOrchestrator
from .rl_agent import RLAgent
from .settings import settings
from .user_agent_manager import UserAgentManager


def validate_inputs(start_urls: list[str], db_path: str, concurrency: int) -> None:
    """Validate input parameters for the crawler."""
    if not start_urls:
        raise ValueError("At least one start URL must be provided.")

    for url in start_urls:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")

    if concurrency <= 0:
        raise ValueError("Concurrency must be a positive integer.")

    if not db_path:
        raise ValueError("Database path cannot be empty.")


async def run_crawler(
    start_urls: list[str],
    db_path: str,
    concurrency: int,
    respect_robots_txt: bool,
    use_rl: bool,
    stats_callback: Optional[Callable] = None,
    alert_callback: Optional[Callable] = None,
) -> None:
    """
    Set up and run the crawler with proper dependency injection.

    This function orchestrates the complete crawling process by:
    1. Initializing all required components (database, user agents, LLM, RL agent)
    2. Setting up the browser environment with Playwright
    3. Running the orchestrator with proper error handling and cleanup

    Args:
        start_urls: List of URLs to begin crawling from
        db_path: Path to the database file for persistence
        concurrency: Number of concurrent workers
        respect_robots_txt: Whether to respect robots.txt rules
        use_rl: Enable reinforcement learning optimization
        stats_callback: Optional callback for reporting statistics
        alert_callback: Optional callback for reporting alerts
    """
    # Validate inputs
    validate_inputs(start_urls, db_path, concurrency)

    logging.info(
        "Starting crawler with %d workers for URLs: %s",
        concurrency,
        start_urls,
    )

    # Initialize core components
    db_manager = DatabaseManager(db_path=db_path)
    user_agent_manager = UserAgentManager(user_agents=settings.USER_AGENT_LIST)
    llm_extractor = LLMExtractor()

    # Initialize RL agent if requested
    rl_agent = None
    if use_rl:
        domain = urlparse(start_urls[0]).netloc if start_urls else "default"
        rl_agent = RLAgent(
            domain=domain,
            model_path=settings.RL_MODEL_PATH,
            training_mode=use_rl
        )

    # Run crawler with proper browser lifecycle management
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            orchestrator = ScrapingOrchestrator(
                start_urls=start_urls,
                db_manager=db_manager,
                user_agent_manager=user_agent_manager,
                llm_extractor=llm_extractor,
                rl_agent=rl_agent,
                concurrency=concurrency,
                respect_robots_txt=respect_robots_txt,
                use_rl=use_rl,
                stats_callback=stats_callback,
                alert_callback=alert_callback,
            )
            # Always await the orchestrator.run since it's an async method
            await orchestrator.run(browser)
        finally:
            # Ensure RL model is saved even if an exception occurs
            if rl_agent:
                rl_agent.save_model()  # Save model on completion
            await browser.close()
