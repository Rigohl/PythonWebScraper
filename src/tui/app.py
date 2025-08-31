import logging
from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.widgets import (
    Header, Footer, Button, Input, Log, ProgressBar, Label, TabbedContent, TabPane, Checkbox, DataTable
)
from textual.logging import TextualHandler
from textual.worker import Worker, WorkerState

from src.settings import settings
from src.database import DatabaseManager
from src.llm_extractor import LLMExtractor
from src.orchestrator import ScrapingOrchestrator
from src.user_agent_manager import UserAgentManager
from src.rl_agent import RLAgent
from src.main import setup_logging

# New widget for displaying alerts
class AlertsDisplay(Container):
    """Un widget para mostrar alertas críticas."""
    def compose(self) -> ComposeResult:
        yield Log(id="alert_log", classes="alerts")

    def add_alert(self, message: str, level: str = "warning"):
        # Textual Log widget uses markup, so we can style messages
        if level == "error":
            self.query_one("#alert_log").write(f"[bold red]ERROR: {message}[/]")
        elif level == "warning":
            self.query_one("#alert_log").write(f"[yellow]WARNING: {message}[/]")
        else:
            self.query_one("#alert_log").write(message)

    def reset(self):
        self.query_one("#alert_log").clear()


class LiveStats(Container):
    """Un widget para mostrar estadísticas en tiempo real."""
    def compose(self) -> ComposeResult:
        yield Label("URLs en cola: 0", id="queue_label")
        yield Label("Procesadas: 0", id="processed_label")
        yield Label("Éxitos: 0", id="success_label")
        yield Label("Fallos: 0", id="failed_label")
        yield Label("Reintentos: 0", id="retry_label")

    def update_stats(self, stats: dict):
        self.query_one("#queue_label").update(f"URLs en cola: {stats['queue_size']}")
        self.query_one("#processed_label").update(f"Procesadas: {stats['processed']}")
        self.query_one("#success_label").update(f"Éxitos: {stats['SUCCESS']}")
        self.query_one("#failed_label").update(f"Fallos: {stats['FAILED']}")
        self.query_one("#retry_label").update(f"Reintentos: {stats['RETRY']}")

    def reset(self):
        for label in self.query(Label):
            base_text = label.renderable.split(":")[0]
            label.update(f"{base_text}: 0")


class DomainStats(Container):
    """Un widget para mostrar estadísticas por dominio en una tabla."""
    def compose(self) -> ComposeResult:
        yield DataTable(id="domain_metrics_table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Dominio", "Backoff", "Procesadas", "Baja Calidad", "Vacías", "Fallos")
        self.border_title = "Métricas por Dominio"

    def update_stats(self, domain_metrics: dict):
        table = self.query_one(DataTable)
        table.clear()
        for domain, metrics in domain_metrics.items():
            table.add_row(
                domain,
                f"{metrics.get('current_backoff_factor', 0):.2f}",
                metrics.get("total_scraped", 0),
                metrics.get("low_quality", 0),
                metrics.get("empty", 0),
                metrics.get("failed", 0),
            )

    def reset(self):
        self.query_one(DataTable).clear()


