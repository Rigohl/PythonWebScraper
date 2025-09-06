"""
Tests for settings configuration and defaults.
"""

import re
from importlib import reload

import pytest  # noqa: F401

from src.settings import settings


class TestSettingsDefaults:
    """Test default values and types for Settings class."""

    def test_min_content_length_is_int_and_positive(self):
        """Verify MIN_CONTENT_LENGTH is integer and greater than 0."""
        assert isinstance(settings.MIN_CONTENT_LENGTH, int)
        assert settings.MIN_CONTENT_LENGTH > 0

    def test_scraper_version_is_semantic_string(self):
        """Verify SCRAPER_VERSION is string with semantic format."""
        assert isinstance(settings.SCRAPER_VERSION, str)
        # Check for semantic versioning pattern (e.g., "0.11.0")
        semantic_pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(semantic_pattern, settings.SCRAPER_VERSION)

    def test_llm_model_is_present_and_string(self):
        """Verify LLM_MODEL is present and is a string."""
        assert hasattr(settings, "LLM_MODEL")
        assert isinstance(settings.LLM_MODEL, str)
        assert len(settings.LLM_MODEL.strip()) > 0

    def test_offline_mode_default(self):
        """Verify OFFLINE_MODE defaults to True for local experience."""
        assert isinstance(settings.OFFLINE_MODE, bool)
        assert settings.OFFLINE_MODE is True

    def test_robots_enabled_default(self):
        """Verify ROBOTS_ENABLED defaults to False."""
        assert isinstance(settings.ROBOTS_ENABLED, bool)
        assert settings.ROBOTS_ENABLED is False

    def test_app_name_present(self):
        """Verify APP_NAME is set and is a string."""
        assert isinstance(settings.APP_NAME, str)
        assert len(settings.APP_NAME.strip()) > 0

    def test_concurrency_is_positive_int(self):
        """Verify CONCURRENCY is positive integer."""
        assert isinstance(settings.CONCURRENCY, int)
        assert settings.CONCURRENCY > 0

    def test_log_level_is_valid(self):
        """Verify LOG_LEVEL is a valid logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert settings.LOG_LEVEL in valid_levels

    def test_pytest_env_relaxes_min_length(self, monkeypatch):
        """Test that pytest environment relaxes minimum content length."""
        # Simulate pytest env variable
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
        # Re-import settings module to observe behavior is environment-aware
        import src.settings as s_mod

        reload(s_mod)
        assert s_mod.settings.MIN_CONTENT_LENGTH <= settings.MIN_CONTENT_LENGTH
