"""Crawler execution runner."""

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


async def run_crawler(
    start_urls: list[str],
    db_path: str,
    concurrency: int,
    respect_robots_txt: bool,
    use_rl: bool,
    stats_callback: Optional[Callable] = None,
    alert_callback: Optional[Callable] = None,
) -> None:
    """Helper function to set up and run the crawler."""
    logging.info(
        "Iniciando crawler con %s trabajadores para las URLs: %s",
        concurrency,
        start_urls,
    )
    db_manager = DatabaseManager(db_path=db_path)
    user_agent_manager = UserAgentManager(user_agents=settings.USER_AGENT_LIST)
    llm_extractor = LLMExtractor()

    rl_agent = None
    if use_rl:
        domain = urlparse(start_urls[0]).netloc if start_urls else "default"
        rl_agent = RLAgent(
            domain=domain, model_path=settings.RL_MODEL_PATH, training_mode=use_rl
        )

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
                stats_callback=stats_callback,
                alert_callback=alert_callback,
            )
            # Always await the orchestrator.run since it's an async method
            await orchestrator.run(browser)
        finally:
            if rl_agent:
                rl_agent.save_model()  # Guardar el modelo al finalizar
            await browser.close()
