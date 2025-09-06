"""Compatibility bridge for legacy import path `src.intelligence.llm_extractor`.

Provides access to `LLMExtractor` and the `settings` object. Also keeps the
`instructor` symbol importable so existing patch targets like
`src.intelligence.llm_extractor.instructor.patch` in tests remain valid.
"""

from ..llm_extractor import LLMExtractor as _BaseLLMExtractor  # noqa: F401
from ..settings import settings  # noqa: F401

try:  # Expose instructor for patching in tests
    import instructor  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    from types import SimpleNamespace

    # Provide a minimal shim so test-suite code that patches
    # `src.intelligence.llm_extractor.instructor.patch` can do so
    # even when the optional `instructor` package isn't installed.
    # The shim exposes a `patch` callable which can be replaced by
    # unittest.mock.patch in tests.
    instructor = SimpleNamespace(patch=lambda *a, **k: None)  # type: ignore


class LLMExtractor(_BaseLLMExtractor):  # type: ignore
    async def extract(self, html_content, response_model):  # type: ignore[override]
        try:
            # Reuse async structured path if available
            return await self.adapter.extract_structured_data(
                html_content, response_model
            )
        except Exception:
            return self.adapter.extract_sync(html_content, response_model)


__all__ = ["LLMExtractor", "settings", "instructor"]
