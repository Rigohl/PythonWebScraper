"""Module for managing scraper module reloading."""

import logging
import sys
import types
from typing import Dict, Optional, cast

from .scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class ScraperRegistry:
    """Registry for managing scraper instances and their modules."""

    _instance = None

    def __new__(cls) -> "ScraperRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.scrapers: Dict[str, BaseScraper] = {}
            cls._instance.scraper_modules: Dict[str, types.ModuleType] = {}
        return cls._instance

    def register_scraper(
        self, name: str, scraper: BaseScraper, module: Optional[types.ModuleType] = None
    ) -> None:
        """Register a scraper instance and its module."""
        self.scrapers[name] = scraper
        if module:
            self.scraper_modules[name] = module

    def get_scraper(self, name: str) -> Optional[BaseScraper]:
        """Get a registered scraper by name."""
        return self.scrapers.get(name)

    def reload_scraper(self, name: str) -> Optional[BaseScraper]:
        """Reload a scraper's module and return a new instance."""
        if name not in self.scraper_modules:
            return None

        try:
            # Reload the module
            module = self.scraper_modules[name]
            reloaded_module = reload_module(module.__name__)

            # Find the scraper class in the reloaded module
            scraper_class = None
            for item_name in dir(reloaded_module):
                item = getattr(reloaded_module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, BaseScraper)
                    and item != BaseScraper
                ):
                    scraper_class = item
                    break

            if not scraper_class:
                logger.error(f"No scraper class found in module {module.__name__}")
                return None

            # Instantiate new scraper
            new_scraper = scraper_class()

            # Update registry
            self.scrapers[name] = new_scraper
            self.scraper_modules[name] = reloaded_module

            logger.info(f"Successfully reloaded scraper: {name}")
            return new_scraper

        except Exception as e:
            logger.error(f"Error reloading scraper {name}: {e}")
            return None


def reload_module(module_name: str) -> types.ModuleType:
    """Reload a module by name, handling imports correctly."""
    sys.modules[module_name]
    return cast(types.ModuleType, __import__(module_name, fromlist=["*"]))
