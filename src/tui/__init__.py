# src/tui/__init__.py

"""
TUI (Text User Interface) module for Web Scraper PRO

This module provides both the original TUI and the new professional dashboard
interface for the web scraper system.
"""

# Original TUI for backward compatibility
from .app import ScraperTUIApp

# New Professional TUI
from .professional_app import WebScraperProfessionalApp, run_professional_app

__all__ = [
    "ScraperTUIApp",  # Original TUI
    "WebScraperProfessionalApp",  # New Professional TUI
    "run_professional_app",  # Entry point for professional app
]
