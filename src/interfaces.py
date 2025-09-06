# src/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .scrapers.base import ScrapeResult


class LearningAgent(ABC):
    """
    Interface for a Reinforcement Learning agent that guides the scraper.
    """

    @abstractmethod
    def choose_next_url(
        self, available_urls: List[str], current_context: Dict[str, Any]
    ) -> str:
        """
        Given a list of available URLs and the current context, choose the best one to scrape next.
        """

    @abstractmethod
    def learn_from_result(self, result: ScrapeResult, context: Dict[str, Any]):
        """
        Update the agent's internal model based on the result of a scrape.
        This is the feedback loop.
        """


def calculate_reward(result: ScrapeResult) -> float:
    """
    Calculates a numerical reward based on a ScrapeResult.
    This can be fine-tuned to guide the agent's learning process.
    """
    if result.status == "FAILED":
        return -1.0

    reward = 0.1  # Base reward for a successful scrape

    if result.data:
        # Reward for extracting data
        reward += 0.5
        # Bonus for extracting key fields
        if "price" in result.data:
            reward += 0.2
        if "title" in result.data:
            reward += 0.1

    # Penalize for finding no new links (dead end)
    if not result.data.get("links"):
        reward -= 0.2

    return round(reward, 2)
