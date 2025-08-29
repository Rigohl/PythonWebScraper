"""
Advanced web scraper module.

This module defines the ``AdvancedScraper`` class which encapsulates the
logic for scraping a single web page. The class is responsible for
navigating to a URL using an asynchronous Playwright ``Page`` instance,
capturing network responses to discover hidden APIs, managing cookies,
processing the page content, and returning a structured ``ScrapeResult``.

Improvements over the original implementation include:

* Clear separation of concerns via helper methods for navigation and cookie
  management.
* Rich docstrings and type hints to aid readability and tooling support.
* Simplified response listener management using a context manager.
* Defensive programming around optional values and error handling.

The class can be reused outside of the larger crawler by passing in
appropriate instances of ``DatabaseManager`` and ``LLMExtractor``.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Callable, List, Optional, Type
from urllib.parse import urljoin, urlparse

import html2text
import imagehash
from bs4 import BeautifulSoup
from PIL import Image
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from readability import Document
from pydantic import BaseModel

from .database import DatabaseManager
from .exceptions import (
    ContentQualityError,
    NetworkError,
    ParsingError,
    ScraperException,
)
from .intelligence.llm_extractor import LLMExtractor
from .models.results import ScrapeResult
from .settings import settings


logger = logging.getLogger(__name__)


class AdvancedScraper:
    """High–level API for scraping a single page.

    The scraper accepts a Playwright ``Page`` object along with helper
    services for database persistence and LLM‑powered extraction. It
    encapsulates the entire lifecycle of visiting a URL, extracting
    meaningful content, computing hashes, classifying the content type
    and returning the results. It also persists discovered API calls and
    cookies to the provided ``DatabaseManager``.

    Parameters
    ----------
    page:
        A Playwright ``Page`` instance used to navigate and interact
        with the web page.
    db_manager:
        A ``DatabaseManager`` responsible for persisting cookies and
        discovered APIs.
    llm_extractor:
        An ``LLMExtractor`` used to clean raw text and optionally
        extract structured data according to a Pydantic schema.
    """

    def __init__(self, page: Page, db_manager: DatabaseManager, llm_extractor: LLMExtractor) -> None:
        self.page = page
        self.db_manager = db_manager
        self.llm_extractor = llm_extractor
        # Use a dedicated logger for this instance
        self.logger = logging.getLogger(self.__class__.__name__)

    async def scrape(
        self,
        url: str,
        extraction_schema: Optional[Type[BaseModel]] = None,
    ) -> ScrapeResult:
        """Scrape a single URL and return structured results.

        This method coordinates the navigation to the target URL,
        records any XHR/Fetch JSON responses, manages cookies, cleans
        and validates the page content, and optionally extracts
        structured data using a provided Pydantic model schema.

        Parameters
        ----------
        url:
            The target URL to scrape.
        extraction_schema:
            Optional Pydantic model used for structured extraction.

        Returns
        -------
        ScrapeResult
            A structured result describing the outcome of the scrape.
        """
        start_time = datetime.now(timezone.utc)
        domain = urlparse(url).netloc

        # Register a response listener to capture API calls
        async with self._response_listener():
            try:
                # Load previously saved cookies and navigate to the page
                if domain:
                    await self._apply_cookies(domain)
                response = await self._navigate_to_url(url)
                # Persist current cookies for reuse
                if domain:
                    await self._persist_cookies(domain)
                # Extract raw HTML and parse visible content
                full_html = await self.page.content()
                scrape_result = await self._process_content(
                    url, full_html, response, extraction_schema
                )
            except (PlaywrightTimeoutError, NetworkError) as exc:
                self.logger.warning(f"Network error or timeout scraping {url}: {exc}")
                return ScrapeResult(status="RETRY", url=url, error_message=str(exc), retryable=True)
            except (ParsingError, ContentQualityError) as exc:
                self.logger.error(f"Parsing or content quality error scraping {url}: {exc}")
                return ScrapeResult(status="FAILED", url=url, error_message=str(exc))
            except Exception as exc:  # noqa: BLE001
                # Catch all unexpected errors to avoid crashing the crawler
                self.logger.error(
                    f"Unexpected error scraping {url}: {exc}", exc_info=True
                )
                return ScrapeResult(status="FAILED", url=url, error_message=f"Unexpected error: {exc}")

        # Set duration and return the result
        end_time = datetime.now(timezone.utc)
        scrape_result.crawl_duration = (end_time - start_time).total_seconds()
        return scrape_result

    @asynccontextmanager
    async def _response_listener(self) -> Callable[[], None]:
        """Context manager to attach and detach a response listener.

        The listener captures XHR/Fetch responses with JSON payloads and
        persists them via ``DatabaseManager.save_discovered_api``. This
        context manager ensures the listener is always removed at the
        end of the scrape, even if exceptions occur.
        """

        async def handler(response) -> None:
            content_type = response.headers.get("content-type", "")
            # Only capture JSON responses
            if response.request.resource_type in {"xhr", "fetch"} and "application/json" in content_type:
                try:
                    json_payload = await response.json()
                except Exception as exc:  # noqa: BLE001
                    self.logger.debug(
                        f"Could not process JSON payload from API {response.url}: {exc}"
                    )
                    return
                payload_str = json.dumps(json_payload, sort_keys=True)
                payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
                try:
                    self.db_manager.save_discovered_api(
                        page_url=self.page.url, api_url=response.url, payload_hash=payload_hash
                    )
                except Exception:
                    # Saving API data should never break scraping
                    self.logger.debug(
                        f"Could not save discovered API for {response.url}", exc_info=True
                    )

        # Attach listener
        self.page.on("response", handler)
        try:
            yield
        finally:
            # Always detach listener to avoid leaks
            self.page.remove_listener("response", handler)

    async def _apply_cookies(self, domain: str) -> None:
        """Load and apply cookies for a given domain from the database.

        Parameters
        ----------
        domain:
            The domain for which to load cookies.
        """
        cookies_json = self.db_manager.load_cookies(domain)
        if not cookies_json:
            return
        try:
            cookies = json.loads(cookies_json)
        except json.JSONDecodeError as exc:
            self.logger.error(f"Error decoding cookies for {domain}: {exc}")
            return
        try:
            await self.page.context.add_cookies(cookies)
            self.logger.info(f"Loaded cookies for {domain}")
        except Exception as exc:  # noqa: BLE001
            self.logger.debug(f"Could not apply cookies for {domain}: {exc}")

    async def _persist_cookies(self, domain: str) -> None:
        """Persist current cookies for a domain to the database."""
        try:
            current_cookies = await self.page.context.cookies()
        except Exception:
            self.logger.debug(f"Could not get current cookies for {domain}")
            return
        if not current_cookies:
            return
        try:
            self.db_manager.save_cookies(domain, json.dumps(current_cookies))
            self.logger.info(f"Saved cookies for {domain}")
        except Exception:  # noqa: BLE001
            self.logger.debug(f"Could not save cookies for {domain}", exc_info=True)

    async def _navigate_to_url(self, url: str):
        """Navigate to the target URL and wait for network idle.

        Raises
        ------
        NetworkError
            If a retryable HTTP status code is encountered.
        PlaywrightTimeoutError
            If navigation times out.
        """
        response = await self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        if response and response.status in settings.RETRYABLE_STATUS_CODES:
            raise NetworkError(f"Retryable status: {response.status}")
        # Wait for network to be idle (no pending requests)
        await self.page.wait_for_load_state("networkidle", timeout=15_000)
        return response

    async def _process_content(
        self,
        url: str,
        full_html: str,
        response,
        extraction_schema: Optional[Type[BaseModel]] = None,
    ) -> ScrapeResult:
        """Extract text, validate quality, compute hashes and build result."""
        # Use readability to extract main content and title
        doc = Document(full_html)
        title = doc.title()
        content_html = doc.summary()
        # Convert HTML to plain text
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        raw_text = h.handle(content_html).strip()
        # Clean text via LLM module
        cleaned_text = await self.llm_extractor.clean_text_content(raw_text)
        # Validate quality and length
        self._validate_content_quality(cleaned_text, title)
        # Compute content hash
        content_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
        # Find visible links
        soup = BeautifulSoup(content_html, "html.parser")
        visible_links = [
            urljoin(url, a["href"])
            for a in soup.find_all("a", href=True)
            if "display: none" not in a.get("style", "").lower()
        ]
        # Capture screenshot and derive a perceptual hash
        screenshot = await self.page.screenshot()
        visual_hash = str(imagehash.phash(Image.open(io.BytesIO(screenshot))))
        # Optionally perform structured extraction
        extracted_data = None
        if extraction_schema:
            llm_output = await self.llm_extractor.extract_structured_data(full_html, extraction_schema)
            if llm_output:
                extracted_data = llm_output.model_dump()
        # Build the result object
        result = ScrapeResult(
            status="SUCCESS",
            url=url,
            title=title,
            content_text=cleaned_text,
            content_html=content_html,
            links=visible_links,
            visual_hash=visual_hash,
            content_hash=content_hash,
            http_status_code=response.status if response else None,
            crawl_duration=0.0,  # Overwritten by caller
            content_type=self._classify_content(title, cleaned_text),
            extracted_data=extracted_data,
            healing_events=[],
        )
        return result

    def _validate_content_quality(self, text: Optional[str], title: Optional[str]) -> None:
        """Validate that the extracted content meets quality thresholds.

        Raises
        ------
        ContentQualityError
            If the content is empty, too short or contains forbidden phrases.
        """
        if not text:
            raise ContentQualityError("Extracted content is empty after cleaning.")
        if len(text) < settings.MIN_CONTENT_LENGTH:
            raise ContentQualityError(
                f"Content is too short ({len(text)} characters)."
            )
        lower_text = text.lower()
        lower_title = title.lower() if title else ""
        for phrase in settings.FORBIDDEN_PHRASES:
            if phrase in lower_text or phrase in lower_title:
                raise ContentQualityError(
                    f"Content appears to be an error page (contains: '{phrase}')."
                )

    def _classify_content(self, title: Optional[str], content_text: Optional[str]) -> str:
        """Classify the type of content based on title and body text."""
        if not title and not content_text:
            return "UNKNOWN"
        title_lower = title.lower() if title else ""
        content_lower = content_text.lower() if content_text else ""
        # Products
        if any(
            keyword in title_lower or keyword in content_lower
            for keyword in ["producto", "comprar", "precio", "añadir al carrito"]
        ):
            return "PRODUCT"
        # Blog posts
        if any(
            keyword in title_lower or keyword in content_lower
            for keyword in ["blog", "articulo", "noticia", "leer más"]
        ):
            return "BLOG_POST"
        # Articles/tutorials
        if any(keyword in title_lower for keyword in ["guia", "tutorial"]):
            return "ARTICLE"
        # General content
        if content_text and len(content_text) > settings.MIN_CONTENT_LENGTH:
            return "GENERAL"
        return "UNKNOWN"


