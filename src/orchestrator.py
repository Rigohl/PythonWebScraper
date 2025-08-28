import asyncio
import logging
from urllib.parse import urlparse, urlunparse, ParseResult
from playwright.async_api import Browser
from src.scraper import AdvancedScraper
import imagehash
from robotexclusionrulesparser import RobotExclusionRulesParser
from src.database import DatabaseManager
from src import config
from collections import defaultdict
from src.models.results import ScrapeResult
from src.exceptions import NetworkError, ScraperException

# Importar los nuevos módulos
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent

logger = logging.getLogger(__name__)

class ScrapingOrchestrator:
    """
    Orquesta el proceso de scraping completo con concurrencia y gestión de colas.
    Recibe sus dependencias (como el db_manager) para facilitar las pruebas.
    """
    def __init__(self, start_urls: list[str], db_manager: DatabaseManager,
                 user_agent_manager: UserAgentManager, llm_extractor: LLMExtractor,
                 rl_agent: RLAgent | None = None, concurrency: int = config.CONCURRENCY,
                 respect_robots_txt: bool = False, use_rl: bool = False):
        self.start_urls = start_urls
        self.concurrency = concurrency
        self.db_manager = db_manager # Injected dependency
        self.user_agent_manager = user_agent_manager # Injected dependency
        if use_rl and not rl_agent:
            raise ValueError("RLAgent must be provisto cuando use_rl es True.")
        self.llm_extractor = llm_extractor # Injected dependency
        self.rl_agent = rl_agent # Injected dependency
        self.use_rl = use_rl

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
            "current_backoff_factor": config.INITIAL_RETRY_BACKOFF_FACTOR,
            "last_action": None, # Para RL
            "last_state": None, # Para RL
            "last_reward": None # Para RL
        })

    def _calculate_priority(self, url: str, parent_content_type: str = "UNKNOWN") -> int:
        """Calcula la prioridad de una URL. Menor número es mayor prioridad."""
        path_depth = urlparse(url).path.count('/')
        content_priority = config.CONTENT_TYPE_PRIORITIES.get(parent_content_type, config.CONTENT_TYPE_PRIORITIES["UNKNOWN"])

        # Combinar profundidad y prioridad de contenido. Multiplicar para dar más peso a la profundidad.
        # O sumar, dependiendo de la estrategia deseada. Aquí, sumamos.
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

    async def _apply_rl_actions(self, domain: str, page) -> tuple[dict, dict]:
        """Obtiene y aplica acciones del agente de RL."""
        current_state = self._get_rl_state(domain)
        actions = self.rl_agent.get_action(current_state)

        # Aplicar acciones del RL Agent (ej. ajustar backoff, cambiar UA)
        if "adjust_backoff_factor" in actions:
            self.domain_metrics[domain]["current_backoff_factor"] *= actions["adjust_backoff_factor"]
            self.logger.debug(f"RL Agent ajusta backoff para {domain} a {self.domain_metrics[domain]['current_backoff_factor']:.2f}")
        if "change_user_agent" in actions and actions["change_user_agent"]:
            new_user_agent = self.user_agent_manager.get_user_agent() # Obtener otro UA
            await page.set_extra_http_headers({"User-Agent": new_user_agent})
            self.logger.debug(f"RL Agent cambia User-Agent para {domain} a {new_user_agent}")

        return current_state, actions

    def _perform_rl_learning(self, state: dict, actions: dict, result: ScrapeResult):
        """Calcula la recompensa y entrena al agente de RL."""
        reward = self._calculate_rl_reward(result)
        next_state = self._get_rl_state(urlparse(result.url).netloc)
        self.rl_agent.learn(state, actions, reward, next_state)

    async def _block_unnecessary_requests(self, route):
        """Bloquea la carga de recursos no esenciales para acelerar el scraping."""
        if route.request.resource_type in config.BLOCKED_RESOURCE_TYPES:
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

            page = await browser.new_page()
            await page.route("**/*", self._block_unnecessary_requests)
            scraper = AdvancedScraper(page, self.db_manager, self.llm_extractor)

            result = None
            domain = urlparse(url).netloc
            current_backoff_factor = self.domain_metrics[domain]["current_backoff_factor"]

            # Obtener User-Agent del manager
            current_user_agent = self.user_agent_manager.get_user_agent()
            await page.set_extra_http_headers({"User-Agent": current_user_agent})

            # RL: Aplicar acciones si está activado
            rl_state, rl_actions = None, None
            if self.use_rl:
                rl_state, rl_actions = await self._apply_rl_actions(domain, page)

            # Obtener el esquema de extracción para el dominio actual
            extraction_schema = config.EXTRACTION_SCHEMA.get(domain)

            for attempt in range(config.MAX_RETRIES + 1):
                try:
                    result = await scraper.scrape(url, extraction_schema=extraction_schema,
                                                  proxy=None, user_agent=current_user_agent)
                    break  # Éxito, salir del bucle de reintentos
                except NetworkError as e:
                    self.logger.warning(f"URL {url} falló por error de red. Reintentando... (Intento {attempt + 1}/{config.MAX_RETRIES})")
                    if attempt < config.MAX_RETRIES:
                        backoff_time = self.domain_metrics[domain]["current_backoff_factor"] * (2 ** attempt)
                        await asyncio.sleep(backoff_time)
                    else:
                        self.logger.error(f"URL {url} falló tras {config.MAX_RETRIES} reintentos de red. Descartando.")
                        result = ScrapeResult(status="RETRY", url=url, error_message=str(e), retryable=True)
                        break
                except ScraperException as e:
                    self.logger.error(f"URL {url} falló con error de scraper: {e}. Descartando.")
                    result = ScrapeResult(status="FAILED", url=url, error_message=str(e))
                    break
                except Exception as e:
                    self.logger.error(f"URL {url} falló con error inesperado: {e}. Descartando.", exc_info=True)
                    result = ScrapeResult(status="FAILED", url=url, error_message=f"Error inesperado: {e}")
                    break

            await page.close()

            # --- Lógica de post-procesamiento y guardado ---
            if result:
                # Procesamiento con LLM
                if result.content_text:
                    result.llm_summary = await self.llm_extractor.summarize_content(result.content_text)
                    result.llm_extracted_data = await self.llm_extractor.extract_structured_data(
                        result.content_html, # Usar el HTML del resultado para extracción
                        {"title": "string", "price": "float", "currency": "string"} # Ejemplo de esquema
                    )

                self.db_manager.save_result(result)
                self._update_domain_metrics(result)
                self._check_for_anomalies(domain)

                # RL: Calcular recompensa y aprender si está activado
                if self.use_rl and rl_state is not None:
                    self._perform_rl_learning(rl_state, rl_actions, result)

                # Loggear eventos de auto-reparación si ocurrieron
                if result.healing_events:
                    for event in result.healing_events:
                        self.logger.warning(f"Evento de Auto-reparación en {url}: Campo '{event['field']}' migrado de '{event['old_selector']}' a '{event['new_selector']}'.")

                if result.status == "SUCCESS":
                    self._check_for_visual_changes(result)
                    await self._add_links_to_queue(result.links, result.content_type)
                    self.logger.info(f"Éxito al procesar {url}. Título: '{result.title}'. Enlaces encontrados: {len(result.links)}. Tipo: {result.content_type}")
                    self.user_agent_manager.release_user_agent(current_user_agent)
                elif result.status == "RETRY":
                    self.user_agent_manager.block_user_agent(current_user_agent)
                    self.logger.warning(f"User-Agent {current_user_agent} bloqueado temporalmente para {domain}. URL {url} marcada para reintento. Razón: {result.error_message}")
                elif result.status == "FAILED":
                    # Un fallo permanente también puede ser culpa del UA, lo bloqueamos.
                    self.user_agent_manager.block_user_agent(current_user_agent)
                    self.logger.error(f"Fallo permanente al procesar {url}. Razón: {result.error_message}")
                else:
                    # Guardar resultados terminales como LOW_QUALITY o EMPTY, pero no seguir sus enlaces
                    self.user_agent_manager.release_user_agent(current_user_agent) # Liberar UA, el scrapeo terminó.
                    self._check_for_visual_changes(result)
                    self.logger.warning(f"URL {url} procesada con estado {result.status}. Razón: {result.error_message}. Tipo: {result.content_type}")

            self.queue.task_done()

    def _update_domain_metrics(self, result: ScrapeResult):
        """Actualiza las métricas de rendimiento para un dominio."""
        domain = urlparse(result.url).netloc
        metrics = self.domain_metrics[domain]
        metrics["total_scraped"] += 1
        if result.status == "LOW_QUALITY":
            metrics["low_quality"] += 1
        elif result.status == "EMPTY":
            metrics["empty"] += 1
        elif result.status == "FAILED":
            metrics["failed"] += 1

    def _check_for_anomalies(self, domain: str):
        """Verifica si hay anomalías en el scraping de un dominio y ajusta el backoff."""
        metrics = self.domain_metrics[domain]
        if metrics["total_scraped"] < 10: # Necesitamos suficientes datos para detectar anomalías
            return

        low_quality_ratio = (metrics["low_quality"] + metrics["empty"]) / metrics["total_scraped"]

        if low_quality_ratio > config.ANOMALY_THRESHOLD_LOW_QUALITY:
            # Aumentar el factor de backoff para este dominio
            old_backoff = metrics["current_backoff_factor"]
            metrics["current_backoff_factor"] *= 1.5 # Aumentar en un 50%
            self.logger.warning(f'Anomalía detectada en {domain}: {low_quality_ratio:.2f} de baja calidad/vacío. Aumentando backoff de {old_backoff} a {metrics["current_backoff_factor"]:.2f}')
        elif low_quality_ratio < config.ANOMALY_THRESHOLD_LOW_QUALITY / 2 and metrics["current_backoff_factor"] > config.INITIAL_RETRY_BACKOFF_FACTOR:
            # Reducir el factor de backoff si el rendimiento mejora
            old_backoff = metrics["current_backoff_factor"]
            metrics["current_backoff_factor"] /= 1.2 # Reducir en un 20%
            if metrics["current_backoff_factor"] < config.INITIAL_RETRY_BACKOFF_FACTOR:
                metrics["current_backoff_factor"] = config.INITIAL_RETRY_BACKOFF_FACTOR
            self.logger.info(f"Rendimiento mejorado en {domain}: {low_quality_ratio:.2f} de baja calidad/vacío. Reduciendo backoff de {old_backoff} a {metrics["current_backoff_factor"]:.2f}")

    def _check_for_visual_changes(self, new_result):
        """Compara el hash visual del nuevo resultado con el almacenado en la BD."""
        if not new_result.visual_hash:
            return  # No se pudo calcular el nuevo hash

        old_result = self.db_manager.get_result_by_url(new_result.url)
        if not old_result or not old_result.get('visual_hash'):
            return  # No hay registro previo o no tiene hash para comparar

        try:
            old_hash = imagehash.hex_to_hash(old_result['visual_hash'])
            new_hash = imagehash.hex_to_hash(new_result.visual_hash)
            distance = old_hash - new_hash
            if distance > config.VISUAL_CHANGE_THRESHOLD:
                self.logger.warning(f"¡ALERTA DE REDISEÑO! Se ha detectado un cambio visual significativo en {new_result.url} (distancia de hash: {distance})")
        except Exception as e:
            self.logger.error(f"No se pudo comparar el hash visual para {new_result.url}: {e}")

    async def _add_links_to_queue(self, links: list[str], parent_content_type: str = "UNKNOWN"):
        """
        Filtra, limpia y añade nuevos enlaces a la cola de prioridad.
        """
        for link in links:
            parsed_link = urlparse(link)
            # Limpiar URL (quitar fragmentos y parámetros de consulta)
            clean_link = urlunparse(parsed_link._replace(fragment="", query=""))

            is_allowed_by_robots = self.robot_rules.is_allowed(config.USER_AGENT, clean_link) if self.robot_rules and self.respect_robots_txt else True

            if urlparse(clean_link).netloc == self.allowed_domain and clean_link not in self.seen_urls and is_allowed_by_robots:
                self.seen_urls.add(clean_link)
                priority = self._calculate_priority(clean_link, parent_content_type) # Pass content_type
                await self.queue.put((priority, clean_link))
                self.logger.debug(f"Encolado: {clean_link} (Prioridad: {priority})")

    async def run(self, browser: Browser):
        """
        Ejecuta el proceso de crawling completo usando una instancia de navegador externa.
        """
        if not self.start_urls:
            self.logger.error("No se proporcionaron URLs iniciales.")
            return

        if self.respect_robots_txt:
            await self._fetch_robot_rules(browser) # Pass browser here
        else:
            self.logger.warning("Se ha desactivado la comprobación de robots.txt.")

        self.logger.info(f"Iniciando crawler para el dominio: {self.allowed_domain}")
        self.logger.info(f"Concurrencia establecida a: {self.concurrency}")

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
        self.logger.info("Proceso de crawling completado.")

    async def _fetch_robot_rules(self, browser: Browser): # Add browser parameter
        """Descarga y parsea el archivo robots.txt del dominio."""
        robots_url = urlunparse((urlparse(self.start_urls[0]).scheme, self.allowed_domain, 'robots.txt', '', '', ''))
        try:
            # Usamos una petición simple, no es necesario un navegador completo para esto
            import httpx # httpx supports HTTP/2 by default
            async with httpx.AsyncClient() as client:
                response = await client.get(robots_url, follow_redirects=True)
                if response.status_code == 200:
                    self.robot_rules = RobotExclusionRulesParser()
                    self.robot_rules.parse(response.text)
                    self.logger.info(f"Reglas de robots.txt cargadas desde {robots_url}")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar o parsear robots.txt desde {robots_url}. Se procederá sin restricciones. Error: {e}")
