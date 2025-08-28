"""
Database management for the improved Web Scraper PRO.

This module wraps the ``dataset`` library to provide a thin abstraction over
SQLite. It exposes convenience methods for saving and retrieving scrape
results, managing cookies and dynamically learned LLM extraction schemas and
APIs, and exporting results to CSV or JSON. Additional helpers allow quick
listing and searching of stored pages so that the TUI can visualise data
without reinventing SQL queries.

The original project used ``dataset`` exclusively. That library is retained
here for backwards compatibility, but callers should consider migrating to
a more robust backend (e.g. PostgreSQL or a graph database) when scaling
beyond a single machine. This wrapper makes such a migration easier in the
future by centralising all database access in one place.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import dataset  # type: ignore

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage persistence of scrape results and related metadata."""

    def __init__(self, db_path: Optional[str] = None, db_connection: Any = None) -> None:
        if db_connection is not None:
            self.db = db_connection
        elif db_path:
            # Ensure directory exists before connecting
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.db = dataset.connect(f"sqlite:///{db_path}")
        else:
            raise ValueError("DatabaseManager requires a path or an existing connection")

        # Primary tables
        self.table = self.db["pages"]
        self.apis_table = self.db["discovered_apis"]
        self.cookies_table = self.db["cookies"]
        self.llm_schemas_table = self.db["llm_extraction_schemas"]

    # -------------------------------------------------------------------------
    # API discovery persistence
    # -------------------------------------------------------------------------
    def save_discovered_api(self, page_url: str, api_url: str, payload_hash: str) -> None:
        data = {
            "page_url": page_url,
            "api_url": api_url,
            "payload_hash": payload_hash,
            "timestamp": datetime.now(timezone.utc),
        }
        # Upsert avoids duplicates based on composite key
        self.apis_table.upsert(data, ["page_url", "api_url", "payload_hash"])
        logger.info("API descubierta en %s: %s", page_url, api_url)

    # -------------------------------------------------------------------------
    # Cookie persistence
    # -------------------------------------------------------------------------
    def save_cookies(self, domain: str, cookies_json: str) -> None:
        data = {
            "domain": domain,
            "cookies": cookies_json,
            "timestamp": datetime.now(timezone.utc),
        }
        self.cookies_table.upsert(data, ["domain"])
        logger.debug("Cookies guardadas para el dominio: %s", domain)

    def load_cookies(self, domain: str) -> Optional[str]:
        row = self.cookies_table.find_one(domain=domain)
        return row["cookies"] if row else None

    # -------------------------------------------------------------------------
    # LLM schema persistence
    # -------------------------------------------------------------------------
    def save_llm_extraction_schema(self, domain: str, schema_json: str) -> None:
        data = {
            "domain": domain,
            "schema": schema_json,
            "timestamp": datetime.now(timezone.utc),
        }
        self.llm_schemas_table.upsert(data, ["domain"])
        logger.debug("Esquema LLM guardado para el dominio: %s", domain)

    def load_llm_extraction_schema(self, domain: str) -> Optional[str]:
        row = self.llm_schemas_table.find_one(domain=domain)
        return row["schema"] if row else None

    # -------------------------------------------------------------------------
    # Result persistence and retrieval
    # -------------------------------------------------------------------------
    def save_result(self, result: Any) -> None:
        """Persist a ``ScrapeResult`` into the pages table.

        The result is converted to JSON where necessary and upserted based on
        its URL. Duplicate content detection based on ``content_hash`` happens
        before insertion to avoid storing redundant pages.
        """
        # Check for duplicate content
        content_hash = getattr(result, "content_hash", None)
        if content_hash:
            existing = self.table.find_one(content_hash=content_hash)
            if existing and existing.get("url") != result.url:
                logger.info(
                    "Contenido duplicado detectado para %s. Original: %s. Marcando como DUPLICATE.",
                    result.url,
                    existing["url"],
                )
                result.status = "DUPLICATE"

        # Convert Pydantic model to dict
        data = result.model_dump(mode="json") if hasattr(result, "model_dump") else dict(result)

        # Serialise complex fields
        if "links" in data and data["links"] is not None:
            data["links"] = json.dumps(data["links"])
        if "extracted_data" in data and data["extracted_data"] is not None:
            data["extracted_data"] = json.dumps(data["extracted_data"])
        if "healing_events" in data and data["healing_events"] is not None:
            data["healing_events"] = json.dumps(data["healing_events"])

        self.table.upsert(data, ["url"])
        logger.debug("Resultado para %s guardado en la base de datos.", result.url)

    def get_result_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        row = self.table.find_one(url=url)
        if not row:
            return None

        # Deserialise JSON fields back to Python objects
        for field in ("links", "extracted_data", "healing_events"):
            if row.get(field):
                try:
                    row[field] = json.loads(row[field])
                except (json.JSONDecodeError, TypeError):
                    row[field] = [] if field == "links" else None
        return row

    # -------------------------------------------------------------------------
    # Listing and searching helpers
    # -------------------------------------------------------------------------
    def list_results(self, status_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Return a list of stored pages optionally filtered by status.

        Parameters
        ----------
        status_filter: str, optional
            If provided, restrict to results with this ``status`` (e.g.
            "SUCCESS", "FAILED").
        limit: int
            Maximum number of rows to return. ``0`` or a negative value
            returns all rows.
        """
        if status_filter:
            iterator = self.table.find(status=status_filter)
        else:
            iterator = self.table.all()
        results: List[Dict[str, Any]] = []
        for i, row in enumerate(iterator):
            # Break early if limit reached
            if limit > 0 and i >= limit:
                break
            results.append(row)
        return results

    def search_results(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search stored pages by title or URL substring.

        The search is case‑insensitive and operates in Python space. For small
        datasets this is sufficient, but for large databases consider using
        SQLite full‑text search (FTS) for better performance.
        """
        keyword_lower = keyword.lower()
        results: List[Dict[str, Any]] = []
        for row in self.table.all():
            title = (row.get("title") or "").lower()
            url = (row.get("url") or "").lower()
            if keyword_lower in title or keyword_lower in url:
                results.append(row)
                if limit > 0 and len(results) >= limit:
                    break
        return results

    # -------------------------------------------------------------------------
    # Export helpers
    # -------------------------------------------------------------------------
    def export_to_csv(self, file_path: str) -> None:
        """Export all successful pages to a CSV file.

        If no records with status ``SUCCESS`` exist, no file is produced.
        """
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)
        results_iterator = self.table.find(status="SUCCESS")
        first_result = next(results_iterator, None)
        if not first_result:
            logger.warning("No hay datos con estado 'SUCCESS' para exportar.")
            return
        import csv
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            processed_first = self._process_csv_row(dict(first_result))
            fieldnames = processed_first.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(processed_first)
            count = 1
            for row in results_iterator:
                processed_row = self._process_csv_row(dict(row))
                writer.writerow({k: processed_row.get(k) for k in fieldnames})
                count += 1
        logger.info("%s registros exportados a %s", count, file_path)

    def export_to_json(self, file_path: str, status_filter: Optional[str] = "SUCCESS") -> None:
        """Export pages to a JSON file.

        Parameters
        ----------
        file_path: str
            Destination path. Directories will be created if necessary.
        status_filter: str, optional
            Restrict export to results with this status. Pass ``None`` to
            export all records.
        """
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)
        if status_filter:
            rows = list(self.table.find(status=status_filter))
        else:
            rows = list(self.table.all())
        with open(file_path, "w", encoding="utf-8") as f:
            # Serialise lists of rows directly; dataset rows are dict‑like
            json.dump([dict(r) for r in rows], f, ensure_ascii=False, indent=2, default=str)
        logger.info("%s registros exportados a %s", len(rows), file_path)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _process_csv_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten extracted data and drop complex objects for CSV export."""
        extracted = row.get("extracted_data")
        if extracted:
            try:
                data = json.loads(extracted) if isinstance(extracted, str) else extracted
                for field, value in data.items():
                    # Only persist the value component for CSV readability
                    if isinstance(value, dict):
                        row[f"extracted_{field}"] = value.get("value")
                    else:
                        row[f"extracted_{field}"] = value
            except Exception:
                pass
        # Remove heavy fields
        row.pop("extracted_data", None)
        row.pop("healing_events", None)
        # Deserialise JSON lists
        links = row.get("links")
        if links:
            try:
                row["links"] = ", ".join(json.loads(links))
            except Exception:
                pass
        return row