"""Unit tests for the AdvancedScraper helper methods.

These tests exercise the pure functions ``_classify_content`` and
``_validate_content_quality`` to ensure they behave correctly given a
variety of inputs. Because Playwright is not available in the test
environment, we only cover methods that do not require a browser
context. Running these tests requires pytest and the project modules.
"""

import pytest

from src.scraper import AdvancedScraper
from src.settings import settings


class DummyScraper(AdvancedScraper):
    """Subclass of AdvancedScraper that bypasses the need for a Page.

    The base ``AdvancedScraper`` expects a Playwright Page, DatabaseManager
    and LLMExtractor. For testing the helper methods we don't need
    those dependencies, so this dummy subclass passes ``None`` values.
    """

    def __init__(self) -> None:
        # Pass None for page, db_manager and llm_extractor.  These fields
        # are not accessed in the methods under test.
        super().__init__(page=None, db_manager=None, llm_extractor=None)  # type: ignore


def test_classify_product() -> None:
    scraper = DummyScraper()
    result = scraper._classify_content("Comprar telefono", "Este articulo te muestra el precio")
    assert result == "PRODUCT"


def test_classify_blog_post() -> None:
    scraper = DummyScraper()
    result = scraper._classify_content("Blog de noticias", "Leer más sobre eventos")
    assert result == "BLOG_POST"


def test_classify_article() -> None:
    scraper = DummyScraper()
    result = scraper._classify_content("Guia definitiva", "Un tutorial completo")
    assert result == "ARTICLE"


def test_classify_general() -> None:
    scraper = DummyScraper()
    long_text = "a" * (settings.MIN_CONTENT_LENGTH + 10)
    result = scraper._classify_content("", long_text)
    assert result == "GENERAL"


def test_classify_unknown() -> None:
    scraper = DummyScraper()
    result = scraper._classify_content("", "breve")
    assert result == "UNKNOWN"


def test_validate_empty_content_raises() -> None:
    scraper = DummyScraper()
    with pytest.raises(Exception):
        scraper._validate_content_quality("", "Titulo")


def test_validate_too_short_raises() -> None:
    scraper = DummyScraper()
    short_text = "a" * (settings.MIN_CONTENT_LENGTH - 5)
    with pytest.raises(Exception):
        scraper._validate_content_quality(short_text, "Titulo")


def test_validate_forbidden_phrase_raises() -> None:
    scraper = DummyScraper()
    forbidden = settings.FORBIDDEN_PHRASES[0]
    with pytest.raises(Exception):
        scraper._validate_content_quality(f"Este texto contiene {forbidden}", "Titulo")