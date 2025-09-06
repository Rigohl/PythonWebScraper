"""Hot reloading implementation for the scraper orchestrator."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .hot_reload import ScraperRegistry
from .orchestrator import ScrapingOrchestrator

logger = logging.getLogger(__name__)


class ScraperWatcher(FileSystemEventHandler):
    def __init__(self, orchestrator: "HotReloadOrchestrator"):
        self.orchestrator = orchestrator
        self.registry = ScraperRegistry()

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return

        if not event.src_path.endswith(".py"):
            return

        # Check if this is a scraper module
        file_path = Path(event.src_path)
        if not any("scrapers" in parent.name for parent in file_path.parents):
            return

        # Get scraper name from file path
        scraper_name = file_path.stem
        if scraper_name == "__init__" or scraper_name == "base":
            return

        logger.info(f"Detected changes in scraper module: {scraper_name}")
        asyncio.create_task(self.orchestrator.reload_scraper(scraper_name))


class HotReloadOrchestrator(ScrapingOrchestrator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = ScraperRegistry()
        self.observer: Optional[Observer] = None
        self.watcher: Optional[ScraperWatcher] = None

    async def start_hot_reload(self):
        """Start watching for changes in scraper modules."""
        if self.observer:
            return

        # Setup file watcher
        scrapers_dir = Path(__file__).parent / "scrapers"
        self.watcher = ScraperWatcher(self)
        self.observer = Observer()
        self.observer.schedule(self.watcher, str(scrapers_dir), recursive=True)
        self.observer.start()

        logger.info(f"Hot reload watcher started for directory: {scrapers_dir}")

    def stop_hot_reload(self):
        """Stop watching for changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    async def reload_scraper(self, scraper_name: str):
        """Reload a scraper module and update any active instances."""
        try:
            # Reload the scraper module
            new_scraper = self.registry.reload_scraper(scraper_name)
            if not new_scraper:
                logger.error(f"Failed to reload scraper: {scraper_name}")
                return

            # Update any existing scraper instances
            # This is safe because the scraper interface ensures compatibility
            if hasattr(self, "scraper") and isinstance(self.scraper, type(new_scraper)):
                self.scraper = new_scraper
                logger.info(f"Updated active scraper instance: {scraper_name}")

        except Exception as e:
            logger.error(f"Error during hot reload of {scraper_name}: {e}")

    async def run(self, browser):
        """Override run to include hot reload support."""
        try:
            # Start hot reload watcher
            await self.start_hot_reload()

            # Run normal scraping process
            await super().run(browser)

        finally:
            # Clean up watcher
            self.stop_hot_reload()
