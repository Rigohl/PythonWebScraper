import asyncio
import logging
from urllib.parse import urlparse, urlunparse, ParseResult
from playwright.async_api import Browser
import httpx
from playwright_stealth import stealth_async
from src.scraper import AdvancedScraper
import imagehash
from robotexclusionrulesparser import RobotExclusionRulesParser
from src.database import DatabaseManager
from src.settings import settings
from collections import defaultdict
from src.models.results import ScrapeResult
from src.exceptions import NetworkError, ParsingError, ContentQualityError, ScraperException, RedirectLoopError
import json 

# Importar los nuevos módulos
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent
from src.fingerprint_manager import FingerprintManager

logger = logging.getLogger(__name__)

class ScrapingOrchestrator:
    """
    Orquesta el proceso de scraping completo con concurrencia y gestión de colas.
    Recibe sus dependencias (como el db_manager) para facilitar las pruebas.
    """
    def __init__(self, start_urls: list[str], db_manager: DatabaseManager,
                 user_agent_manager: UserAgentManager, llm_extractor: LLMExtractor,
                 rl_agent: RLAgent | None = None, concurrency: int = settings.CONCURRENCY,
                 respect_robots_txt: bool = False, use_rl: bool = False,
                 stats_callback=None, alert_callback=None):
        self.start_urls = start_urls
        self.concurrency = concurrency
        self.db_manager = db_manager # Injected dependency
        self.user_agent_manager = user_agent_manager # Injected dependency
        self.fingerprint_manager = FingerprintManager(user_agent_manager=self.user_agent_manager)
        if use_rl and not rl_agent:
            raise ValueError("RLAgent must be provisto cuando use_rl es True.")
        self.llm_extractor = llm_extractor # Injected dependency
        self.rl_agent = rl_agent # Injected dependency
        self.use_rl = use_rl
        self.stats_callback = stats_callback # Para reportar a la TUI
        self.alert_callback = alert_callback # Added for reporting alerts to TUI

        self.queue = asyncio.PriorityQueue()
        self.seen_urls = set()
        self.respect_robots_txt = respect_robots_txt
        self.allowed_domain = urlparse(start_urls[0]).netloc if start_urls else ""
        self.robot_rules = None
        self.logger = logging.getLogger(self.__class__.__name__)

        # Métricas para detección de anomalías y ajuste adaptativo
        self.domain_metrics = defaultdict(lambda: {
            "total_scraped": 0,
            "low_quality": 0,
            "empty": 0,
            "failed": 0,
            "current_backoff_factor": settings.INITIAL_RETRY_BACKOFF_FACTOR,
            "last_action_dict": None, # Para RL: almacenar el diccionario de acciones
            "last_state_dict": None, # Para RL: almacenar el diccionario de estado
        })

    def _calculate_priority(self, url: str, parent_content_type: str = "UNKNOWN") -> int:
        """Calcula la prioridad de una URL. Menor número es mayor prioridad."""
        path_depth = urlparse(url).path.count('/')
        content_priority = settings.CONTENT_TYPE_PRIORITIES.get(parent_content_type, settings.CONTENT_TYPE_PRIORITIES["UNKNOWN"])

        # Combinar profundidad y prioridad de contenido.
        return path_depth + content_priority

    def _get_rl_state(self, domain: str) -> dict:
        """Genera el estado actual para el agente de RL."""
        metrics = self.domain_metrics[domain]
        total_scraped = metrics["total_scraped"]
        # Evitar división por cero
        low_quality_ratio = (metrics["low_quality"] + metrics["empty"]) / total_scraped if total_scraped > 0 else 0
        failure_ratio = metrics["failed"] / total_scraped if total_scraped > 0 else 0

        return {
            "low_quality_ratio": low_quality_ratio,
            "failure_ratio": failure_ratio,
            "current_backoff": metrics["current_backoff_factor"],
        }

    def _calculate_rl_reward(self, result: ScrapeResult) -> float:
        """Calcula la recompensa para el agente de RL basado en el resultado."""
        if result.status == "SUCCESS":
            return 1.0  # Recompensa alta por éxito
        if result.status in ["LOW_QUALITY", "EMPTY"]:
            return -0.5 # Penalización media por baja calidad
        if result.status == "FAILED":
            return -1.0 # Penalización alta por fallo
        return 0.0 # Sin recompensa para otros estados (ej. RETRY)

    async def _apply_rl_actions(self, domain: str):
        """Obtiene y aplica acciones del agente de RL."""
        current_state_dict = self._get_rl_state(domain)
        actions_dict = self.rl_agent.get_action(current_state_dict)

        # Aplicar acciones del RL Agent
        if "adjust_backoff_factor" in actions_dict:
            self.domain_metrics[domain]["current_backoff_factor"] *= actions_dict["adjust_backoff_factor"]
            self.logger.debug(f"RL Agent ajusta backoff para {domain} a {self.domain_metrics[domain]['current_backoff_factor']:.2f}")
        
        # Almacenar el estado y la acción para el aprendizaje posterior
        self.domain_metrics[domain]["last_state_dict"] = current_state_dict
        self.domain_metrics[domain]["last_action_dict"] = actions_dict

    def _perform_rl_learning(self, result: ScrapeResult):
        """Calcula la recompensa y entrena al agente de RL."""
        domain = urlparse(result.url).netloc
        metrics = self.domain_metrics[domain]

        if metrics["last_state_dict"] is None or metrics["last_action_dict"] is None:
            self.logger.debug(f"No hay estado o acción previos para el aprendizaje RL en {domain}.")
            return

        reward = self._calculate_rl_reward(result)
        next_state_dict = self._get_rl_state(domain)
        
        self.rl_agent.learn(
            metrics["last_state_dict"], 
            metrics["last_action_dict"], 
            reward, 
            next_state_dict
        )
        # Limpiar después de aprender para evitar re-aprender con la misma experiencia
        metrics["last_state_dict"] = None
        metrics["last_action_dict"] = None

    async def _block_unnecessary_requests(self, route):
        """Bloquea la carga de recursos no esenciales para acelerar el scraping."""
        if route.request.resource_type in settings.BLOCKED_RESOURCE_TYPES:
            await route.abort()
        else:
            await route.continue_()

    async def _worker(self, browser: Browser, worker_id: int):
        """
        Tarea trabajadora que procesa URLs de la cola.
        """
        while True:
            priority, url = await self.queue.get()
            self.logger.info(f"Trabajador {worker_id} procesando: {url} (Prioridad: {priority})")

            fingerprint = self.fingerprint_manager.get_fingerprint()
            current_user_agent = fingerprint["user_agent"]

            page = await browser.new_page(
                user_agent=current_user_agent,
                viewport=fingerprint["viewport"]
            )
            await stealth_async(page)
            
            await page.route("**/*", self._block_unnecessary_requests)
            scraper = AdvancedScraper(page, self.db_manager, self.llm_extractor)

            result = None
            domain = urlparse(url).netloc
            
            if self.use_rl:
                await self._apply_rl_actions(domain)

            dynamic_extraction_schema = None
            stored_schema_json = self.db_manager.load_llm_extraction_schema(domain)
            if stored_schema_json:
                try:
                    dynamic_extraction_schema = json.loads(stored_schema_json)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error al decodificar esquema LLM para {domain}: {e}")
                    if self.alert_callback: self.alert_callback(f"Error al decodificar esquema LLM para {domain}: {e}", level="error")

            for attempt in range(settings.MAX_RETRIES + 1):
                try:
                    result = await scraper.scrape(url, extraction_schema=dynamic_extraction_schema,
                                                  proxy=None, user_agent=current_user_agent)
                    break
                except NetworkError as e:
                    self.logger.warning(f"URL {url} falló por error de red. Reintentando... (Intento {attempt + 1}/{settings.MAX_RETRIES})")
                    if attempt < settings.MAX_RETRIES:
                        backoff_time = self.domain_metrics[domain]["current_backoff_factor"] * (2 ** attempt)
                        await asyncio.sleep(backoff_time)
                    else:
                        self.logger.error(f"URL {url} falló tras {settings.MAX_RETRIES} reintentos de red. Descartando.")
                        if self.alert_callback: self.alert_callback(f"Fallo de red persistente para {url}. Descartando.", level="error")
                        result = ScrapeResult(status="RETRY", url=url, error_message=str(e), retryable=True)
                        break
                except Exception as e:
                    self.logger.error(f"URL {url} falló con error inesperado: {e}. Descartando.", exc_info=True)
                    if self.alert_callback: self.alert_callback(f"Error inesperado al procesar {url}: {e}", level="error")
                    result = ScrapeResult(status="FAILED", url=url, error_message=f"Error inesperado: {e}")
                    break

            await page.close()

            if result:
                if result.content_text:
                    result.llm_summary = await self.llm_extractor.summarize_content(result.content_text)

                self.db_manager.save_result(result)
                self._update_domain_metrics(result)
                
                if not self.use_rl:
                    self._check_for_anomalies(domain)
                else:
                    self._perform_rl_learning(result)

                if result.status == "SUCCESS":
                    self._check_for_visual_changes(result)
                    await self._add_links_to_queue(result.links, result.content_type)
                    self.user_agent_manager.release_user_agent(current_user_agent)
                elif result.status == "FAILED":
                    self.user_agent_manager.block_user_agent(current_user_agent)
                    if self.alert_callback: self.alert_callback(f"Fallo permanente al procesar {url}. Razón: {result.error_message}", level="error")

            self.queue.task_done()

    def _update_domain_metrics(self, result: ScrapeResult):
        domain = urlparse(result.url).netloc
        metrics = self.domain_metrics[domain]
        metrics["total_scraped"] += 1
        if result.status == "LOW_QUALITY":
            metrics["low_quality"] += 1
        elif result.status == "EMPTY":
            metrics["empty"] += 1
        elif result.status == "FAILED":
            metrics["failed"] += 1

        if self.stats_callback:
            self.stats_callback({
                "processed": 1,
                "queue_size": self.queue.qsize(),
                "status": result.status,
                "domain_metrics": self.domain_metrics
            })

    def _check_for_anomalies(self, domain: str):
        metrics = self.domain_metrics[domain]
        if metrics["total_scraped"] < 10:
            return

        low_quality_ratio = (metrics["low_quality"] + metrics["empty"]) / metrics["total_scraped"]

        if low_quality_ratio > settings.ANOMALY_THRESHOLD_LOW_QUALITY:
            old_backoff = metrics["current_backoff_factor"]
            metrics["current_backoff_factor"] *= 1.5
            alert_message = f'Anomalía detectada en {domain}: {low_quality_ratio:.2f} de baja calidad/vacío. Aumentando backoff de {old_backoff} a {metrics["current_backoff_factor"]:.2f}'
            self.logger.warning(alert_message)
            if self.alert_callback: self.alert_callback(alert_message, level="warning")
        elif low_quality_ratio < settings.ANOMALY_THRESHOLD_LOW_QUALITY / 2 and metrics["current_backoff_factor"] > settings.INITIAL_RETRY_BACKOFF_FACTOR:
            old_backoff = metrics["current_backoff_factor"]
            metrics["current_backoff_factor"] /= 1.2
            if metrics["current_backoff_factor"] < settings.INITIAL_RETRY_BACKOFF_FACTOR:
                metrics["current_backoff_factor"] = settings.INITIAL_RETRY_BACKOFF_FACTOR
            self.logger.info(f"Rendimiento mejorado en {domain}: {low_quality_ratio:.2f} de baja calidad/vacío. Reduciendo backoff de {old_backoff} a {metrics['current_backoff_factor']:.2f}")

    def _check_for_visual_changes(self, new_result):
        if not new_result.visual_hash:
            return

        old_result = self.db_manager.get_result_by_url(new_result.url)
        if not old_result or not old_result.get('visual_hash'):
            return

        try:
            old_hash = imagehash.hex_to_hash(old_result['visual_hash'])
            new_hash = imagehash.hex_to_hash(new_result.visual_hash)
            distance = old_hash - new_hash
            if distance > settings.VISUAL_CHANGE_THRESHOLD:
                alert_message = f"¡ALERTA DE REDISEÑO! Se ha detectado un cambio visual significativo en {new_result.url} (distancia de hash: {distance})"
                self.logger.warning(alert_message)
                if self.alert_callback: self.alert_callback(alert_message, level="warning")
        except Exception as e:
            self.logger.error(f"No se pudo comparar el hash visual para {new_result.url}: {e}")
            if self.alert_callback: self.alert_callback(f"Error al comparar hash visual para {new_result.url}: {e}", level="error")

    async def _add_links_to_queue(self, links: list[str], parent_content_type: str = "UNKNOWN"):
        for link in links:
            parsed_link = urlparse(link)
            clean_link = urlunparse(parsed_link._replace(fragment="", query=""))

            is_allowed_by_robots = self.robot_rules.is_allowed(settings.USER_AGENT, clean_link) if self.robot_rules and self.respect_robots_txt else True

            if urlparse(clean_link).netloc == self.allowed_domain and clean_link not in self.seen_urls and is_allowed_by_robots:
                self.seen_urls.add(clean_link)
                priority = self._calculate_priority(clean_link, parent_content_type)
                await self.queue.put((priority, clean_link))

    async def run(self, browser: Browser):
        if not self.start_urls:
            self.logger.error("No se proporcionaron URLs iniciales.")
            if self.alert_callback: self.alert_callback("No se proporcionaron URLs iniciales para el crawling.", level="error")
            return

        if self.respect_robots_txt:
            await self._fetch_robot_rules()
        else:
            self.logger.warning("Se ha desactivado la comprobación de robots.txt.")
            if self.alert_callback: self.alert_callback("La comprobación de robots.txt está desactivada.", level="warning")

        for url in self.start_urls:
            if url not in self.seen_urls:
                self.seen_urls.add(url)
                priority = self._calculate_priority(url)
                await self.queue.put((priority, url))

        worker_tasks = [
            asyncio.create_task(self._worker(browser, i + 1))
            for i in range(self.concurrency)
        ]

        await self.queue.join()

        for task in worker_tasks:
            task.cancel()
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        
        if self.use_rl and self.rl_agent:
            self.rl_agent.save_model()
            
        self.logger.info("Proceso de crawling completado.")
        if self.alert_callback: self.alert_callback("Proceso de crawling completado.", level="info")

    async def _fetch_robot_rules(self):
        robots_url = urlunparse((urlparse(self.start_urls[0]).scheme, self.allowed_domain, 'robots.txt', '', '', ''))
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(robots_url, follow_redirects=True)
                if response.status_code == 200:
                    self.robot_rules = RobotExclusionRulesParser()
                    self.robot_rules.parse(response.text)
                else:
                    self.logger.warning(f"No se pudo obtener robots.txt desde {robots_url}. Código de estado: {response.status_code}")
                    if self.alert_callback: self.alert_callback(f"No se pudo cargar robots.txt desde {robots_url}. Código: {response.status_code}.", level="warning")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar o parsear robots.txt desde {robots_url}. Error: {e}")
            if self.alert_callback: self.alert_callback(f"Error al cargar/parsear robots.txt desde {robots_url}. Error: {e}", level="warning")
