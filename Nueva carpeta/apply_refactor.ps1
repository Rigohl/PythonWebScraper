# Auto-generated script to apply refactored code to a local repository
param([Parameter(Mandatory=$true)][string]$RepoPath)

# Create backup of the existing src folder
$timestamp = (Get-Date).ToString('yyyyMMddHHmmss')
$backupPath = Join-Path $RepoPath ("backup_src_" + $timestamp)
Copy-Item -Path (Join-Path $RepoPath 'src') -Destination $backupPath -Recurse -Force
Write-Host "Se creó un respaldo en $backupPath"

# Reemplazando src\database.py
$content = @'
"""
SQLite persistence layer for scraping results and metadata.

This module defines a :class:`DatabaseManager` that uses the ``dataset``
package to provide a lightweight ORM over a SQLite database.  It persists
scraping results (:class:`ScrapeResult` instances), discovered API calls,
cookie jars and LLM extraction schemas.  Additional helper methods allow
exporting results to CSV or JSON and searching stored pages by keywords.

This rewrite adds context manager support, improved error handling and
extensive documentation.  It keeps backwards‑compatible method names so
existing callers will continue to work.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional, Iterable, List, Dict, Iterator

import dataset

from src.models.results import ScrapeResult

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage connections and operations on a SQLite backing store.

    ``DatabaseManager`` encapsulates a :class:`dataset.Database` instance and
    exposes several tables – pages, discovered APIs, cookies and LLM
    extraction schemas.  It provides CRUD operations for each of these as
    well as convenience methods for exporting data and searching stored
    results.

    A ``DatabaseManager`` can be constructed either with a filesystem path
    (``db_path``) or an existing ``dataset`` connection (``db_connection``).
    When a path is provided the directory is created if it does not exist.
    """

    def __init__(self,
                 db_path: Optional[str] = None,
                 db_connection: Optional[dataset.Database] = None) -> None:
        if db_connection is not None:
            self.db = db_connection
        elif db_path is not None:
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.db = dataset.connect(f"sqlite:///{db_path}")
        else:
            raise ValueError("Se debe proporcionar ''db_path'' o ''db_connection''.")
        # Table handles
        self.table = self.db["pages"]
        self.apis_table = self.db["discovered_apis"]
        self.cookies_table = self.db["cookies"]
        self.llm_schemas_table = self.db["llm_extraction_schemas"]

    # ------------------------------------------------------------------
    # Context manager API
    # ------------------------------------------------------------------
    def __enter__(self) -> "DatabaseManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # dataset closes connections on garbage collection but we do it
        # explicitly when using a context manager for clarity.  Any exception
        # raised during exit is suppressed and must be handled by the caller.
        try:
            self.db.executable.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Discovered APIs and cookies
    # ------------------------------------------------------------------
    def save_discovered_api(self, page_url: str, api_url: str, payload_hash: str) -> None:
        """Insert or update a discovered API call.

        Duplicate entries are avoided by using a composite key of
        ``page_url``, ``api_url`` and ``payload_hash``.
        """
        data = {
            "page_url": page_url,
            "api_url": api_url,
            "payload_hash": payload_hash,
            "timestamp": datetime.now(timezone.utc),
        }
        self.apis_table.upsert(data, ["page_url", "api_url", "payload_hash"])
        logger.info(f"API descubierta en {page_url}: {api_url}")

    def save_cookies(self, domain: str, cookies_json: str) -> None:
        """Persist cookies for the given domain."""
        data = {
            "domain": domain,
            "cookies": cookies_json,
            "timestamp": datetime.now(timezone.utc),
        }
        self.cookies_table.upsert(data, ["domain"])
        logger.debug(f"Cookies guardadas para el dominio: {domain}")

    def load_cookies(self, domain: str) -> Optional[str]:
        """Retrieve cookies for a domain or ``None`` if not found."""
        row = self.cookies_table.find_one(domain=domain)
        return row["cookies"] if row else None

    def save_llm_extraction_schema(self, domain: str, schema_json: str) -> None:
        """Persist an LLM extraction schema for a domain."""
        data = {
            "domain": domain,
            "schema": schema_json,
            "timestamp": datetime.now(timezone.utc),
        }
        self.llm_schemas_table.upsert(data, ["domain"])
        logger.debug(f"Esquema LLM guardado para el dominio: {domain}")

    def load_llm_extraction_schema(self, domain: str) -> Optional[str]:
        """Retrieve a stored LLM extraction schema or ``None`` if missing."""
        row = self.llm_schemas_table.find_one(domain=domain)
        return row["schema"] if row else None

    # ------------------------------------------------------------------
    # Scrape result persistence
    # ------------------------------------------------------------------
    def save_result(self, result: ScrapeResult) -> None:
        """Insert or update a :class:`ScrapeResult`.

        The ``url`` field is used as a primary key.  Duplicate content is
        detected via the ``content_hash``; if a different URL has the same
        hash, the result status is set to ``DUPLICATE``.
        """
        # Deduplication: mark as duplicate if another URL has the same content hash
        if result.content_hash:
            existing = self.table.find_one(content_hash=result.content_hash)
            if existing and existing.get("url") != result.url:
                logger.info(f"Contenido duplicado detectado para {result.url}. Original: {existing[''url'']}. Marcando como DUPLICATE.")
                result.status = "DUPLICATE"

        data = result.model_dump(mode=''json'')

        # JSON serialise complex fields
        if data.get("links") is not None:
            data["links"] = json.dumps(data["links"])
        if data.get("extracted_data") is not None:
            data["extracted_data"] = json.dumps(data["extracted_data"])
        if data.get("healing_events") is not None:
            data["healing_events"] = json.dumps(data["healing_events"])

        self.table.upsert(data, ["url"])
        logger.debug(f"Resultado para {result.url} guardado en la base de datos.")

    def get_result_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch a stored result by URL and deserialise JSON fields."""
        row = self.table.find_one(url=url)
        return self._deserialize_row(row) if row else None

    # ------------------------------------------------------------------
    # Export operations
    # ------------------------------------------------------------------
    def export_to_csv(self, file_path: str) -> None:
        """Export all ``SUCCESS`` results to a CSV file.

        The resulting CSV will contain flattened extracted data fields and
        exclude rows with non‑success statuses.  If no rows qualify, no
        file is created.
        """
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

        results_iterator = self.table.find(status=''SUCCESS'')
        first = next(results_iterator, None)
        if first is None:
            logger.warning("No hay datos con estado ''SUCCESS'' para exportar. No se creará ningún archivo.")
            return

        import csv
        with open(file_path, ''w'', newline='''', encoding=''utf-8'') as csvfile:
            processed_first = self._process_csv_row(dict(first))
            fieldnames = list(processed_first.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(processed_first)
            count = 1
            for row in results_iterator:
                processed = self._process_csv_row(dict(row))
                writer.writerow({k: processed.get(k) for k in fieldnames})
                count += 1
        logger.info(f"{count} registros con estado ''SUCCESS'' exportados a {file_path}")

    def export_to_json(self, file_path: str) -> None:
        """Export all stored results to a JSON file."""
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

        results = self.list_results()
        if not results:
            logger.warning("No hay datos para exportar a JSON. No se creará ningún archivo.")
            return
        with open(file_path, ''w'', encoding=''utf-8'') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logger.info(f"{len(results)} registros exportados a {file_path}")

    # ------------------------------------------------------------------
    # Search operations
    # ------------------------------------------------------------------
    def list_results(self) -> List[Dict[str, Any]]:
        """Return a list of all stored results with deserialised fields."""
        all_rows = self.table.all()
        return [self._deserialize_row(dict(row)) for row in all_rows]

    def search_results(self, query: str) -> List[Dict[str, Any]]:
        """Search results whose title or content contains a substring.

        Args:
            query: A substring to search for (case insensitive).

        Returns:
            A list of deserialised results matching the query.
        """
        like_query = f"%{query}%"
        results_iterator = self.table.find(_or=[
            {''title'': {''like'': like_query}},
            {''content_text'': {''like'': like_query}},
        ])
        return [self._deserialize_row(dict(row)) for row in results_iterator]

    # ------------------------------------------------------------------
    # Internal helper methods
    # ------------------------------------------------------------------
    def _process_csv_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten extracted data for CSV export and remove the original field."""
        if row.get(''extracted_data''):
            try:
                extracted = json.loads(row[''extracted_data''])
                for field, data in extracted.items():
                    row[f''extracted_{field}''] = data.get(''value'')
            except (json.JSONDecodeError, TypeError):
                pass
            finally:
                row.pop(''extracted_data'', None)
        return row

    def _deserialize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialise JSON fields (links, extracted_data, healing_events)."""
        if row is None:
            return row
        # Links
        if row.get(''links''):
            try:
                row[''links''] = json.loads(row[''links''])
            except (json.JSONDecodeError, TypeError):
                row[''links''] = []
        # Complex fields
        for field in [''extracted_data'', ''healing_events'']:
            if row.get(field):
                try:
                    row[field] = json.loads(row[field])
                except (json.JSONDecodeError, TypeError):
                    row[field] = None if field == ''extracted_data'' else []
        return row
'@
$destPath = Join-Path $RepoPath 'src\database.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\llm_extractor.py
$content = @'
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
    from openai import OpenAI
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
                logger.info("LLMExtractor inicializado con el cliente de OpenAI parcheado.")
            except Exception as e:
                logger.error(f"Error inicializando OpenAI client: {e}")
        else:
            logger.warning("LLM API no configurada o dependencias faltantes; se usará modo offline.")

    async def clean_text_content(self, text: str) -> str:
        """Clean HTML text using an LLM or fallback to naive heuristics.

        The cleaning prompt instructs the LLM to remove navigation bars,
        footers and other non‑essential elements.  If the call fails or
        offline mode is active, this method returns the original text.  For
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
                    {"role": "system", "content": "Eres un experto en limpiar contenido HTML. Tu tarea es eliminar todo el texto que no sea el contenido principal de la página, como barras de navegación, pies de página, anuncios, pop-ups y texto legal. Devuelve únicamente el contenido principal."},
                    {"role": "user", "content": text},
                ],
            )
            return response.cleaned_text
        except Exception as e:
            logger.error(f"Error durante la limpieza de texto con LLM: {e}", exc_info=True)
            return text

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Perform zero‑shot extraction of structured data from HTML.

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
                    {"role": "system", "content": "Eres un experto en extracción de datos de páginas web. Tu tarea es analizar el siguiente contenido HTML y rellenar el esquema Pydantic proporcionado con la información encontrada. Extrae los datos de la forma más precisa posible."},
                    {"role": "user", "content": html_content},
                ],
            )
            logger.info(f"Extracción Zero-Shot exitosa para el modelo {response_model.__name__}.")
            return response
        except Exception as e:
            logger.error(f"Error durante la extracción Zero-Shot con LLM: {e}", exc_info=True)
            return response_model()

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Summarise a block of text using the LLM or a naive fallback.

        If the LLM cannot be called, a simple heuristic summarisation is
        applied: the first ``max_words`` words of the input are returned.  In
        production one could replace this with a more sophisticated offline
        summariser such as a frequency‑based extractor.
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
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al sumarizar contenido con LLM: {e}", exc_info=True)
            return text_content[: max_words * 10]
