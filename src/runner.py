# src/runner.py

import asyncio
import importlib
import inspect
import logging
import os
from typing import List, Optional
from urllib.parse import urlparse

import httpx
from .scrapers.base import BaseScraper
from .models.results import ScrapeResult
from .database import DatabaseManager
from .llm_extractor import LLMExtractor
from .user_agent_manager import UserAgentManager
from .rl_agent import RLAgent
from .orchestrator import ScrapingOrchestrator
from .intelligence.hybrid_brain import get_hybrid_brain
from .settings import settings
from playwright.async_api import async_playwright

import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(log_file_path: Optional[str] = None, tui_handler: Optional[logging.Handler] = None, level: int = logging.INFO):
    # Remove existing handlers to ensure idempotent reconfiguration
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Determine log file path (default if none passed)
    if not log_file_path:
        log_file_path = os.path.join(os.path.dirname(__file__), "..", "logs", "scraper_run.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # File handler (JSON)
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(JsonFormatter())

    # Console handler (human readable)
    console_handler = logging.StreamHandler()
    console_console_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_handler.setFormatter(logging.Formatter(console_console_fmt))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Optional TUI in-memory/forward handler
    if tui_handler is not None:
        root_logger.addHandler(tui_handler)

    root_logger.setLevel(level)

# Call setup_logging() at the beginning of the file
setup_logging()
logger = logging.getLogger(__name__)

async def run_crawler(
    start_urls: List[str],
    db_path: str = "data/scraper_database.db",
    concurrency: int = 5,
    respect_robots_txt: bool = True,
    use_rl: bool = False,
    stats_callback=None,
    alert_callback=None,
) -> None:
    """Run the main scraping orchestrator with the given parameters.

    Parameters
    ----------
    start_urls:
        List of starting URLs to crawl
    db_path:
        Path to the database file
    concurrency:
        Number of concurrent workers
    respect_robots_txt:
        Whether to respect robots.txt
    use_rl:
        Whether to use reinforcement learning agent
    """
    # Initialize dependencies
    db_manager = DatabaseManager(db_path=db_path)
    user_agent_manager = UserAgentManager(user_agents=settings.USER_AGENT_LIST)
    llm_extractor = LLMExtractor()

    # Optionally initialize RL agent
    rl_agent = None
    if use_rl and start_urls:
        domain = urlparse(start_urls[0]).netloc
        rl_agent = RLAgent(domain=domain, training_mode=True)

    # Initialize HybridBrain - Intelligence is always active
    hybrid_brain = get_hybrid_brain()

    # Configure brain based on settings
    if settings.CONSCIOUSNESS_ENABLED:
        hybrid_brain.enable_consciousness()
    else:
        hybrid_brain.disable_consciousness()

    hybrid_brain.set_integration_mode(settings.INTELLIGENCE_INTEGRATION_MODE)

    # Start continuous learning if enabled
    if settings.CONTINUOUS_LEARNING_ENABLED:
        hybrid_brain.start_continuous_learning()

    logger.info(f"🧠 HybridBrain initialized - Mode: {settings.INTELLIGENCE_INTEGRATION_MODE}, Consciousness: {settings.CONSCIOUSNESS_ENABLED}")

    # Launch browser and run orchestrator
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            orchestrator = ScrapingOrchestrator(
                start_urls=start_urls,
                db_manager=db_manager,
                user_agent_manager=user_agent_manager,
                llm_extractor=llm_extractor,
                rl_agent=rl_agent,
                brain=hybrid_brain,  # Use HybridBrain instead of simple Brain
                concurrency=concurrency,
                respect_robots_txt=respect_robots_txt,
                stats_callback=stats_callback,
                alert_callback=alert_callback,
            )
            await orchestrator.run(browser)
        finally:
            await browser.close()
            # Save RL model if used
            if rl_agent:
                rl_agent.save_model()
            # Flush hybrid brain (saves all intelligence systems)
            try:
                hybrid_brain.flush()
            except Exception:
                pass
            # Auto export Markdown report if enabled and not under tests
            try:
                if not os.getenv("PYTEST_CURRENT_TEST") and os.getenv("AUTO_EXPORT_MD", "1") != "0":
                    from .database import DatabaseManager as _DBM
                    dbm = _DBM(db_path=db_path)
                    from datetime import datetime as _dt
                    ts = _dt.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
                    report_path = os.path.join("exports", "reports", f"auto_report_{ts}.md")
                    os.makedirs(os.path.dirname(report_path), exist_ok=True)
                    dbm.export_to_markdown(report_path)
                    logger.info(f"Auto Markdown report generated: {report_path}")
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed auto Markdown export: {e}")


async def discover_and_run_scrapers(urls: List[str]):
    """
    Dynamically discovers and runs scrapers from the 'src/scrapers' directory.
    """
    scrapers_path = os.path.join(os.path.dirname(__file__), "scrapers")
    scraper_instances: List[BaseScraper] = []

    # Discover scrapers
    for filename in os.listdir(scrapers_path):
        if filename.endswith(".py") and not filename.startswith("__") and filename != "base.py":
            module_name = f"src.scrapers.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseScraper) and obj is not BaseScraper:
                        scraper_instances.append(obj())
                        logger.info(f"Discovered scraper: {name}")
            except ImportError as e:
                logger.error(f"Failed to import scraper from {filename}: {e}")

    if not scraper_instances:
        logger.warning("No scrapers found.")
        return

    # Run scrapers
    async with httpx.AsyncClient() as client:
        tasks = []
        # This is a simple mapping. A more robust solution would match scraper to URL.
        for scraper in scraper_instances:
            for url in urls:
                 # A simple logic to match scraper to url
                if scraper.name.split('_')[0] in url:
                    tasks.append(scraper.scrape(client, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, ScrapeResult):
                logger.info(f"Scraped {result.url} successfully.")
                # Avoid dumping full page content to stdout; log a trimmed snippet for debugging.
                if result.content_text:
                    snippet = (result.content_text[:200] + "…") if len(result.content_text) > 200 else result.content_text
                    logger.debug("Content snippet: %s", snippet)
            elif isinstance(result, Exception):
                logger.error(f"Scraper failed with exception: {result}", exc_info=False)


async def main(urls: List[str]):
    """
    Main entry point.
    """
    await discover_and_run_scrapers(urls)

# This is for direct execution and testing of the runner
if __name__ == "__main__":
    # Example usage:
    target_urls = ["http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"]
    asyncio.run(main(target_urls))
