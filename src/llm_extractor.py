import instructor
from openai import OpenAI
from pydantic import BaseModel, create_model
import logging
from typing import Type, TypeVar

from src.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMExtractor:
    """
    Utiliza un LLM (a través de la API de OpenAI y `instructor`) para realizar
    tareas de procesamiento de lenguaje natural como limpieza y extracción estructurada.
    """
    def __init__(self):
        if not settings.LLM_API_KEY:
            raise ValueError("La clave de API de LLM (LLM_API_KEY) no está configurada en los ajustes.")
        
        # A.2.2: Usar `instructor` para parchear el cliente de OpenAI
        self.client = instructor.patch(OpenAI(api_key=settings.LLM_API_KEY))
        logger.info("LLMExtractor inicializado con el cliente de OpenAI parcheado.")

    async def clean_text_content(self, text: str) -> str:
        """
        Utiliza el LLM para limpiar el texto, eliminando elementos no deseados como
        menús, pies de página, anuncios y otro contenido "basura".
        """
        try:
            class CleanedText(BaseModel):
                cleaned_text: str

            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                response_model=CleanedText,
                messages=[
                    {"role": "system", "content": "Eres un experto en limpiar contenido HTML. Tu tarea es eliminar todo el texto que no sea el contenido principal de la página, como barras de navegación, pies de página, anuncios, pop-ups y texto legal. Devuelve únicamente el contenido principal."},
                    {"role": "user", "content": text}
                ]
            )
            return response.cleaned_text
        except Exception as e:
            logger.error(f"Error durante la limpieza de texto con LLM: {e}", exc_info=True)
            # Si falla el LLM, devolvemos el texto original para no romper el flujo
            return text

    async def extract_structured_data(self, html_content: str, response_model: Type[T]) -> T:
        """
        A.2.3: Realiza extracción de datos "Zero-Shot" de un contenido HTML.

        En lugar de usar selectores, se le pasa el HTML y un modelo Pydantic
        al LLM, y este se encarga de "rellenar" el modelo con los datos encontrados.

        Args:
            html_content: El contenido HTML de la página.
            response_model: El modelo Pydantic que define la estructura de los datos a extraer.

        Returns:
            Una instancia del `response_model` con los datos extraídos.
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                response_model=response_model,
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción de datos de páginas web. Tu tarea es analizar el siguiente contenido HTML y rellenar el esquema Pydantic proporcionado con la información encontrada. Extrae los datos de la forma más precisa posible."},
                    {"role": "user", "content": html_content}
                ]
            )
            logger.info(f"Extracción Zero-Shot exitosa para el modelo {response_model.__name__}.")
            return response
        except Exception as e:
            logger.error(f"Error durante la extracción Zero-Shot con LLM para el modelo {response_model.__name__}: {e}", exc_info=True)
            # En caso de error, devolvemos una instancia vacía del modelo para no romper el flujo
            return response_model()

    async def extract_structured_data_dynamic_schema(self, html_content: str, schema_dict: dict) -> dict | None:
        """
        Extrae datos estructurados usando un LLM y un esquema Pydantic dinámico.
        `schema_dict` debe ser un diccionario que describa un modelo Pydantic,
        por ejemplo: {"name": (str, ...), "price": (float, ...)}.
        """
        if not self.client:
            logger.warning("LLM no configurado, no se puede realizar la extracción estructurada dinámica.")
            return None
        
        if not schema_dict:
            logger.debug("No se proporcionó un esquema para la extracción LLM estructurada dinámica.")
            return None

        try:
            # Construir dinámicamente el modelo Pydantic a partir del diccionario
            DynamicSchema = create_model('DynamicSchema', **{
                field: (field_type, ...) for field, field_type in schema_dict.items()
            }) # Default value should be Ellipsis (...) for required fields

            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,  # Use settings.LLM_MODEL
                response_model=DynamicSchema,
                messages=[
                    {"role": "system", "content": "You are an expert data extraction bot. Extract information from the provided HTML content based on the user's schema."},
                    {"role": "user", "content": f"Extract the following information from the HTML content:\n\nHTML:\n{html_content}\n\nSchema: {schema_dict}"
                    }
                ]
            )
            return response.model_dump()
        except Exception as e:
            logger.error(f"Error en la extracción estructurada dinámica con LLM: {e}", exc_info=True)
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
                model=settings.LLM_MODEL, # Use settings.LLM_MODEL
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Summarize the following text in approximately {max_words} words רבי"},
                    {"role": "user", "content": text_content}
                ],
                temperature=0.7,
                max_tokens=max_words * 2 # Permitir más tokens para asegurar que el resumen se complete
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error al sumarizar contenido con LLM: {e}", exc_info=True)
            return text_content # Devuelve el texto original en caso de error