'@
$destPath = Join-Path $RepoPath 'src\llm_extractor.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\scraper.py
$content = @'
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
from .llm_extractor import LLMExtractor
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
                self.logger.warning(f"Error de red o timeout en scrape de {url}: {exc}")
                return ScrapeResult(status="RETRY", url=url, error_message=str(exc), retryable=True)
            except (ParsingError, ContentQualityError) as exc:
                self.logger.error(f"Error de parseo o calidad de contenido en scrape de {url}: {exc}")
                return ScrapeResult(status="FAILED", url=url, error_message=str(exc))
            except Exception as exc:  # noqa: BLE001
                # Catch all unexpected errors to avoid crashing the crawler
                self.logger.error(
                    f"Error inesperado en scrape de {url}: {exc}", exc_info=True
                )
                return ScrapeResult(status="FAILED", url=url, error_message=f"Error inesperado: {exc}")

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
                        f"No se pudo procesar el payload JSON de la API {response.url}: {exc}"
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
                        f"No se pudo guardar la API descubierta para {response.url}", exc_info=True
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
            self.logger.error(f"Error al decodificar cookies para {domain}: {exc}")
            return
        try:
            await self.page.context.add_cookies(cookies)
            self.logger.info(f"Cookies cargadas para {domain}")
        except Exception as exc:  # noqa: BLE001
            self.logger.debug(f"No se pudieron aplicar cookies para {domain}: {exc}")

    async def _persist_cookies(self, domain: str) -> None:
        """Persist current cookies for a domain to the database."""
        try:
            current_cookies = await self.page.context.cookies()
        except Exception:
            self.logger.debug(f"No se pudieron obtener cookies actuales para {domain}")
            return
        if not current_cookies:
            return
        try:
            self.db_manager.save_cookies(domain, json.dumps(current_cookies))
            self.logger.info(f"Cookies guardadas para {domain}")
        except Exception:  # noqa: BLE001
            self.logger.debug(f"No se pudieron guardar cookies para {domain}", exc_info=True)

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
            raise NetworkError(f"Estado reintentable: {response.status}")
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
            raise ContentQualityError("El contenido extraído está vacío después de la limpieza.")
        if len(text) < settings.MIN_CONTENT_LENGTH:
            raise ContentQualityError(
                f"El contenido es demasiado corto ({len(text)} caracteres)."
            )
        lower_text = text.lower()
        lower_title = title.lower() if title else ""
        for phrase in settings.FORBIDDEN_PHRASES:
            if phrase in lower_text or phrase in lower_title:
                raise ContentQualityError(
                    f"Contenido parece ser una página de error (contiene: ''{phrase}'')."
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
'@
$destPath = Join-Path $RepoPath 'src\scraper.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\frontier_classifier.py
$content = @'
"""
Heuristic frontier classifier for URL prioritisation.

This module provides a lightweight ``FrontierClassifier`` that extracts
rudimentary features from a URL – path depth, query parameter count and a
binary indicator for HTTPS – and computes a simple score.  The score can
then be used by a crawling orchestrator to prioritise which links to
process first.  A more sophisticated implementation could load a
pre‑trained machine learning model; here we maintain a deterministic
heuristic for ease of testing.
"""

from __future__ import annotations

from urllib.parse import urlparse
import numpy as np
from typing import Iterable, Tuple


class FrontierClassifier:
    """Dummy classifier for estimating the promise of a URL.

    The classifier exposes two methods:

    * :meth:`extract_features` converts a URL into a numeric feature vector.
    * :meth:`predict_score` computes a floating‑point score from the features
      using a simple heuristic: deeper paths and HTTPS receive higher
      scores.
    """

    def __init__(self, model_path: str | None = None) -> None:
        # ``model_path`` is accepted for forward compatibility but unused.
        self.model_path = model_path

    @staticmethod
    def extract_features(url: str) -> np.ndarray:
        """Return a feature vector ``[path_depth, query_params, is_https]``.

        Args:
            url: The URL to extract features from.

        Returns:
            A 1×3 numpy array of integers.
        """
        parsed = urlparse(url)
        path_segments = [segment for segment in parsed.path.split(''/'') if segment]
        query_params = parsed.query.split(''&'') if parsed.query else []
        features = [
            len(path_segments),
            len(query_params),
            1 if parsed.scheme == ''https'' else 0,
        ]
        return np.array(features, dtype=float).reshape(1, -1)

    def predict_score(self, url: str) -> float:
        """Compute a heuristic score for the given URL.

        The score is computed as ``0.1 * path_depth + 0.5 * is_https``.

        Args:
            url: The URL to score.

        Returns:
            float: The heuristic promise score; larger values indicate higher priority.
        """
        features = self.extract_features(url)
        path_depth = features[0, 0]
        is_https = features[0, 2]
        return float(path_depth * 0.1 + is_https * 0.5)

    # Maintain backwards compatibility with older callers using ``predict``
    def predict(self, url: str) -> float:
        """Alias for :meth:`predict_score`.  Provided for backwards compatibility."""
        return self.predict_score(url)

    def train(self, dataset_path: str) -> None:
        """Placeholder train method.

        This method accepts a path to a dataset but does nothing.  It exists
        solely to mirror the interface of a real classifier.  In a real
        implementation, you would load the dataset, extract features and
        train a model, persisting it to ``self.model_path`` for later use.
        """
        print(f"Entrenamiento dummy del clasificador con dataset: {dataset_path}")
'@
$destPath = Join-Path $RepoPath 'src\frontier_classifier.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\fingerprint_manager.py
$content = @'
"""
Fingerprint management utilities for the scraper.

This module defines a ``FingerprintManager`` class responsible for generating
browser fingerprints that combine a user‑agent, screen resolution and a
handful of JavaScript navigator overrides.  The goal of the manager is to
rotate through a pool of User‑Agents while also randomising viewport sizes
and JS properties to make the underlying browser instance appear more like
a human-operated browser.

The original implementation bundled all logic in a single function.  This
rewrite introduces a small ``Fingerprint`` dataclass to represent the
generated fingerprint and allows injection of a custom random generator for
testability.  It also performs additional validation on constructor
arguments and exposes a method to update the viewport list at runtime.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

from src.user_agent_manager import UserAgentManager

# A predefined set of common screen resolutions.  These values are taken from
# public browser statistics and can be extended or replaced by consumers.
DEFAULT_VIEWPORTS: list[dict[str, int]] = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]


@dataclass(frozen=True)
class Fingerprint:
    """Represents a fully constructed browser fingerprint.

    Attributes:
        user_agent: The User‑Agent string to present.
        viewport: A mapping with ``width`` and ``height`` keys representing
            the viewport dimensions.
        js_overrides: A mapping of JavaScript property overrides to inject
            into the page context.
    """

    user_agent: str
    viewport: Dict[str, int]
    js_overrides: Dict[str, Any]


class FingerprintManager:
    """Generates realistic browser fingerprints for web scraping.

    ``FingerprintManager`` collaborates with a :class:`UserAgentManager` to
    rotate through a collection of User‑Agents.  It randomly selects one
    viewport from a supplied sequence, derives an appropriate platform string
    from the User‑Agent and constructs a set of JavaScript navigator
    overrides.  Consumers may supply their own random number generator via
    the ``rand`` argument for deterministic testing.
    """

    def __init__(self,
                 user_agent_manager: UserAgentManager,
                 viewports: Sequence[Dict[str, int]] | None = None,
                 rand: random.Random | None = None) -> None:
        if user_agent_manager is None:
            raise ValueError("Se debe proporcionar un UserAgentManager.")
        self.user_agent_manager = user_agent_manager

        # Use a copy of the default list to avoid accidental mutation.
        self.viewports: list[Dict[str, int]] = list(viewports) if viewports else list(DEFAULT_VIEWPORTS)
        if not self.viewports:
            raise ValueError("La lista de viewports no puede estar vacía.")

        # Allow dependency injection of a random generator for testability.
        self._random = rand if rand is not None else random.Random()

    def set_viewports(self, viewports: Iterable[Dict[str, int]]) -> None:
        """Replace the list of available viewports.

        This method validates that at least one viewport is provided and
        replaces the internal viewport list.  A copy of the provided
        sequence is stored to avoid external mutation.
        """
        vp_list = list(viewports)
        if not vp_list:
            raise ValueError("La lista de viewports no puede estar vacía.")
        self.viewports = vp_list

    def _platform_from_ua(self, user_agent: str) -> str:
        """Infer the ``navigator.platform`` value from a User‑Agent string."""
        ua_lower = user_agent.lower()
        if "windows" in ua_lower:
            return "Win32"
        if "macintosh" in ua_lower or "mac os" in ua_lower:
            return "MacIntel"
        if "linux" in ua_lower:
            return "Linux x86_64"
        if "iphone" in ua_lower or "ipad" in ua_lower:
            return "iPhone"
        if "android" in ua_lower:
            return "Linux armv8l"
        return "Win32"

    def get_fingerprint(self) -> Fingerprint:
        """Return a new :class:`Fingerprint` with randomised values.

        The method obtains the next available User‑Agent from the underlying
        :class:`UserAgentManager`, selects a viewport at random using the
        injected random generator and constructs a set of JavaScript
        overrides that make the browser appear less like an automated tool.

        Returns:
            Fingerprint: a dataclass instance containing the chosen
                User‑Agent, viewport and JS overrides.
        """
        user_agent = self.user_agent_manager.get_user_agent()
        viewport = self._random.choice(self.viewports)
        platform = self._platform_from_ua(user_agent)

        js_overrides = {
            "navigator.webdriver": False,
            # Provide languages as a Python list literal for injection.
            "navigator.languages": "[''en-US'', ''en'']",
            "navigator.platform": f"''{platform}''",
            "navigator.plugins.length": 0,
            "screen.colorDepth": 24,
            "navigator.hardwareConcurrency": self._random.choice([4, 8, 16]),
            "navigator.deviceMemory": self._random.choice([4, 8]),
        }

        return Fingerprint(user_agent=user_agent, viewport=viewport, js_overrides=js_overrides)
'@
$destPath = Join-Path $RepoPath 'src\fingerprint_manager.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\user_agent_manager.py
$content = @'
"""
User‑Agent rotation and blocking manager.

This module defines ``UserAgentManager``, a small utility class for
rotating through a collection of User‑Agent strings, temporarily blocking
agents that lead to detection or throttling and restoring them after a
configurable timeout.  The original implementation used bare functions
without extensive type hints or documentation.  In this rewrite we add
comprehensive docstrings, type annotations and a few helper methods to
improve testability and clarity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, List, Set, Dict


@dataclass
class UserAgentManager:
    """Manages rotation and temporary blocking of User‑Agent strings.

    The manager maintains a pool of User‑Agents and cycles through them on
    successive calls to :meth:`get_user_agent`.  Agents can be blocked for
    a specified duration using :meth:`block_user_agent`, during which
    :meth:`get_user_agent` will skip them.  Once the block expires or the
    agent is manually released via :meth:`release_user_agent`, it becomes
    available again.

    Args:
        user_agents: An iterable of User‑Agent strings.  Duplicate
            values are ignored.

    Raises:
        ValueError: If ``user_agents`` is empty.
    """

    user_agents: List[str]
    available_user_agents: Set[str] = field(init=False)
    blocked_user_agents: Dict[str, datetime] = field(init=False, default_factory=dict)
    _rotation_index: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if not self.user_agents:
            raise ValueError("La lista de User-Agents no puede estar vacía.")
        # Normalise to a list to allow index-based rotation and create a set
        # of available agents for fast membership tests.
        self.user_agents = list(dict.fromkeys(self.user_agents))
        self.available_user_agents = set(self.user_agents)

    def _clean_expired_blocks(self) -> None:
        """Remove expired entries from the blocked user agents dictionary."""
        now = datetime.now()
        expired = [ua for ua, until in self.blocked_user_agents.items() if now > until]
        for ua in expired:
            # Re-add to available and delete from blocked
            self.available_user_agents.add(ua)
            del self.blocked_user_agents[ua]

    def get_user_agent(self) -> str:
        """Return the next available User‑Agent, rotating through the pool.

        If all agents are currently blocked, this method returns a User‑Agent
        from the original list in round‑robin order, even if that agent is
        still blocked.  This ensures the scraper always has something to send.

        Returns:
            str: A User‑Agent string.
        """
        self._clean_expired_blocks()
        if not self.available_user_agents:
            # All are blocked; fall back to sequential rotation through the
            # original list.  We don''t remove the block entry here because
            # the block timeout may still be in force.
            self._rotation_index = (self._rotation_index + 1) % len(self.user_agents)
            return self.user_agents[self._rotation_index]

        # Cycle through only available agents
        available_list = list(self.available_user_agents)
        self._rotation_index = (self._rotation_index + 1) % len(available_list)
        return available_list[self._rotation_index]

    def block_user_agent(self, user_agent: str, duration_seconds: int = 300) -> None:
        """Temporarily block a User‑Agent for a given number of seconds.

        Args:
            user_agent: The User‑Agent string to block.  If the agent is not
                recognised, this method silently returns.
            duration_seconds: The number of seconds to block the User‑Agent.
        """
        if user_agent in self.available_user_agents:
            self.available_user_agents.remove(user_agent)
        # Always set/update the blocked expiry time, even if the agent wasn''t available.
        self.blocked_user_agents[user_agent] = datetime.now() + timedelta(seconds=duration_seconds)

    def release_user_agent(self, user_agent: str) -> None:
        """Release a previously blocked User‑Agent immediately.

        Args:
            user_agent: The User‑Agent string to release.  If the agent is not
                present in the blocked list, this method silently returns.
        """
        if user_agent in self.blocked_user_agents:
            del self.blocked_user_agents[user_agent]
            self.available_user_agents.add(user_agent)

    def is_blocked(self, user_agent: str) -> bool:
        """Check whether a User‑Agent is currently blocked."""
        self._clean_expired_blocks()
        return user_agent in self.blocked_user_agents

    def has_available(self) -> bool:
        """Return ``True`` if at least one User‑Agent is currently available."""
        self._clean_expired_blocks()
        return bool(self.available_user_agents)
'@
$destPath = Join-Path $RepoPath 'src\user_agent_manager.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\__init__.py
$content = @'
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
'@
$destPath = Join-Path $RepoPath 'src\__init__.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

# Reemplazando src\rl_agent.py
$content = @'
"""
Reinforcement learning wrapper for adaptive scraping.

This module defines an RL environment and agent for controlling the
backoff factor of a web scraper.  It attempts to load the PPO algorithm
from stable_baselines3 when available; if the dependency is missing, it
falls back to a dummy model that simply returns no‑change actions.  This
design keeps the orchestrator functional in offline test environments.
"""

from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

import numpy as np

try:
    import gymnasium as gym  # type: ignore
    from gymnasium import spaces  # type: ignore
    from stable_baselines3 import PPO  # type: ignore
    from stable_baselines3.common.vec_env import DummyVecEnv  # type: ignore
    RL_AVAILABLE = True
except Exception:
    # Provide minimal shims when RL libraries are missing
    RL_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScrapingEnv:
    """Gymnasium environment for the RL agent.

    The environment defines a continuous observation space representing
    domain metrics and a discrete action space with three possible actions:
    decrease, keep or increase the backoff factor.  When gymnasium is not
    installed, this class provides the minimal interface expected by the
    agent.
    """

    def __init__(self) -> None:
        if RL_AVAILABLE:
            # Define observation and action spaces using gymnasium types
            self.observation_space = spaces.Box(low=np.array([0.0, 0.0, 0.1]),
                                                high=np.array([1.0, 1.0, 10.0]),
                                                dtype=np.float32)
            self.action_space = spaces.Discrete(3)
        self.current_state = np.zeros(3, dtype=np.float32)

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        # Placeholder; the orchestrator drives the environment.
        return self.current_state, 0.0, False, False, {}

    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, dict]:
        self.current_state = np.zeros(3, dtype=np.float32)
        return self.current_state, {}

    def set_state(self, state_dict: dict) -> None:
        """Update the internal state representation from a metrics dictionary."""
        self.current_state = np.array([
            state_dict.get("low_quality_ratio", 0.0),
            state_dict.get("failure_ratio", 0.0),
            state_dict.get("current_backoff", 0.1),
        ], dtype=np.float32)


