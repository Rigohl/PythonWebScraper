"""
Smoke tests to verify that all major components can be imported without errors.

This test suite helps catch ModuleNotFoundError and other import-related issues
early in the development cycle, especially after refactoring.
"""

import pytest


def test_tui_app_can_be_imported():
    """
    Verifies that the main TUI application and its dependencies can be imported.
    """
    try:
        from src.tui.app import ScraperTUIApp
    except ImportError as e:
        pytest.fail(f"Failed to import ScraperTUIApp due to an ImportError: {e}")


def test_orchestrator_and_dependencies_can_be_imported():
    """
    Verifies that the ScrapingOrchestrator and its dependencies can be imported.
    """
    try:
        from src.orchestrator import ScrapingOrchestrator
    except ImportError as e:
        pytest.fail(f"Failed to import ScrapingOrchestrator due to an ImportError: {e}")
