"""
Language model helper utilities.

This module exposes an ``LLMExtractor`` class that encapsulates calls to a
Large Language Model (LLM) for tasks such as cleaning HTML, extracting
structured data into Pydantic models and summarising long passages of text.
When the OpenAI API key is unavailable or when an API call fails, the
extractor falls back to simple deterministic logic so that the rest of
the pipeline can continue without throwing exceptions.  This design makes
the scraper resilient in offline environments and simplifies testing.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Type, TypeVar, Optional

try:
    import instructor
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    # If the OpenAI SDK or instructor is not installed, we mark the client as unavailable.
    OPENAI_AVAILABLE = False

from pydantic import BaseModel, create_model
from src.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMExtractor:
    """Envoltura para un Modelo de Lenguaje para limpiar, extraer y resumir.

    Al instanciarse, el extractor intenta construir un cliente de OpenAI
    parcheado por ``instructor``. Si la clave de API no está configurada o
    faltan las dependencias requeridas, el extractor operará en modo offline
    y se basará en una lógica de respaldo determinista.
    """

    def __init__(self) -> None:
        self.client: Optional[Any] = None
        if OPENAI_AVAILABLE and settings.LLM_API_KEY:
            try:
                self.client = instructor.patch(OpenAI(api_key=settings.LLM_API_KEY))
                logger.info("LLMExtractor inicializado con el cliente de OpenAI parcheado.")
            except Exception as e:
                logger.error(f"Error inicializando OpenAI client: {e}")
        else:
            logger.warning("LLM API no configurada o dependencias faltantes; se usará modo offline.")

    async def clean_text_content(self, text: str) -> str:
        """Limpia texto HTML usando un LLM o recurre a heurísticas simples.

        El prompt de limpieza instruye al LLM para que elimine barras de
        navegación, pies de página y otros elementos no esenciales. Si la
        llamada falla o el modo offline está activo, este método devuelve el
        texto original. En modo offline, se podría extender con un filtro
        simple de "readability".
        """
        if not self.client:
            # Fallback: no cleaning performed.
            return text
        try:
            class CleanedText(BaseModel):
                cleaned_text: str
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                response_model=CleanedText,
                messages=[
                    {"role": "system", "content": "Eres un experto en limpiar contenido HTML. Tu tarea es eliminar todo el texto que no sea el contenido principal de la página, como barras de navegación, pies de página, anuncios, pop-ups y texto legal. Devuelve únicamente el contenido principal."},
                    {"role": "user", "content": text},
                ],
            )
            return response.cleaned_text
        except Exception as e:
            logger.error(f"Error durante la limpieza de texto con LLM: {e}", exc_info=True)
            return text

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Realiza una extracción "zero-shot" de datos estructurados desde HTML.

        Cuando el LLM no está disponible, este método devuelve una instancia
        vacía de ``response_model`` para que el código que lo llama pueda
        proceder sin fallar.
        """
        if not self.client:
            return response_model()
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                response_model=response_model,
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción de datos de páginas web. Tu tarea es analizar el siguiente contenido HTML y rellenar el esquema Pydantic proporcionado con la información encontrada. Extrae los datos de la forma más precisa posible."},
                    {"role": "user", "content": html_content},
                ],
            )
            logger.info(f"Extracción Zero-Shot exitosa para el modelo {response_model.__name__}.")
            return response
        except Exception as e:
            logger.error(f"Error durante la extracción Zero-Shot con LLM: {e}", exc_info=True)
            return response_model()

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Resume un bloque de texto usando el LLM o una alternativa simple.

        Si no se puede llamar al LLM, se aplica una heurística simple de
        resumen: se devuelven las primeras ``max_words`` palabras. En
        producción, esto podría reemplazarse con un resumidor offline más
        sofisticado, como un extractor basado en frecuencia.
        """
        if not self.client:
            # Naive summarisation: return the first ``max_words`` words.
            words = re.split(r"\s+", text_content)
            return " ".join(words[:max_words])
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"Eres un asistente útil. Resume el siguiente texto en aproximadamente {max_words} palabras."},
                    {"role": "user", "content": text_content},
                ],
                temperature=0.7,
                max_tokens=max_words * 2,
            )
            # The OpenAI API returns a list of choices; pick the first.
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al sumarizar contenido con LLM: {e}", exc_info=True)
            return text_content[: max_words * 10]
