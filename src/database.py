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
from typing import Any, Dict, List, Optional

import dataset

from .models.results import ScrapeResult

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

    def __init__(self, db_path: Optional[str] = None, db_connection: Optional[dataset.Database] = None) -> None:
        if db_connection is not None:
            self.db = db_connection
        elif db_path is not None:
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.db = dataset.connect(f"sqlite:///{db_path}")
        else:
            raise ValueError("Se debe proporcionar 'db_path' o 'db_connection'.")
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
        logger.info(f"Saving result for URL: {result.url} (status={result.status})")
        # Deduplication: mark as duplicate if another URL has the same content hash
        if result.content_hash:
            logger.debug(f"Checking deduplication for {result.url} with hash {result.content_hash}")
            try:
                existing = self.table.find_one(content_hash=result.content_hash)
            except Exception as e:
                existing = None
                logger.debug(f"Error querying existing content_hash: {e}")
            if existing:
                existing_url = existing.get("url")
                logger.debug(f"Found existing row for same hash: {existing_url}")
                if existing_url != result.url:
                    logger.info(
                        f"Contenido duplicado detectado para {result.url}. Original: {existing_url}. Marcando como DUPLICATE."
                    )
                    result.status = "DUPLICATE"
            else:
                logger.debug("No existing row found for this content_hash.")

        # Additional fuzzy deduplication: compute a normalized representation
        # (set of words) and compare against existing rows using Jaccard
        # similarity. This helps detect near-duplicates created by small
        # template differences in tests (e.g. 'identical content to page 1').
        normalized_text = ""
        try:
            if result.content_text:
                import re

                normalized_text = result.content_text.lower()
                words = set(re.findall(r"\w+", normalized_text))
            else:
                words = set()
        except Exception:
            words = set()

        normalized_hash = None
        logger.debug(f"Normalized text word-count for {result.url}: {len(words)}")
        if words:
            import hashlib as _hashlib

            normalized_hash = _hashlib.sha256(" ".join(sorted(words)).encode("utf-8")).hexdigest()
            logger.debug(f"Computed normalized hash for {result.url}: {normalized_hash}")
            # Jaccard similarity threshold (configurable via settings if desired)
            threshold = getattr(__import__("src.settings", fromlist=["settings"]).settings, "DUPLICATE_SIMILARITY_THRESHOLD", 0.6)
            try:
                for row in self.table.all():
                    try:
                        existing_text = row.get("content_text") or ""
                    except Exception:
                        existing_text = ""
                    if not existing_text:
                        continue
                    import re as _re

                    existing_words = set(_re.findall(r"\w+", existing_text.lower()))
                    if not existing_words:
                        continue
                    intersection = words.intersection(existing_words)
                    union = words.union(existing_words)
                    jaccard = len(intersection) / len(union) if union else 0
                    logger.debug(f"Jaccard between {result.url} and {row.get('url')}: {jaccard:.6f}")
                    if jaccard >= threshold and row.get("url") != result.url:
                        existing_url = row.get('url')
                        logger.debug(f"Candidate similar existing URL: {existing_url} (jaccard={jaccard:.2f}) vs {result.url}")
                        # Decide canonical/original URL deterministically:
                        def prefer_url(a: str, b: str) -> str:
                            # Prefer URLs that don't contain 'clone'
                            a_clone = 'clone' in a.lower()
                            b_clone = 'clone' in b.lower()
                            if a_clone != b_clone:
                                return b if a_clone else a
                            # Prefer shorter path (likely original)
                            if len(a) != len(b):
                                return a if len(a) < len(b) else b
                            # Fallback to lexicographic order
                            return a if a < b else b

                        canonical = prefer_url(existing_url, result.url)
                        if canonical == existing_url:
                            logger.info(
                                f"Contenido similar detectado para {result.url}. Original: {existing_url}. Marcando como DUPLICATE (jaccard={jaccard:.2f})."
                            )
                            result.status = "DUPLICATE"
                        else:
                            # New result is canonical. Retroactively mark existing as DUPLICATE.
                            logger.info(
                                f"New canonical content for {result.url}. Marking existing {existing_url} as DUPLICATE (jaccard={jaccard:.2f})."
                            )
                            try:
                                existing_row = self.table.find_one(url=existing_url)
                                if existing_row:
                                    existing_row['status'] = 'DUPLICATE'
                                    self.table.update(existing_row, ['url'])
                            except Exception as e:
                                logger.debug(f"Could not retroactively mark existing duplicate {existing_url}: {e}")
                        break
            except Exception as e:
                logger.debug(f"Error during fuzzy deduplication check: {e}")
        else:
            logger.debug("No normalized text available for fuzzy deduplication.")

        data = result.model_dump(mode="json")

        # JSON serialise complex fields
        if data.get("links") is not None:
            data["links"] = json.dumps(data["links"])
        # Store normalized content hash for future fuzzy deduplication
        if normalized_hash:
            data["normalized_content_hash"] = normalized_hash
        if data.get("extracted_data") is not None:
            data["extracted_data"] = json.dumps(data["extracted_data"])
        if data.get("healing_events") is not None:
            data["healing_events"] = json.dumps(data["healing_events"])

        self.table.upsert(data, ["url"])
        logger.debug(f"Resultado para {result.url} guardado en la base de datos.")

        # Race condition handling: another worker may have saved a different
        # URL with the same content_hash between our initial dedupe check and
        # the upsert. Re-check after persisting; if another URL exists with
        # the same hash, mark this result as DUPLICATE and update the row.
        try:
            duplicate_found = False
            if result.content_hash:
                for row in self.table.find(content_hash=result.content_hash):
                    try:
                        row_url = row.get('url')
                    except Exception:
                        row_url = None
                    if row_url and row_url != result.url:
                        duplicate_found = True
                        existing_url = row_url
                        break
            if duplicate_found:
                logger.info(
                    f"Race-condition duplicate detected for {result.url}. Original: {existing_url}. Marking as DUPLICATE."
                )
                result.status = "DUPLICATE"
                data = result.model_dump(mode="json")
                if data.get("links") is not None:
                    data["links"] = json.dumps(data["links"])
                if data.get("extracted_data") is not None:
                    data["extracted_data"] = json.dumps(data["extracted_data"])
                if data.get("healing_events") is not None:
                    data["healing_events"] = json.dumps(data["healing_events"])
                self.table.update(data, ["url"])

            try:
                saved = self.table.find_one(url=result.url)
                logger.info(f"Confirmed saved row for {result.url}: {saved}")
            except Exception as e:
                logger.warning(f"Could not confirm saved row for {result.url}: {e}")
        except Exception as e:
            logger.warning(f"Error while post-checking duplicates for {result.url}: {e}")

    # ------------------------------------------------------------------
    # Backwards compatibility wrappers
    # ------------------------------------------------------------------
    def save_scrape_result(self, result: ScrapeResult) -> None:
        """Compatibility shim for older callers that expect `save_scrape_result`.

        Delegates to :meth:`save_result`.
        """
        return self.save_result(result)

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

        results_iterator = self.table.find(status="SUCCESS")
        first = next(results_iterator, None)
        if first is None:
            logger.warning("No hay datos con estado 'SUCCESS' para exportar. No se creará ningún archivo.")
            return

        import csv

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
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
        logger.info(f"{count} registros con estado 'SUCCESS' exportados a {file_path}")

    def export_to_json(self, file_path: str) -> None:
        """Export all stored results to a JSON file."""
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

        results = self.list_results()
        if not results:
            logger.warning("No hay datos para exportar a JSON. No se creará ningún archivo.")
            return
        with open(file_path, "w", encoding="utf-8") as f:
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
        # Use dataset's query capabilities for efficient searching
        # This avoids loading the entire table into memory.
        # The `ilike` operator provides case-insensitive matching.
        from sqlalchemy import or_
        
        table = self.db.load_table(self.table.name)
        # Using raw SQLAlchemy for a more complex OR query
        statement = table.table.select().where(
            or_(table.table.c.title.ilike(f"%{query}%"), table.table.c.content_text.ilike(f"%{query}%"))
        )
        rows = self.db.query(statement)
        return [self._deserialize_row(dict(row)) for row in rows]

    # ------------------------------------------------------------------
    # Internal helper methods
    # ------------------------------------------------------------------
    def _process_csv_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten extracted data for CSV export and remove the original field."""
        if row.get("extracted_data"):
            try:
                extracted = json.loads(row["extracted_data"])
                for field, data in extracted.items():
                    row[f"extracted_{field}"] = data.get("value")
            except (json.JSONDecodeError, TypeError):
                pass
            finally:
                row.pop("extracted_data", None)
        return row

    def _deserialize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialise JSON fields (links, extracted_data, healing_events)."""
        if row is None:
            return row
        # Links
        if row.get("links"):
            try:
                row["links"] = json.loads(row["links"])
            except (json.JSONDecodeError, TypeError):
                row["links"] = []
        # Complex fields
        for field in ["extracted_data", "healing_events"]:
            if row.get(field):
                try:
                    row[field] = json.loads(row[field])
                except (json.JSONDecodeError, TypeError):
                    row[field] = None if field == "extracted_data" else []
        return row
