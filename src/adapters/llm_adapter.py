"""
Adaptador para LLM con interfaz abstracta.

Este módulo define una interfaz abstracta para operaciones de LLM
y una implementación concreta usando OpenAI/Instructor. Facilita el testing con mocks.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

try:
    import instructor  # type: ignore
    from openai import OpenAI, APIError, APITimeoutError, APIConnectionError  # type: ignore
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    # Definir excepciones mínimas para cuando OpenAI no esté disponible
    class APIError(Exception):  # type: ignore
        pass

    class APITimeoutError(Exception):  # type: ignore
        pass

    class APIConnectionError(Exception):  # type: ignore
        pass

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMAdapter(ABC):
    """Interfaz abstracta para operaciones de LLM."""

    @abstractmethod
    async def clean_text(self, text: str) -> str:
        """Limpiar texto usando LLM."""
        pass

    @abstractmethod
    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Extraer datos estructurados usando LLM."""
        pass

    @abstractmethod
    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Resumir contenido usando LLM."""
        pass

    @abstractmethod
    def extract_sync(self, html_content: str, response_model: Type[T]) -> T:
        """Método síncrono legacy para compatibilidad con tests."""
        pass


class OpenAIAdapter(LLMAdapter):
    """Implementación concreta del adaptador usando OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo") -> None:
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI no está disponible. Instale con: pip install openai instructor")

        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

        try:
            self.client = instructor.patch(OpenAI(api_key=api_key))
            self.logger.info("Cliente OpenAI inicializado correctamente.")
        except Exception as e:
            self.logger.error(f"Error inicializando cliente OpenAI: {e}")
            raise

    async def clean_text(self, text: str) -> str:
        """Limpiar texto usando OpenAI."""
        if not text.strip():
            return text

        class CleanedText(BaseModel):
            cleaned_text: str

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_model=CleanedText,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert in cleaning HTML content. Remove navigation, "
                            "footer, ads, pop-ups, legal and boilerplate; return ONLY core "
                            "article/body text."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
            )
            return response.cleaned_text
        except (APIError, APITimeoutError, APIConnectionError) as e:
            self.logger.warning(f"Error en API de OpenAI para limpieza de texto: {e}")
            return text
        except Exception as e:
            self.logger.error(f"Error inesperado en limpieza de texto: {e}")
            return text

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Extraer datos estructurados usando OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract structured data matching the provided Pydantic schema "
                            "from the HTML. If a field is absent, leave it empty."
                        ),
                    },
                    {"role": "user", "content": html_content},
                ],
            )
            self.logger.info(f"Extracción estructurada completada para {response_model.__name__}")
            return response
        except (APIError, APITimeoutError, APIConnectionError) as e:
            self.logger.warning(f"Error en API de OpenAI para extracción estructurada: {e}")
            return response_model()
        except Exception as e:
            self.logger.error(f"Error inesperado en extracción estructurada: {e}")
            return response_model()

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Resumir contenido usando OpenAI."""
        if not text_content.strip():
            return ""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"Summarize the following text in about {max_words} words, "
                            "concise and factual."
                        ),
                    },
                    {"role": "user", "content": text_content},
                ],
                temperature=0.4,
                max_tokens=max_words * 2,
            )
            summary = response.choices[0].message.content
            return summary or ""
        except (APIError, APITimeoutError, APIConnectionError) as e:
            self.logger.warning(f"Error en API de OpenAI para resumen: {e}")
            # Fallback: primeras palabras
            import re
            words = re.split(r"\s+", text_content)
            return " ".join(words[:max_words])
        except Exception as e:
            self.logger.error(f"Error inesperado en resumen: {e}")
            import re
            words = re.split(r"\s+", text_content)
            return " ".join(words[:max_words])

    def extract_sync(self, html_content: str, response_model: Type[T]) -> T:
        """Método síncrono legacy para compatibilidad."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=response_model,
                messages=[
                    {"role": "system", "content": "Extract structured data."},
                    {"role": "user", "content": html_content},
                ],
            )
            return response
        except Exception:
            return response_model()


class OfflineLLMAdapter(LLMAdapter):
    """Implementación offline/mock para testing y modo sin conexión."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Adaptador LLM offline inicializado.")

    async def clean_text(self, text: str) -> str:
        """Limpieza básica sin LLM."""
        # Limpieza simple: remover exceso de espacios
        import re
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Crear instancia vacía del modelo."""
        return response_model()

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Resumen simple: primeras palabras."""
        import re
        words = re.split(r"\s+", text_content)
        return " ".join(words[:max_words])

    def extract_sync(self, html_content: str, response_model: Type[T]) -> T:
        """Método síncrono legacy."""
        from pydantic.fields import FieldInfo

        # Fabricar objeto con valores por defecto
        values = {}
        for name, model_field in response_model.model_fields.items():
            fi: FieldInfo = model_field
            if fi.default is not None or fi.default_factory is not None:
                values[name] = fi.default
                continue
            ann = fi.annotation
            if ann is int:
                values[name] = 0
            elif ann is float:
                values[name] = 0.0
            elif ann is bool:
                values[name] = False
            else:
                values[name] = ""

        try:
            return response_model.model_construct(**values)
        except Exception:
            return response_model(**{k: v for k, v in values.items() if v not in (None,)})


class MockLLMAdapter(LLMAdapter):
    """Implementación mock para testing avanzado."""

    def __init__(self, mock_responses: dict = None) -> None:
        self.mock_responses = mock_responses or {}
        self.call_count = 0

    async def clean_text(self, text: str) -> str:
        """Mock de limpieza."""
        self.call_count += 1
        return self.mock_responses.get("clean_text", f"cleaned: {text}")

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """Mock de extracción estructurada."""
        self.call_count += 1
        if "extract_data" in self.mock_responses:
            return self.mock_responses["extract_data"]
        return response_model()

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str:
        """Mock de resumen."""
        self.call_count += 1
        return self.mock_responses.get("summarize", f"summary of {text_content[:50]}...")

    def extract_sync(self, html_content: str, response_model: Type[T]) -> T:
        """Mock síncrono."""
        self.call_count += 1
        if "extract_sync" in self.mock_responses:
            return self.mock_responses["extract_sync"]
        return response_model()
