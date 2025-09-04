"""Compatibility package for legacy import paths under `src.intelligence`.

Re-exports the modules that were moved to top-level to preserve
backwards compatibility with existing tests importing e.g.
`from src.intelligence.llm_extractor import LLMExtractor`.
"""

from ..llm_extractor import LLMExtractor
from ..rl_agent import RLAgent

__all__ = ["LLMExtractor", "RLAgent"]
