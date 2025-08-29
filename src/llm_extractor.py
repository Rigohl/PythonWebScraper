"""
Language model helper utilities.

This module exposes an ``LLMExtractor`` class that encapsulates calls to a
Large Language Model (LLM) for tasks such as cleaning HTML, extracting
structured data into Pydantic models and summarising long passages of text.
When the OpenAI API key is unavailable or when an API call fails, the
extractor falls back to simple deterministic logic so that the rest of
the pipeline can continue without throwing exceptions.  This design makes
the scraper resilient in offline environments and simplifies testing.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Type, TypeVar, Optional

try:
    import instructor
    from openai import OpenAI, APIError, APITimeoutError, APIConnectionError
    OPENAI_AVAILABLE = True
except Exception:
    # If the OpenAI SDK or instructor is not installed, we mark the client as unavailable.
    OPENAI_AVAILABLE = False

from pydantic import BaseModel, create_model
from src.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMExtractor:
    """Wrapper around a Language Model for cleaning, extracting and summarising.

    Upon instantiation the extractor attempts to construct an OpenAI client
    patched by ``instructor``.  If the API key is not set or the required
    dependencies are missing, the extractor will operate in offline mode and
    rely on deterministic fallback logic.
    """

    def __init__(self) -> None:
        self.client: Optional[Any] = None
        if OPENAI_AVAILABLE and settings.LLM_API_KEY:
            try:
                self.client = instructor.patch(OpenAI(api_key=settings.LLM_API_KEY))
                logger.info("LLMExtractor initialized with patched OpenAI client.")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
        else:
            logger.warning("LLM API key not configured or dependencies missing; using offline mode.")

    async def clean_text_content(self, text: str) -> str:
        """Clean HTML text using an LLM or fallback to naive heuristics.

        The cleaning prompt instructs the LLM to remove navigation bars,
        footers and other non-essential elements. If the call fails or
        offline mode is active, this method returns the original text. For
        offline mode one could extend this with a simple readability filter.
        """
        if not self.client:
            # Fallback: no cleaning performed.
            return text
        try:
            class CleanedText(BaseModel):
                cleaned_text: str
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                response_model=CleanedText,
                messages=[
                    {"role": "system", "content": "You are an expert in cleaning HTML content. Your task is to remove all text that is not the main content of the page, such as navigation bars, footers, ads, pop-ups, and legal text. Return only the main content."},
                    {"role": "user", "content": text},
                ],
            )
            return response.cleaned_text
        except (APIError, APITimeoutError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during text cleaning: {e}", exc_info=True)
            return text
        except Exception as e:
            logger.error(f"Unexpected error during LLM text cleaning: {e}", exc_info=True)
            return text

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Perform zero-shot extraction of structured data from HTML.

        When the LLM is unavailable this method returns an empty instance of
        ``response_model`` so that the caller can proceed without crashing.
        """
        if not self.client:
            return response_model()
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                response_model=response_model,
                messages=[
                    {"role": "system", "content": "You are an expert in data extraction from web pages. Your task is to analyze the following HTML content and fill the provided Pydantic schema with the information found. Extract the data as accurately as possible."},
                    {"role": "user", "content": html_content},
                ],
            )
            logger.info(f"Zero-shot extraction successful for model {response_model.__name__}.")
            return response
        except (APIError, APITimeoutError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during zero-shot extraction: {e}", exc_info=True)
            return response_model()
        except Exception as e:
            logger.error(f"Unexpected error during zero-shot extraction: {e}", exc_info=True)
            return response_model()

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Summarise a block of text using the LLM or a naive fallback.

        If the LLM cannot be called, a simple heuristic summarisation is
        applied: the first ``max_words`` words of the input are returned. In
        production one could replace this with a more sophisticated offline
        summariser such as a frequency-based extractor.
        """
        if not self.client:
            # Naive summarisation: return the first ``max_words`` words.
            words = re.split(r"\s+", text_content)
            return " ".join(words[:max_words])
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Summarize the following text in approximately {max_words} words."},
                    {"role": "user", "content": text_content},
                ],
                temperature=0.7,
                max_tokens=max_words * 2,
            )
            # The OpenAI API returns a list of choices; pick the first.
            summary = response.choices[0].message.content
            return summary if summary is not None else ""
        except (APIError, APITimeoutError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during content summarization: {e}", exc_info=True)
            return " ".join(re.split(r"\s+", text_content)[:max_words])
        except Exception as e:
            logger.error(f"Unexpected error during content summarization: {e}", exc_info=True)
            return " ".join(re.split(r"\s+", text_content)[:max_words])
