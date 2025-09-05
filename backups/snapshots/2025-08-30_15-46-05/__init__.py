"""Refactored modules for the PythonWebScraper project.

This package mirrors the layout of the upstream ``src`` directory and
contains improved versions of several modules.  When used as a drop‑in
replacement the refactored modules offer clearer APIs, better type
annotations and enhanced testability while preserving backwards
compatibility.
"""

# Re-export key classes for convenience
from .fingerprint_manager import FingerprintManager, Fingerprint  # noqa: F401
from .user_agent_manager import UserAgentManager  # noqa: F401
from .frontier_classifier import FrontierClassifier  # noqa: F401
from .database import DatabaseManager  # noqa: F401
from .llm_extractor import LLMExtractor  # noqa: F401
from .rl_agent import RLAgent, ScrapingEnv  # noqa: F401
