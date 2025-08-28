import asyncio
import logging
from datetime import datetime, timezone # Added import
from readability import Document
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
import html2text
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import imagehash
from PIL import Image
import io
from typing import Optional, List

from src.settings import settings
from src.database import DatabaseManager
from src.llm_extractor import LLMExtractor
from src.models.results import ScrapeResult
from src.exceptions import NetworkError, ParsingError, ContentQualityError, ScraperException

logger = logging.getLogger(__name__)

class AdvancedScraper:
    """Encapsula la lógica de scraping para una sola página, ahora con limpieza inteligente y auto-reparación."""

    def __init__(self, page: Page, db_manager: DatabaseManager, llm_extractor: LLMExtractor):
        self.page = page
        self.db_manager = db_manager
        self.llm_extractor = llm_extractor
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _generate_stable_selector(self, locator: Locator) -> str:
        """Intenta generar un selector CSS estable para un elemento dado."""
        element_id = await locator.get_attribute("id")
        if element_id: return f"#{element_id}"
        test_id = await locator.get_attribute("data-testid")
        if test_id: return f"[data-testid='{test_id}']"
        tag_name = await locator.evaluate("element => element.tagName.toLowerCase()")
        class_name = await locator.get_attribute("class")
        if class_name:
            stable_classes = ".".join(class_name.split())
            return f"{tag_name}.{stable_classes}"
        return tag_name

    async def scrape(self,
                     url: str,
                     extraction_schema: Optional[dict] = None,
                     proxy: Optional[str] = None,
                     user_agent: Optional[str] = None) -> ScrapeResult:
        """Realiza el scraping, limpieza, extracción y validación de una URL."""
        start_time = datetime.now(timezone.utc)
        try:
            # 1. Navegación y obtención de contenido base
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if response and response.status in settings.RETRYABLE_STATUS_CODES:
                raise NetworkError(f"Estado reintentable: {response.status}")
            await self.page.wait_for_load_state("networkidle", timeout=15000)

            # 2. Extracción de contenido principal con Readability
            full_html = await self.page.content()
            doc = Document(full_html)
            title = doc.title()
            content_html = doc.summary()

            # 3. Limpieza Inteligente
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            raw_text = h.handle(content_html).strip()

            # Usar LLM para eliminar "basura" restante
            cleaned_text = await self.llm_extractor.clean_text_content(raw_text)

            # 4. Análisis de calidad sobre el texto limpio
            self._validate_content_quality(cleaned_text, title)

            # 5. Extracción de enlaces y metadatos
            soup = BeautifulSoup(content_html, 'html.parser')
            visible_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) if 'display: none' not in a.get('style', '').lower()]
            screenshot = await self.page.screenshot()
            visual_hash = str(imagehash.phash(Image.open(io.BytesIO(screenshot))))

            # 6. Extracción Estructurada con Auto-reparación
            extracted_data, healing_events = await self._perform_structured_extraction(url, extraction_schema)

            end_time = datetime.now(timezone.utc)
            return ScrapeResult(
                status="SUCCESS", url=url, title=title, content_text=cleaned_text, content_html=content_html,
                links=visible_links, visual_hash=visual_hash,
                http_status_code=response.status if response else None,
                crawl_duration=(end_time - start_time).total_seconds(),
                content_type=self._classify_content(title, cleaned_text),
                extracted_data=extracted_data, healing_events=healing_events
            )

        except (PlaywrightTimeoutError, NetworkError) as e:
            self.logger.warning(f"Error de red o timeout en scrape de {url}: {e}")
            return ScrapeResult(status="RETRY", url=url, error_message=str(e), retryable=True)
        except (ParsingError, ContentQualityError) as e:
            self.logger.error(f"Error de parseo o calidad de contenido en scrape de {url}: {e}")
            return ScrapeResult(status="FAILED", url=url, error_message=str(e))
        except Exception as e:
            self.logger.error(f"Error inesperado en scrape de {url}: {e}", exc_info=True)
            return ScrapeResult(status="FAILED", url=url, error_message=f"Error inesperado: {e}")

    async def _perform_structured_extraction(self, url: str, schema: Optional[dict]) -> (dict, list):
        """Realiza la extracción de datos usando selectores y se auto-repara si fallan."""
        if not schema:
            return {}, []

        extracted_data = {}
        healing_events = []
        previous_result = self.db_manager.get_result_by_url(url)

        for field, selector in schema.items():
            try:
                element = self.page.locator(selector).first
                if await element.count() > 0:
                    value = await element.inner_text()
                    extracted_data[field] = {"value": value.strip(), "selector": selector}
                else: # Selector falló, intentar auto-reparación
                    self.logger.warning(f"Selector '{selector}' para '{field}' falló en {url}. Intentando auto-reparación...")
                    healed = False
                    if previous_result and previous_result.get('extracted_data') and field in previous_result['extracted_data']:
                        old_text_value = previous_result['extracted_data'][field].get('value')
                        if old_text_value:
                            healed_locator = self.page.locator(f":text-is('{old_text_value}')").first
                            if await healed_locator.count() > 0:
                                new_selector = await self._generate_stable_selector(healed_locator)
                                extracted_data[field] = {"value": old_text_value, "selector": new_selector}
                                healing_events.append({"field": field, "old_selector": selector, "new_selector": new_selector})
                                self.logger.info(f"¡ÉXITO DE AUTO-REPARACIÓN! Campo '{field}' reparado. Nuevo selector: '{new_selector}'")
                                healed = True
                    if not healed:
                        self.logger.error(f"FALLO DE AUTO-REPARACIÓN para el campo '{field}' en {url}.")
                        extracted_data[field] = {"value": None, "selector": selector, "error": "Selector failed"}
            except Exception as e:
                self.logger.error(f"Error extrayendo campo '{field}': {e}")
                extracted_data[field] = {"value": None, "selector": selector, "error": str(e)}
        return extracted_data, healing_events

    def _validate_content_quality(self, text: Optional[str], title: Optional[str]):
        """Valida la calidad del contenido extraído y limpio."""
        if not text:
            raise ContentQualityError("El contenido extraído está vacío después de la limpieza.")
        if len(text) < config.MIN_CONTENT_LENGTH:
            raise ContentQualityError(f"El contenido es demasiado corto ({len(text)} caracteres).")
        for phrase in config.FORBIDDEN_PHRASES:
            if phrase in text.lower() or (title and phrase in title.lower()):
                raise ContentQualityError(f"Contenido parece ser una página de error (contiene: '{phrase}').")

    def _classify_content(self, title: Optional[str], content_text: Optional[str]) -> str:
        """Clasifica el contenido de la página basado en palabras clave."""
        title_lower = title.lower() if title else ""
        content_lower = content_text.lower() if content_text else ""
        if "producto" in title_lower or "comprar" in title_lower or "precio" in content_lower or "añadir al carrito" in content_lower:
            return "PRODUCT"
        if "blog" in title_lower or "articulo" in title_lower or "noticia" in title_lower or "leer más" in content_lower:
            return "BLOG_POST"
        if "guia" in title_lower or "tutorial" in title_lower:
            return "ARTICLE"
        if content_text and len(content_text) > config.MIN_CONTENT_LENGTH:
            return "GENERAL"
        return "UNKNOWN"
