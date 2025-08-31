"""Compatibility bridge for legacy import path `src.intelligence.llm_extractor`.

Provides access to `LLMExtractor` and the `settings` object. Also keeps the
`instructor` symbol importable so existing patch targets like
`src.intelligence.llm_extractor.instructor.patch` in tests remain valid.
"""

from ..llm_extractor import LLMExtractor  # noqa: F401
from ..settings import settings  # noqa: F401

try:  # Expose instructor for patching in tests
    import instructor  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    instructor = None  # type: ignore

__all__ = ["LLMExtractor", "settings", "instructor"]
# Thin wrapper to maintain backward compatibility with old import path
from ..llm_extractor import *  # noqa: F401,F403
