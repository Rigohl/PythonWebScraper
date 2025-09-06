# src/scrapers/base.py
from abc import ABC, abstractmethod

from httpx import AsyncClient

from ..models.results import ScrapeResult


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def scrape(self, client: AsyncClient, url: str) -> ScrapeResult:
        """
        Scrapes a single URL and returns the result.
        This method must be implemented by all subclasses.
        """
        pass

    def __str__(self):
        return f"Scraper(name={self.name})"

    def get_info(self):
        """Get basic info about the scraper."""
        return {"name": self.name, "type": self.__class__.__name__}
