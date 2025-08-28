"""
Textual TUI for the improved Web Scraper PRO.

This user interface exposes controls for launching the crawler, monitoring
its progress in real time and browsing previously scraped pages. It builds
upon the original TUI with a number of enhancements:

* A dedicated "Resultados" tab lists the contents of the SQLite database so
  users can quickly verify what has been captured without leaving the app.
  Results can be filtered by a simple substring search against the page
  title or URL and exported to CSV or JSON.
* robots.txt checks are disabled by default; the checkbox in the Crawl tab
  reflects this default state.
* The LLM extractor is instantiated without requiring an explicit API key
  argument; the key and model are drawn from ``settings``.

Note: network‑bound operations (e.g. starting the crawl) are executed in
background workers to keep the UI responsive. Database operations are
synchronous for simplicity; dataset performs lazy iteration so typical
result sets are small. If your database grows substantially you may wish
to offload these operations to a worker thread.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Callable, Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.widgets import (
    Header,
    Footer,
    Button,
    Input,
    Log,
    ProgressBar,
    Label,
    TabbedContent,
    TabPane,
    Checkbox,
    DataTable,
)
from textual.logging import TextualHandler
from textual.worker import Worker, WorkerState

from .settings import settings
from .database import DatabaseManager
from .llm_extractor import LLMExtractor
from .orchestrator import ScrapingOrchestrator  # type: ignore
from .user_agent_manager import UserAgentManager  # type: ignore
from .rl_agent import RLAgent  # type: ignore
from .main import setup_logging  # reuse logging configuration


class AlertsDisplay(Container):
    """Widget to show critical alerts from the scraper."""

    def compose(self) -> ComposeResult:
        yield Log(id="alert_log", classes="alerts")

    def add_alert(self, message: str, level: str = "warning") -> None:
        log = self.query_one("#alert_log", Log)
        if level == "error":
            log.write(f"[bold red]ERROR: {message}[/]")
        elif level == "warning":
            log.write(f"[yellow]WARNING: {message}[/]")
        else:
            log.write(message)

    def reset(self) -> None:
        self.query_one("#alert_log", Log).clear()


class LiveStats(Container):
    """Widget showing overall statistics about the crawl."""

    def compose(self) -> ComposeResult:
        yield Label("URLs en cola: 0", id="queue_label")
        yield Label("Procesadas: 0", id="processed_label")
        yield Label("Éxitos: 0", id="success_label")
        yield Label("Fallos: 0", id="failed_label")
        yield Label("Reintentos: 0", id="retry_label")

    def update_stats(self, stats: Dict[str, int]) -> None:
        self.query_one("#queue_label", Label).update(f"URLs en cola: {stats['queue_size']}")
        self.query_one("#processed_label", Label).update(f"Procesadas: {stats['processed']}")
        self.query_one("#success_label", Label).update(f"Éxitos: {stats['SUCCESS']}")
        self.query_one("#failed_label", Label).update(f"Fallos: {stats['FAILED']}")
        self.query_one("#retry_label", Label).update(f"Reintentos: {stats['RETRY']}")

    def reset(self) -> None:
        for label in self.query(Label):
            base_text = label.renderable.split(":")[0]
            label.update(f"{base_text}: 0")


class DomainStats(Container):
    """Widget showing per‑domain metrics in a table."""

    def compose(self) -> ComposeResult:
        yield DataTable(id="domain_metrics_table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "Dominio",
            "Backoff",
            "Procesadas",
            "Baja Calidad",
            "Vacías",
            "Fallos",
        )
        self.border_title = "Métricas por Dominio"

    def update_stats(self, domain_metrics: Dict[str, Dict[str, any]]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for domain, metrics in domain_metrics.items():
            table.add_row(
                domain,
                f"{metrics.get('current_backoff_factor', 0):.2f}",
                str(metrics.get("total_scraped", 0)),
                str(metrics.get("low_quality", 0)),
                str(metrics.get("empty", 0)),
                str(metrics.get("failed", 0)),
            )

    def reset(self) -> None:
        self.query_one(DataTable).clear()


class ScraperTUIApp(App):
    """Main Textual application for controlling the web scraper."""

    CSS_PATH = "../styles.css"
    TITLE = "Scraper PRO"
    SUB_TITLE = "Un crawler y archivador web inteligente."
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("d", "toggle_dark", "Modo Oscuro"),
    ]

    def __init__(self, log_file_path: Optional[str] = None) -> None:
        super().__init__()
        self.log_file_path = log_file_path
        self.scraper_worker: Optional[Worker] = None
        self.live_stats_data: Dict[str, int] = {
            "queue_size": 0,
            "processed": 0,
            "SUCCESS": 0,
            "FAILED": 0,
            "RETRY": 0,
            "LOW_QUALITY": 0,
        }
        self.domain_metrics: Dict[str, Dict[str, any]] = {}

    # ---------------------------- State persistence ---------------------------
    _state_path = os.path.join(os.path.expanduser("~"), ".scraper_tui_state.json")

    def _load_state(self) -> None:
        """Load persisted UI state from disk, if available."""
        try:
            with open(self._state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Only update known fields
            start_url = data.get("start_url")
            concurrency = data.get("concurrency")
            no_robots = data.get("no_robots")
            use_rl = data.get("use_rl")
            if start_url:
                self.query_one("#start_url", Input).value = start_url
            if concurrency:
                self.query_one("#concurrency", Input).value = str(concurrency)
            if no_robots is not None:
                self.query_one("#no_robots", Checkbox).value = no_robots
            if use_rl is not None:
                self.query_one("#use_rl", Checkbox).value = use_rl
        except FileNotFoundError:
            pass
        except Exception as e:
            logging.warning("No se pudo cargar el estado previo de la TUI: %s", e)

    def _save_state(self) -> None:
        """Persist current UI state to disk."""
        try:
            data = {
                "start_url": self.query_one("#start_url", Input).value,
                "concurrency": self.query_one("#concurrency", Input).value,
                "no_robots": self.query_one("#no_robots", Checkbox).value,
                "use_rl": self.query_one("#use_rl", Checkbox).value,
            }
            with open(self._state_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            logging.warning("No se pudo guardar el estado de la TUI: %s", e)

    # ------------------------------- Composition -----------------------------
    def compose(self) -> ComposeResult:
        """Create the application layout."""
        with Grid(id="app-grid"):
            with Container(id="left-pane"):
                yield Header()
                with TabbedContent(initial="crawl-tab"):
                    # ----------------------- Crawl Tab ----------------------
                    with TabPane("Crawl", id="crawl-tab"):
                        yield Label("URL de inicio:")
                        yield Input(placeholder="http://toscrape.com/", id="start_url")
                        yield Label("Trabajadores concurrentes:")
                        yield Input(value=str(settings.CONCURRENCY), id="concurrency")
                        # robots disabled by default
                        yield Checkbox("Ignorar robots.txt", id="no_robots", value=True)
                        yield Checkbox("Usar Agente RL (WIP)", value=False, id="use_rl")
                    # --------------------- Stats Tab ----------------------
                    with TabPane("Estadísticas", id="stats-tab"):
                        yield LiveStats()
                        yield DomainStats()
                    # -------------------- Results Tab ---------------------
                    with TabPane("Resultados", id="results-tab"):
                        yield Input(placeholder="Filtrar por título o URL", id="results_query")
                        with Container(id="results_buttons"):
                            yield Button("Buscar", variant="primary", id="results_search_button")
                            yield Button("Refrescar", variant="primary", id="results_refresh_button")
                            yield Button("Exportar CSV", variant="success", id="results_export_csv_button")
                            yield Button("Exportar JSON", variant="success", id="results_export_json_button")
                        yield DataTable(id="results_table")
                with Container(id="actions-pane"):
                    yield Button("Iniciar Crawling", variant="primary", id="start_button")
                    yield Button("Detener Crawling", variant="error", id="stop_button", disabled=True)
                with Container(id="progress-container"):
                    yield Label("Progreso:", id="stats_label")
                    yield ProgressBar(id="progress_bar", total=100, show_eta=False)
                yield AlertsDisplay(id="alerts_display")
                yield Button("Salir", variant="default", id="quit_button")
            with Container(id="right-pane"):
                yield Log(id="log_view", highlight=True, markup=True)
        yield Footer()

    # ------------------------------ Lifecycle -------------------------------
    def on_mount(self) -> None:
        """Called when the app is mounted in the DOM."""
        # Configure logging to pipe into the Log widget
        log_widget = self.query_one("#log_view", Log)
        setup_logging(log_file_path=self.log_file_path, tui_handler=TextualHandler(log_widget))
        # Hide progress bar until crawl starts
        self.query_one("#progress_bar", ProgressBar).visible = False
        # Set border titles for metrics widgets
        self.query_one(LiveStats).border_title = "Estadísticas Globales"
        self.query_one(DomainStats).border_title = "Métricas por Dominio"
        self.query_one(AlertsDisplay).border_title = "Alertas Críticas"
        self.query_one(AlertsDisplay).reset()
        self.query_one("#stats_label", Label).update("Listo para iniciar.")
        # Load persisted state if available
        self._load_state()
        # Load initial results table
        self.call_after_refresh(self.load_results)

    # ------------------------------ Buttons -------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "start_button":
                self.action_start_crawl()
            case "stop_button":
                self.action_stop_crawl()
            case "quit_button":
                self.action_quit()
            case "results_search_button":
                self.action_results_search()
            case "results_refresh_button":
                self.action_results_refresh()
            case "results_export_csv_button":
                self.action_results_export_csv()
            case "results_export_json_button":
                self.action_results_export_json()
            case _:
                # Unhandled button
                pass

    # ------------------------- Stats / Alerts callbacks ---------------------
    def stats_update_callback(self, update: Dict[str, any]) -> None:
        # Update global stats
        self.live_stats_data["processed"] += update.get("processed", 0)
        self.live_stats_data["queue_size"] = update.get("queue_size", self.live_stats_data["queue_size"])
        status = update.get("status")
        if status in self.live_stats_data:
            self.live_stats_data[status] += 1
        self.query_one(LiveStats).update_stats(self.live_stats_data)
        # Update domain metrics table
        domain_metrics_data = update.get("domain_metrics")
        if domain_metrics_data:
            self.domain_metrics = domain_metrics_data
            self.query_one(DomainStats).update_stats(self.domain_metrics)

    def alert_callback(self, message: str, level: str = "warning") -> None:
        # Schedule alert on the main thread
        self.call_later(self.query_one(AlertsDisplay).add_alert, message, level)

    # ----------------------------- Crawl actions ----------------------------
    def action_start_crawl(self) -> None:
        start_url_input = self.query_one("#start_url", Input)
        concurrency_input = self.query_one("#concurrency", Input)
        no_robots_checkbox = self.query_one("#no_robots", Checkbox)
        use_rl_checkbox = self.query_one("#use_rl", Checkbox)
        start_url = start_url_input.value
        if not start_url:
            self.query_one("#stats_label", Label).update("[bold red]Error: La URL de inicio no puede estar vacía.[/]")
            return
        try:
            concurrency = int(concurrency_input.value)
        except ValueError:
            self.query_one("#stats_label", Label).update("[bold red]Error: La concurrencia debe ser un número.[/]")
            return
        # UI adjustments
        self.set_ui_for_crawling(True)
        # Reset stats
        for key in self.live_stats_data:
            self.live_stats_data[key] = 0
        self.query_one(LiveStats).reset()
        self.query_one(DomainStats).reset()
        self.query_one(AlertsDisplay).reset()
        # Persist state
        self._save_state()
        # Launch worker to perform crawl asynchronously
        self.scraper_worker = self.run_worker(
            self.crawl_worker(
                start_urls=[start_url],
                db_path=settings.DB_PATH,
                concurrency=concurrency,
                respect_robots_txt=not no_robots_checkbox.value,
                use_rl=use_rl_checkbox.value,
                stats_callback=self.stats_update_callback,
                alert_callback=self.alert_callback,
            ),
            name="ScraperWorker",
        )

    def action_stop_crawl(self) -> None:
        if self.scraper_worker:
            logging.warning("Deteniendo el proceso de crawling…")
            self.scraper_worker.cancel()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "ScraperWorker":
            if event.state == WorkerState.SUCCESS:
                logging.info("El proceso de crawling ha finalizado con éxito.")
                self.query_one("#stats_label", Label).update("¡Crawling completado!")
            elif event.state == WorkerState.CANCELLED:
                logging.warning("El proceso de crawling ha sido cancelado.")
                self.query_one("#stats_label", Label).update("Proceso detenido por el usuario.")
            elif event.state == WorkerState.ERROR:
                logging.error(f"El worker de crawling ha fallado: {event.worker.error}")
                self.query_one("#stats_label", Label).update("[bold red]Error durante el crawling.[/]")
            # Restore UI after any termination
            if event.state in (WorkerState.SUCCESS, WorkerState.CANCELLED, WorkerState.ERROR):
                self.set_ui_for_crawling(False)
                # Persist state when finishing crawl
                self._save_state()

    def set_ui_for_crawling(self, is_crawling: bool) -> None:
        self.query_one("#start_button", Button).disabled = is_crawling
        self.query_one("#stop_button", Button).disabled = not is_crawling
        self.query_one("#start_url", Input).disabled = is_crawling
        self.query_one("#concurrency", Input).disabled = is_crawling
        self.query_one("#no_robots", Checkbox).disabled = is_crawling
        self.query_one("#use_rl", Checkbox).disabled = is_crawling
        progress_bar = self.query_one(ProgressBar)
        if is_crawling:
            progress_bar.visible = True
            # Start indeterminate progress
            progress_bar.advance(None)
            self.query_one("#stats_label", Label).update("Crawling en progreso…")
        else:
            progress_bar.visible = False

    async def crawl_worker(
        self,
        start_urls: List[str],
        db_path: str,
        concurrency: int,
        respect_robots_txt: bool,
        use_rl: bool,
        stats_callback: Callable[[Dict[str, any]], None],
        alert_callback: Callable[[str, str], None],
    ) -> None:
        logging.info(f"Iniciando crawling para: {start_urls}")
        db_manager = DatabaseManager(db_path=db_path)
        user_agent_manager = UserAgentManager(user_agents=settings.USER_AGENT_LIST)
        llm_extractor = LLMExtractor()  # Instantiated without explicit api_key
        rl_agent = RLAgent(model_path=settings.RL_MODEL_PATH) if use_rl else None  # type: ignore
        orchestrator = ScrapingOrchestrator(
            start_urls=start_urls,
            db_manager=db_manager,
            user_agent_manager=user_agent_manager,
            llm_extractor=llm_extractor,
            rl_agent=rl_agent,
            concurrency=concurrency,
            respect_robots_txt=respect_robots_txt,
            use_rl=use_rl,
            stats_callback=stats_callback,
            alert_callback=alert_callback,
        )
        from playwright.async_api import async_playwright  # import here to avoid Playwright overhead when not crawling
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                await orchestrator.run(browser)
            finally:
                if rl_agent:
                    rl_agent.save_model()  # type: ignore
                await browser.close()

    # ------------------------- Results tab actions ---------------------------
    async def load_results(self, query: Optional[str] = None) -> None:
        """Populate the results table.

        If ``query`` is provided, a simple substring search is applied to the
        title and URL fields. Otherwise the most recent pages are listed.
        """
        # Use synchronous DB operations for simplicity
        db_manager = DatabaseManager(db_path=settings.DB_PATH)
        rows: List[Dict[str, any]]
        if query:
            rows = db_manager.search_results(query, limit=100)
        else:
            rows = db_manager.list_results(limit=100)
        table = self.query_one("#results_table", DataTable)
        table.clear()
        # If there are no rows, add a placeholder
        if not rows:
            table.add_columns("Mensaje")
            table.add_row("No se encontraron resultados.")
            return
        # Determine columns dynamically but ensure a consistent order
        columns = ["url", "title", "status", "content_hash"]
        table.add_columns(*[col.capitalize() if col != "content_hash" else "Hash" for col in columns])
        for row in rows:
            table.add_row(
                str(row.get("url", "")),
                str(row.get("title", "")),
                str(row.get("status", "")),
                str(row.get("content_hash", "")),
            )

    def action_results_search(self) -> None:
        query = self.query_one("#results_query", Input).value
        # schedule asynchronous loading
        self.call_later(self.call_after_refresh, self.load_results, query)

    def action_results_refresh(self) -> None:
        # reload all results
        self.call_later(self.call_after_refresh, self.load_results)

    def action_results_export_csv(self) -> None:
        # Export results to a timestamped CSV in the user's home directory
        export_dir = os.path.join(os.path.expanduser("~"), "scraper_exports")
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, f"scraper_results_{int(asyncio.get_event_loop().time())}.csv")
        db_manager = DatabaseManager(db_path=settings.DB_PATH)
        db_manager.export_to_csv(file_path)
        self.alert_callback(f"Datos exportados a {file_path}", level="info")

    def action_results_export_json(self) -> None:
        export_dir = os.path.join(os.path.expanduser("~"), "scraper_exports")
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, f"scraper_results_{int(asyncio.get_event_loop().time())}.json")
        db_manager = DatabaseManager(db_path=settings.DB_PATH)
        db_manager.export_to_json(file_path)
        self.alert_callback(f"Datos exportados a {file_path}", level="info")

    # ------------------------------- Exit -----------------------------------
    def action_quit(self) -> None:
        # Persist state before exiting
        self._save_state()
        self.exit()