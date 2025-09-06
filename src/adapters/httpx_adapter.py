"""
Adaptador HTTPX para peticiones HTTP resilientes.

Proporciona una interfaz asíncrona mínima para obtener HTML y JSON encapsulando
retries, timeouts y conversión de errores en excepciones controladas.

Diseño:
- Usa httpx.AsyncClient interno (inyección opcional para tests).
- Retries exponenciales simples sobre errores de red / timeouts / 5xx.
- Método `close()` para liberar recursos cuando se usa fuera de context manager.
- Preparado para ser mockeado en tests mediante `httpx.MockTransport`.

Interfaz pública:
- fetch_html(url, *, timeout=..., max_retries=...)
- fetch_json(url, *, timeout=..., max_retries=...)

No lanza excepciones sin envolver: re-lanza RuntimeError con mensaje estable.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

try:
    import httpx  # type: ignore

    HTTPX_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin dependencia
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore

logger = logging.getLogger(__name__)


class HttpxAdapter:
    def __init__(self, client: Optional["httpx.AsyncClient"] = None) -> None:  # type: ignore[name-defined]
        if not HTTPX_AVAILABLE:
            raise RuntimeError(
                "httpx no está disponible. Instale con: pip install httpx"
            )
        self._own_client = client is None
        self.client = client or httpx.AsyncClient(timeout=None, follow_redirects=True)

    async def fetch_html(
        self,
        url: str,
        *,
        timeout: float = 15.0,
        max_retries: int = 2,
        backoff_base: float = 0.5,
    ) -> str:
        response = await self._request(
            "GET",
            url,
            timeout=timeout,
            max_retries=max_retries,
            backoff_base=backoff_base,
        )
        return response.text

    async def fetch_json(
        self,
        url: str,
        *,
        timeout: float = 15.0,
        max_retries: int = 2,
        backoff_base: float = 0.5,
    ) -> Any:
        response = await self._request(
            "GET",
            url,
            timeout=timeout,
            max_retries=max_retries,
            backoff_base=backoff_base,
        )
        try:
            return response.json()
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"Error parseando JSON desde {url}: {e}") from e

    async def _request(
        self,
        method: str,
        url: str,
        *,
        timeout: float,
        max_retries: int,
        backoff_base: float,
    ):
        attempt = 0
        last_exc: Optional[Exception] = None
        while attempt <= max_retries:
            try:
                response = await self.client.request(method, url, timeout=timeout)
                if response.status_code >= 500:
                    if attempt < max_retries:
                        # Solo reintenta si no hemos agotado los reintentos
                        raise RuntimeError(f"HTTP {response.status_code} (reintento)")
                    else:
                        # Si agotamos los reintentos, lanza error
                        msg = f"Fallo HTTP tras {attempt+1} intentos para {url}: HTTP {response.status_code}"
                        logger.warning(msg)
                        raise RuntimeError(msg)
                return response
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt >= max_retries:
                    msg = f"Fallo HTTP tras {attempt+1} intentos para {url}: {exc}"  # noqa: E501
                    logger.warning(msg)
                    raise RuntimeError(msg) from exc
                sleep_for = backoff_base * (2**attempt)
                await asyncio.sleep(sleep_for)
                attempt += 1
        # Debe haberse devuelto o lanzado antes; este return es defensivo
        raise RuntimeError(f"Fallo HTTP inesperado para {url}: {last_exc}")

    async def close(self) -> None:
        if self._own_client:
            try:
                await self.client.aclose()
            except Exception:  # noqa: BLE001
                pass

    async def __aenter__(self) -> "HttpxAdapter":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
