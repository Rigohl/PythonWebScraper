"""Compatibility package for legacy import paths under `src.intelligence`.

Re-exports the modules that were moved to top-level to preserve
backwards compatibility with existing tests importing e.g.
`from src.intelligence.llm_extractor import LLMExtractor`.
"""

from ..llm_extractor import LLMExtractor  # noqa: F401
from ..rl_agent import RLAgent  # noqa: F401
from .conversation_ai import ConversationalAI  # noqa: F401
from .bot_manager import BotManager  # noqa: F401
from .command_processor import CommandProcessor  # noqa: F401

__all__ = ["LLMExtractor", "RLAgent", "ConversationalAI", "BotManager", "CommandProcessor"]
from ..llm_extractor import \
    LLMExtractor as _RootLLMExtractor  # backward compat alias
# Compatibility package for legacy imports (tests rely on src.intelligence.llm_extractor)
from .llm_extractor import LLMExtractor  # re-export
