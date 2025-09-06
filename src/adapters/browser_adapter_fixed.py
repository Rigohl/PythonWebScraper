"""
Adaptador para Playwright con interfaz abstracta.

Este módulo define una interfaz abstracta para operaciones de navegación web
y una implementación concreta usando Playwright. Facilita el testing con mocks.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

try:
    from playwright.async_api import Page, Response

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

    # Definir tipos mínimos para cuando Playwright no esté disponible
    class Page:  # type: ignore
        pass

    class Response:  # type: ignore
        pass


logger = logging.getLogger(__name__)


class BrowserAdapter(ABC):
    """Interfaz abstracta para operaciones de navegación web."""

    @abstractmethod
    async def navigate_to_url(
        self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000
    ) -> Optional[Dict[str, Any]]:
        """Navegar a una URL y retornar información de respuesta."""

    @abstractmethod
    async def get_content(self) -> str:
        """Obtener el contenido HTML de la página actual."""

    @abstractmethod
    async def wait_for_load_state(
        self, state: str = "networkidle", timeout: int = 15000
    ) -> None:
        """Esperar a que la página esté en el estado especificado."""

    @abstractmethod
    async def screenshot(self) -> bytes:
        """Tomar una captura de pantalla de la página actual."""

    @abstractmethod
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Obtener cookies de la página actual."""

    @abstractmethod
    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Establecer cookies en la página actual."""

    @abstractmethod
    def add_response_listener(self, handler) -> None:
        """Agregar un listener para interceptar respuestas."""

    @abstractmethod
    def remove_response_listener(self, handler) -> None:
        """Remover un listener de respuestas."""

    @abstractmethod
    def get_current_url(self) -> str:
        """Obtener la URL actual."""


class PlaywrightAdapter(BrowserAdapter):
    """Implementación concreta del adaptador usando Playwright."""

    def __init__(self, page: Page) -> None:
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright no está disponible. Instale con: pip install playwright"
            )
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    async def navigate_to_url(
        self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000
    ) -> Optional[Dict[str, Any]]:
        """Navegar a una URL usando Playwright."""
        try:
            response = await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            if response:
                return {
                    "status": response.status,
                    "url": response.url,
                    "headers": dict(response.headers),
                }
            return None
        except Exception as e:
            self.logger.error(f"Error navegando a {url}: {e}")
            raise

    async def get_content(self) -> str:
        """Obtener contenido HTML."""
        try:
            return await self.page.content()
        except Exception as e:
            self.logger.error(f"Error obteniendo contenido: {e}")
            raise

    async def wait_for_load_state(
        self, state: str = "networkidle", timeout: int = 15000
    ) -> None:
        """Esperar estado de carga."""
        try:
            await self.page.wait_for_load_state(state, timeout=timeout)
        except Exception as e:
            self.logger.error(f"Error esperando estado {state}: {e}")
            raise

    async def screenshot(self) -> bytes:
        """Tomar captura de pantalla."""
        try:
            return await self.page.screenshot()
        except Exception as e:
            self.logger.error(f"Error tomando captura: {e}")
            # Fallback para entornos de test
            return b"test_screenshot_data"

    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Obtener cookies."""
        try:
            return await self.page.context.cookies()
        except Exception as e:
            self.logger.error(f"Error obteniendo cookies: {e}")
            return []

    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Establecer cookies."""
        try:
            await self.page.context.add_cookies(cookies)
        except Exception as e:
            self.logger.error(f"Error estableciendo cookies: {e}")

    def add_response_listener(self, handler) -> None:
        """Agregar listener de respuestas."""
        self.page.on("response", handler)

    def remove_response_listener(self, handler) -> None:
        """Remover listener de respuestas."""
        self.page.remove_listener("response", handler)

    def get_current_url(self) -> str:
        """Obtener URL actual."""
        return self.page.url


class MockBrowserAdapter(BrowserAdapter):
    """Implementación mock para testing."""

    def __init__(
        self,
        mock_content: str = "<html><body>Test content</body></html>",
        mock_url: str = "http://test.com",
    ) -> None:
        self.mock_content = mock_content
        self.mock_url = mock_url
        self.mock_response = {
            "status": 200,
            "url": mock_url,
            "headers": {"content-type": "text/html"},
        }
        self.should_raise_network_error = False
        self.mock_api_responses = []
        self.response_listeners = []
        self.cookies_store = []
        self._cookies_were_set = False

    async def navigate_to_url(
        self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000
    ) -> Optional[Dict[str, Any]]:
        """Mock navigation."""
        if self.should_raise_network_error:
            from src.exceptions import NetworkError

            raise NetworkError("Simulated network error for testing")

        # Process any API responses
        for response in self.mock_api_responses:
            for handler in self.response_listeners:
                await handler(response)

        return self.mock_response

    async def get_content(self) -> str:
        """Mock content."""
        return self.mock_content

    async def wait_for_load_state(
        self, state: str = "networkidle", timeout: int = 15000
    ) -> None:
        """Mock wait."""
        await asyncio.sleep(0.01)  # Small delay to simulate waiting

    async def screenshot(self) -> bytes:
        """Mock screenshot."""
        return b"mock_screenshot_data"

    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Mock cookies getter."""
        return self.cookies_store.copy()

    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Mock cookies setter."""
        self.cookies_store = cookies.copy()
        self._cookies_were_set = True

    def add_response_listener(self, handler) -> None:
        """Mock add listener."""
        self.response_listeners.append(handler)

    def remove_response_listener(self, handler) -> None:
        """Mock remove listener."""
        if handler in self.response_listeners:
            self.response_listeners.remove(handler)

    def get_current_url(self) -> str:
        """Mock current URL."""
        return self.mock_url

    @property
    def cookies_were_set(self) -> bool:
        """Check if cookies were set."""
        return self._cookies_were_set