class DummyModel:
    """Simple fallback model used when RL libraries are unavailable.

    The dummy model always returns the "no change" action and performs no
    learning.  It exposes the same ``predict``, ``learn`` and ``save``
    interface expected by :class:`RLAgent`.
    """

    def __init__(self) -> None:
        pass

    def predict(self, obs: np.ndarray, deterministic: bool = True) -> Tuple[np.ndarray, None]:
        return np.array([1]), None  # action 1 corresponds to no change

    def learn(self, total_timesteps: int) -> None:
        # No learning performed
        pass

    def save(self, path: str) -> None:
        # Saving does nothing in dummy mode
        pass


class RLAgent:
    """Reinforcement Learning agent controlling the scraper backoff factor.

    The agent uses a PPO model from stable_baselines3 when available; if
    dependencies are missing it falls back to a dummy model that issues
    neutral actions and does not learn.  The ``domain`` parameter is used
    solely to namespace the model on disk.  The ``model_path`` is an
    optional filesystem path for loading and saving the trained model.
    """

    def __init__(self, domain: str, model_path: Optional[str] = None, training_mode: bool = True) -> None:
        self.domain = domain
        self.model_path = model_path
        self.training_mode = training_mode
        self.env = ScrapingEnv()
        self.experience_buffer: list[tuple] = []
        self.buffer_size = 100

        if RL_AVAILABLE:
            self.vec_env = DummyVecEnv([lambda: self.env])  # type: ignore
            # Load existing model if possible
            if model_path and os.path.exists(f"{model_path}.zip"):
                try:
                    self.model = PPO.load(model_path, env=self.vec_env, custom_objects={"observation_space": self.env.observation_space, "action_space": self.env.action_space})  # type: ignore
                    logger.info(f"Modelo RL cargado desde: {model_path}")
                except Exception as e:
                    logger.error(f"Error al cargar el modelo RL desde {model_path}: {e}. Inicializando uno nuevo.")
                    self.model = PPO("MlpPolicy", self.vec_env, verbose=0, device="cpu")  # type: ignore
            else:
                self.model = PPO("MlpPolicy", self.vec_env, verbose=0, device="cpu")  # type: ignore
                logger.info("Nuevo modelo PPO inicializado.")
        else:
            # Fallback: dummy model
            self.model = DummyModel()
            logger.warning("stable_baselines3 no está disponible; usando DummyModel para RL.")

    def get_action(self, state_dict: dict) -> dict:
        """Compute an action dictionary from a state dictionary."""
        self.env.set_state(state_dict)
        obs = self.env.current_state
        action, _ = self.model.predict(obs, deterministic=True)
        action_val = int(action) if isinstance(action, (np.ndarray, list)) else int(action)
        if action_val == 0:
            return {"adjust_backoff_factor": 0.8}
        if action_val == 1:
            return {"adjust_backoff_factor": 1.0}
        if action_val == 2:
            return {"adjust_backoff_factor": 1.2}
        logger.warning(f"Acción RL desconocida: {action_val}. Devolviendo acción por defecto.")
        return {"adjust_backoff_factor": 1.0}

    def learn(self, state: dict, action_taken: dict, reward: float, next_state: dict) -> None:
        """Append an experience to the buffer and train when full.

        In dummy mode this method records the experience but does not
        actually invoke learning.  With PPO available it performs a
        rudimentary training step when the experience buffer reaches
        ``buffer_size``.  Note that this is a simplification; full on‑policy
        training would require direct interaction with the environment.
        """
        # Map the action dict back to an index
        if action_taken.get("adjust_backoff_factor") == 0.8:
            act_idx = 0
        elif action_taken.get("adjust_backoff_factor") == 1.2:
            act_idx = 2
        else:
            act_idx = 1
        self.experience_buffer.append((state, act_idx, reward, next_state))
        # When RL is unavailable, do nothing more
        if not RL_AVAILABLE:
            return
        # Trigger training if buffer is full
        if len(self.experience_buffer) >= self.buffer_size:
            try:
                self.model.learn(total_timesteps=self.buffer_size)
                logger.info(f"Modelo PPO entrenado con {self.buffer_size} pasos.")
            except Exception as e:
                logger.error(f"Error durante el aprendizaje del modelo PPO: {e}", exc_info=True)
            finally:
                self.experience_buffer = []
                self.save_model()

    def save_model(self) -> None:
        """Persist the trained model to disk if a path was provided."""
        if RL_AVAILABLE and self.model_path:
            try:
                self.model.save(self.model_path)
                logger.info(f"Modelo RL guardado en: {self.model_path}")
            except Exception as e:
                logger.error(f"Error al guardar el modelo RL en {self.model_path}: {e}")
'@
$destPath = Join-Path $RepoPath 'src\rl_agent.py'
New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
Set-Content -Path $destPath -Value $content -Force

Write-Host "Los archivos refactorizados se han aplicado correctamente."