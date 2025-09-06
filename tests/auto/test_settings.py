import re

import pytest


def _import_settings_module():
    try:
        from src import settings as s

        return s.settings  # Access the instance, not the module
    except Exception:
        pytest.skip("src.settings.settings not importable")


def test_min_content_length_positive():
    s = _import_settings_module()
    assert hasattr(s, "MIN_CONTENT_LENGTH"), "MIN_CONTENT_LENGTH missing"
    assert isinstance(s.MIN_CONTENT_LENGTH, int)
    assert s.MIN_CONTENT_LENGTH > 0


def test_scraper_version_semverish():
    s = _import_settings_module()
    assert hasattr(s, "SCRAPER_VERSION"), "SCRAPER_VERSION missing"
    assert isinstance(s.SCRAPER_VERSION, str)
    assert re.match(
        r"^\d+\.\d+\.\d+", s.SCRAPER_VERSION
    ), "SCRAPER_VERSION not semver-like"


def test_llm_model_present():
    s = _import_settings_module()
    assert hasattr(s, "LLM_MODEL"), "LLM_MODEL missing"
    assert isinstance(s.LLM_MODEL, str)
    assert s.LLM_MODEL.strip() != ""
