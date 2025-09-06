"""
Adaptadores para encapsular dependencias externas.

Este módulo contiene adaptadores que encapsulan las llamadas a librerías externas
como Playwright, HTTPX, OpenAI, etc. Esto facilita el testing y reduce el acoplamiento.
"""

from __future__ import annotations

__all__ = ["browser_adapter", "httpx_adapter", "llm_adapter"]

# Lightweight logger setup for adapters package
import logging

logging.getLogger("src.adapters").addHandler(logging.NullHandler())
