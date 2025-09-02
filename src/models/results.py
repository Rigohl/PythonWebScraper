from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from ..settings import settings


class RetryableError(Exception):
    """Excepción personalizada para errores que permiten reintentos."""

class ScrapeResult(BaseModel):
    """Modelo de datos para el resultado de un scrape, validado con Pydantic."""
    status: str
    url: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) # noqa
    scraper_version: str = settings.SCRAPER_VERSION

    # Core content
    title: Optional[str] = None
    content_text: Optional[str] = None # El texto final, limpio por IA.
    content_html: Optional[str] = None # El HTML principal de readability.
    links: List[str] = Field(default_factory=list)

    # Self-healing and structured data
    extracted_data: Optional[dict] = None
    healing_events: Optional[List[dict]] = None

    # Metadata and metrics
    content_hash: Optional[str] = None
    visual_hash: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False
    http_status_code: Optional[int] = None
    content_type: Optional[str] = None # e.g., PRODUCT, BLOG_POST
    crawl_duration: Optional[float] = None
    llm_summary: Optional[str] = None
    llm_extracted_data: Optional[dict] = None
