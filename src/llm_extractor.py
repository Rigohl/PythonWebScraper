"""
Language model helper utilities.

This module exposes an ``LLMExtractor`` class that encapsulates calls to a
Large Language Model (LLM) for tasks such as cleaning HTML, extracting
structured data into Pydantic models and summarising long passages of text.
This implementation now uses LLM adapters for better abstraction and testing.
When the OpenAI API key is unavailable or when an API call fails, the
extractor falls back to simple deterministic logic so that the rest of
the pipeline can continue without throwing exceptions.  This design makes
the scraper resilient in offline environments and simplifies testing.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

from .adapters.llm_adapter import LLMAdapter, OpenAIAdapter, OfflineLLMAdapter
from .settings import settings


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMExtractor:
    """Lightweight wrapper around an LLM with safe offline fallbacks.

    This class now uses LLM adapters for better abstraction and testing.
    Behaviour:
    - If ``settings.OFFLINE_MODE`` is True OR dependencies / API key are missing,
      the extractor works in deterministic offline mode.
    - Each public method degrades gracefully without raising, guaranteeing the
      rest of the scraping pipeline keeps functioning.
    """

    def __init__(self, adapter: Optional[LLMAdapter] = None) -> None:  # noqa: D401
        if adapter:
            self.adapter = adapter
        elif settings.LLM_API_KEY and not settings.OFFLINE_MODE:
            try:
                self.adapter = OpenAIAdapter(
                    api_key=settings.LLM_API_KEY,
                    model=settings.LLM_MODEL
                )
                logger.info("LLMExtractor: adaptador OpenAI inicializado.")
            except Exception as e:  # pragma: no cover - unexpected init failures
                logger.error(f"LLMExtractor: error inicializando adaptador OpenAI: {e}")
                self.adapter = OfflineLLMAdapter()
        else:
            self.adapter = OfflineLLMAdapter()
            logger.info("LLMExtractor: modo offline (sin cliente remoto).")

    # ---------------------------------------------------------------------
    # Public API (async)
    # ---------------------------------------------------------------------
    async def clean_text_content(self, text: str) -> str:
        """Return cleaned main content text.

        Offline fallback: returns the original text unchanged.
        """
        return await self.adapter.clean_text(text)

    async def extract_structured_data(
        self, html_content: str, response_model: Type[T]
    ) -> T:
        """Zero‑shot structured extraction into a Pydantic ``response_model``.

        Offline fallback: instantiate and return an empty model.
        """
        return await self.adapter.extract_structured_data(html_content, response_model)

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Summarise content; fallback returns first ``max_words`` words."""
        return await self.adapter.summarize_content(text_content, max_words)

    # ------------------------------------------------------------------
    # Backwards compatibility (legacy sync API expected by some tests)
    # ------------------------------------------------------------------
    # ---------------------------------------------------------------------
    # Backward compatibility sync alias
    # ---------------------------------------------------------------------
    async def extract(self, html_content: str, response_model: Type[T]):  # type: ignore[override]
        """Legacy wrapper.

        Si el adaptador implementa extracción estructurada asíncrona la usamos
        para incrementar correctamente contadores de mocks; de lo contrario
        caemos al método síncrono legacy.
        """
        try:
            # Prefer async path when available
            return await self.adapter.extract_structured_data(html_content, response_model)  # type: ignore[attr-defined]
        except Exception:
            return self.adapter.extract_sync(html_content, response_model)