class ScraperTUIApp(App):
    """Una interfaz de usuario textual para Web Scraper PRO."""

    CSS_PATH = "../../styles.css"
    TITLE = "Scraper PRO"
    SUB_TITLE = "Un crawler y archivador web inteligente."

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("d", "toggle_dark", "Modo Oscuro"),
    ]

    def __init__(self, log_file_path: str | None = None):
        super().__init__()
        self.log_file_path = log_file_path
        self.scraper_worker: Worker | None = None
        self.live_stats_data = {
            "queue_size": 0,
            "processed": 0,
            "total_urls": 0,
            "SUCCESS": 0,
            "FAILED": 0,
            "RETRY": 0,
            "LOW_QUALITY": 0,
        }
        self.domain_metrics = {}

    def compose(self) -> ComposeResult:
        """Crea los widgets de la aplicación."""
        with Grid(id="app-grid"):
            with Container(id="left-pane"):
                yield Header()
                with TabbedContent(initial="crawl-tab"):
                    with TabPane("Crawl", id="crawl-tab"):
                        yield Label("URL de inicio:")
                        yield Input(placeholder="http://toscrape.com/", id="start_url")
                        yield Label("Trabajadores concurrentes:")
                        yield Input(value=str(settings.CONCURRENCY), id="concurrency")
                        yield Checkbox("Ignorar robots.txt", id="no_robots")
                        yield Checkbox("Usar Agente RL (WIP)", value=False, id="use_rl")
                    with TabPane("Estadísticas", id="stats-tab"):
                        yield LiveStats()
                        yield DomainStats()

                with Container(id="actions-pane"):
                    yield Button("Iniciar Crawling", variant="primary", id="start_button")
                    yield Button("Detener Crawling", variant="error", id="stop_button", disabled=True)

                with Container(id="progress-container"):
                    yield Label("Progreso:", id="stats_label")
                    yield ProgressBar(id="progress_bar", total=100, show_eta=False)

                yield AlertsDisplay(id="alerts_display") # New widget for alerts

                yield Button("Salir", variant="default", id="quit_button")

            with Container(id="right-pane"):
                yield Log(id="log_view", highlight=True)
        yield Footer()

    def on_mount(self) -> None:
        """Se llama cuando la app se monta en el DOM."""
        log_widget = self.query_one("#log_view", Log)
        # Pasamos el handler de la TUI a la configuración de logging
        setup_logging(log_file_path=self.log_file_path, tui_handler=TextualHandler(log_widget))
        self.query_one("#progress_bar").visible = False
        self.query_one(LiveStats).border_title = "Estadísticas Globales"
        self.query_one(DomainStats).border_title = "Métricas por Dominio" # Ensure DomainStats has a border title
        self.query_one(AlertsDisplay).border_title = "Alertas Críticas" # Set border title for alerts
        self.query_one(AlertsDisplay).reset() # Clear alerts on mount
        self.query_one("#stats_label").update("Listo para iniciar.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja los clics de los botones."""
        if event.button.id == "start_button":
            self.action_start_crawl()
        elif event.button.id == "stop_button":
            self.action_stop_crawl()
        elif event.button.id == "quit_button":
            self.action_quit()

    def stats_update_callback(self, update: dict):
        """Callback que el orquestador llamará para actualizar las estadísticas."""
        # Actualizar estadísticas globales
        self.live_stats_data["processed"] += update.get("processed", 0)
        self.live_stats_data["queue_size"] = update.get("queue_size", self.live_stats_data["queue_size"])
        status = update.get("status")
        if status in self.live_stats_data:
            self.live_stats_data[status] += 1
        self.query_one(LiveStats).update_stats(self.live_stats_data)

        # Actualizar barra de progreso y etiqueta
        processed_count = self.live_stats_data["processed"]
        queue_size = self.live_stats_data["queue_size"]
        total_urls = processed_count + queue_size

        progress_bar = self.query_one(ProgressBar)
        stats_label = self.query_one("#stats_label")

        if total_urls > 0:
            progress_bar.total = total_urls
            progress_bar.progress = processed_count
            percentage = (processed_count / total_urls) * 100
            stats_label.update(f"Procesadas: {processed_count} de {total_urls} ({percentage:.2f}%)")


        # B.1.3: Actualizar la tabla de métricas por dominio
        domain_metrics_data = update.get("domain_metrics")
        if domain_metrics_data:
            self.domain_metrics = domain_metrics_data
            self.query_one(DomainStats).update_stats(self.domain_metrics)

    def alert_callback(self, message: str, level: str = "warning"):
        """Callback para que el orquestador envíe alertas a la TUI."""
        self.call_later(self.query_one(AlertsDisplay).add_alert, message, level)

    def action_start_crawl(self) -> None:
        """Inicia el proceso de crawling en un worker."""
        start_url_input = self.query_one("#start_url", Input)
        concurrency_input = self.query_one("#concurrency", Input)
        no_robots_checkbox = self.query_one("#no_robots", Checkbox)
        use_rl_checkbox = self.query_one("#use_rl", Checkbox)

        start_url = start_url_input.value
        if not start_url:
            self.query_one("#stats_label").update("[bold red]Error: La URL de inicio no puede estar vacía.[/]")
            return

        try:
            concurrency = int(concurrency_input.value)
        except ValueError:
            self.query_one("#stats_label").update("[bold red]Error: La concurrencia debe ser un número.[/]")
            return

        self.set_ui_for_crawling(True)
        # Reiniciar estadísticas
        self.live_stats_data = {k: 0 for k in self.live_stats_data}
        self.query_one("#stats_label").update("Iniciando...")
        self.query_one(ProgressBar).update(total=100, progress=0)
        self.query_one(LiveStats).reset()
        self.query_one(DomainStats).reset() # Reset domain stats too
        self.query_one(AlertsDisplay).reset() # Reset alerts


        self.scraper_worker = self.run_worker(
            self.crawl_worker(
                start_urls=[start_url],
                db_path=settings.DB_PATH,
                concurrency=concurrency,
                respect_robots_txt=not no_robots_checkbox.value,
                use_rl=use_rl_checkbox.value,
                stats_callback=self.stats_update_callback,
                alert_callback=self.alert_callback # Pass the new callback
            ),
            name="ScraperWorker"
        )

    def action_stop_crawl(self) -> None:
        """Detiene el worker de crawling."""
        if self.scraper_worker:
            logging.warning("Deteniendo el proceso de crawling...")
            self.scraper_worker.cancel()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Se llama cuando el estado del worker cambia."""
        if event.worker.name == "ScraperWorker":
            if event.state == WorkerState.SUCCESS:
                logging.info("El proceso de crawling ha finalizado con éxito.")
                self.query_one(ProgressBar).update(total=100, progress=100)
                self.query_one("#stats_label").update("¡Crawling completado!")
            elif event.state == WorkerState.CANCELLED:
                logging.warning("El proceso de crawling ha sido cancelado.")
                self.query_one("#stats_label").update("Proceso detenido por el usuario.")
            elif event.state == WorkerState.ERROR:
                logging.error(f"El worker de crawling ha fallado: {event.worker.error}")
                self.query_one(ProgressBar).add_class("error")
                self.query_one("#stats_label").update("[bold red]Error durante el crawling.[/]")

            # En cualquier caso de finalización, restaurar la UI
            if event.state in (WorkerState.SUCCESS, WorkerState.CANCELLED, WorkerState.ERROR):
                self.set_ui_for_crawling(False)

    def set_ui_for_crawling(self, is_crawling: bool) -> None:
        """Habilita o deshabilita los controles de la UI durante el crawling."""
        self.query_one("#start_button").disabled = is_crawling
        self.query_one("#stop_button").disabled = not is_crawling
        self.query_one("#start_url").disabled = is_crawling
        self.query_one("#concurrency").disabled = is_crawling
        self.query_one("#no_robots").disabled = is_crawling
        self.query_one("#use_rl").disabled = is_crawling

        progress_bar = self.query_one(ProgressBar)
        progress_bar.remove_class("error")
        if is_crawling:
            progress_bar.visible = True
            progress_bar.update(total=100, progress=0)
            self.query_one("#stats_label").update("Crawling en progreso...")
        else:
            # Al finalizar, no ocultamos la barra para que se vea el 100%
            progress_bar.visible = False

    async def crawl_worker(
        self, start_urls: list[str], db_path: str, concurrency: int, respect_robots_txt: bool, use_rl: bool, stats_callback, alert_callback
    ) -> None:
        """La función asíncrona que ejecuta el scraper."""
        logging.info(f"Iniciando crawling para: {start_urls}")

        db_manager = DatabaseManager(db_path=db_path)
        user_agent_manager = UserAgentManager(user_agents=settings.USER_AGENT_LIST)
        llm_extractor = LLMExtractor()
        rl_agent = RLAgent(model_path=settings.RL_MODEL_PATH) if use_rl else None

        orchestrator = ScrapingOrchestrator(
            start_urls=start_urls, db_manager=db_manager, user_agent_manager=user_agent_manager,
            llm_extractor=llm_extractor, rl_agent=rl_agent, concurrency=concurrency,
            respect_robots_txt=respect_robots_txt, use_rl=use_rl, stats_callback=stats_callback,
            alert_callback=alert_callback
        )

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                await orchestrator.run(browser)
            finally:
                if rl_agent:
                    rl_agent.save_model() # Save the model on graceful shutdown
                await browser.close()

    def action_quit(self) -> None:
        """Sale de la aplicación."""
        self.exit()

