import logging
import openai
import instructor
from pydantic import BaseModel, create_model # Added create_model and BaseModel
from typing import Type # Added Type

logger = logging.getLogger(__name__)

class LLMExtractor:
    """
    Clase para la integración con Modelos de Lenguaje Grandes (LLMs),
    ahora con extracción estructurada real usando Pydantic.
    """
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            instructor.patch(self.client)
            logger.info("LLMExtractor inicializado con API Key y cliente OpenAI parcheado.")
        else:
            logger.warning("LLMExtractor inicializado sin API Key. Las funcionalidades LLM reales no estarán disponibles.")

    async def extract_structured_data(self, html_content: str, schema_dict: dict) -> dict | None:
        """
        Extrae datos estructurados usando un LLM y un esquema Pydantic dinámico.
        `schema_dict` debe ser un diccionario que describa un modelo Pydantic,
        por ejemplo: {"name": (str, ...), "price": (float, ...)}.
        """
        if not self.client:
            logger.warning("LLM no configurado, no se puede realizar la extracción estructurada.")
            return None
        
        if not schema_dict:
            logger.debug("No se proporcionó un esquema para la extracción LLM estructurada.")
            return None

        try:
            # Construir dinámicamente el modelo Pydantic a partir del diccionario
            DynamicSchema = create_model('DynamicSchema', **{
                field: (field_type, ...) for field, field_type in schema_dict.items()
            }) # Default value should be Ellipsis (...) for required fields

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # O el modelo que se prefiera
                response_model=DynamicSchema,
                messages=[
                    {"role": "system", "content": "You are an expert data extraction bot. Extract information from the provided HTML content based on the user's schema."},
                    {"role": "user", "content": f"Extract the following information from the HTML content:\n\nHTML:\n{html_content}\n\nSchema: {schema_dict}"
                    }
                ]
            )
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error en la extracción estructurada con LLM: {e}", exc_info=True)
            return None

    async def summarize_content(self, text_content: str, max_words: int = 100) -> str | None:
        """
        Sumariza contenido usando un LLM.
        """
        if not self.client:
            logger.warning("LLM no configurado, no se puede realizar la sumarización inteligente.")
            return text_content # Devuelve el texto original si no hay LLM

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Summarize the following text in approximately {max_words} words."},
                    {"role": "user", "content": text_content}
                ],
                temperature=0.7,
                max_tokens=max_words * 2 # Permitir más tokens para asegurar que el resumen se complete
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al sumarizar contenido con LLM: {e}", exc_info=True)
            return text_content # Devuelve el texto original en caso de error

    async def clean_text_content(self, raw_text: str) -> str:
        """
        Limpia el texto usando un LLM para eliminar boilerplate.
        """
        if not self.client:
            logger.debug("LLM no configurado, devolviendo texto crudo sin limpieza inteligente.")
            return raw_text

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert text cleaner. Remove any navigation menus, headers, footers, ad text, or disclaimers from the following web page content. Return only the main article body or primary content. If the content is already clean, return it as is."},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0.0 # Baja temperatura para una limpieza más determinista
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al limpiar contenido con LLM: {e}", exc_info=True)
            return raw_text # Devuelve el texto original en caso de error
