# -*- coding: utf-8 -*-
import os
from datetime import datetime
from urllib.parse import urlparse
import json
import re # Added import for re module

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Button, Input, Static, Log, Checkbox, ProgressBar, TabbedContent, TabPane

# Importaciones desde nuestros nuevos módulos
from database import DatabaseManager
from orchestrator import ScrapingContext, ScrapingOrchestrator

class ScraperApp(App):
    """La aplicación principal de scraping con interfaz de usuario de texto."""
    CSS_PATH = "../styles.css" # Ruta relativa al CSS fuera de la carpeta src
    BINDINGS = [("d", "toggle_dark", "Modo Oscuro")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            with Vertical(id="left-pane"):
                # Usamos pestañas para organizar la configuración y evitar el scroll.
                with TabbedContent(initial="main-tab"):
                    with TabPane("Principal", id="main-tab"):
                        yield Input(placeholder="Introduce la URL aquí...", id="url_input")
                        yield Checkbox("Modo Automático (descubrir URLs)", id="auto_mode", value=True)
                        yield Input(placeholder="Patrones de URL a Excluir (coma)", id="excluded_patterns_input")
                    with TabPane("Avanzado", id="advanced-tab"):
                        yield Input(placeholder="Proxies (coma, ej: http://user:pass@host:port)", id="proxies_input")
                        yield Input(placeholder="Límite de Concurrencia", value="5", id="concurrency_input")
                        yield Input(placeholder="Máximo de Reintentos", value="3", id="retries_input")
                    with TabPane("Formatos", id="formats-tab"):
                        yield Checkbox("Texto Limpio (.txt)", value=True, id="format_txt")
                        yield Checkbox("Markdown (.md)", value=True, id="format_md")
                        yield Checkbox("Excel/CSV (.csv)", value=True, id="format_csv")
                        yield Checkbox("JSON Lines (.jsonl)", value=True, id="format_json")

                # Contenedor para acciones, progreso y salida.
                with Vertical(id="actions-pane"):
                    yield Button("Iniciar Scraping", variant="success", id="start_button")
                    yield Button("Guardar Config", id="save_config_button")
                    yield Button("Cargar Config", id="load_config_button")
                    yield Button("Limpiar Log", id="clear_log_button")
                    with Container(id="progress-container"):
                        yield Static("Progreso:", classes="sub-header")
                        yield ProgressBar(id="progress_bar", total=100, show_eta=False, show_percentage=True)
                        yield Static("Procesadas: 0 | En Cola: 0", id="stats_label")
                    yield Button("Salir", variant="error", id="quit_button")
            with VerticalScroll(id="right-pane"):
                yield Log(id="log", auto_scroll=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#progress-container").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start_button":
            url = self.query_one("#url_input").value
            if url:
                self.query_one(Log).clear()
                self.query_one(Log).write_line("Iniciando proceso con scraper avanzado...")
                event.button.disabled = True
                self.query_one("#progress-container").display = True
                self.run_worker(self._start_scraping_job, name="scraper_worker", group="scraping", exclusive=True, thread=True)
            else:
                self.query_one(Log).write_line("[ERROR] Por favor, introduce una URL.")
        elif event.button.id == "quit_button":
            self.exit()
        elif event.button.id == "clear_log_button":
            self.query_one(Log).clear()
        elif event.button.id == "save_config_button":
            self._save_config()
        elif event.button.id == "load_config_button":
            self._load_config()


    def _on_scraping_finish(self) -> None:
        """
        Callback to re-enable the start button from the orchestrator.
        Reactive attributes in Textual are thread-safe.
        """
        self.query_one("#start_button").disabled = False

    def _save_config(self) -> None:
        """Guarda la configuración actual de la UI en config.json."""
        log = self.query_one(Log)
        try:
            config_data = {
                "url": self.query_one("#url_input").value,
                "auto_mode": self.query_one("#auto_mode").value,
                "excluded_patterns": self.query_one("#excluded_patterns_input").value,
                "proxies": self.query_one("#proxies_input").value,
                "concurrency": self.query_one("#concurrency_input").value,
                "retries": self.query_one("#retries_input").value,
                "formats": {
                    "txt": self.query_one("#format_txt").value,
                    "md": self.query_one("#format_md").value,
                    "csv": self.query_one("#format_csv").value,
                    "json": self.query_one("#format_json").value,
                }
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            log.write_line("[bold green]Configuración guardada en config.json[/bold green]")
        except Exception as e:
            log.write_line(f"[bold red]Error al guardar configuración: {e}[/bold red]")

    def _load_config(self) -> None:
        """Carga la configuración desde config.json a la UI."""
        log = self.query_one(Log)
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                self.query_one("#url_input").value = config_data.get("url", "")
                self.query_one("#auto_mode").value = config_data.get("auto_mode", True)
                self.query_one("#excluded_patterns_input").value = config_data.get("excluded_patterns", "")
                self.query_one("#proxies_input").value = config_data.get("proxies", "")
                self.query_one("#concurrency_input").value = config_data.get("concurrency", "5")
                self.query_one("#retries_input").value = config_data.get("retries", "3")
                formats = config_data.get("formats", {})
                for fmt, enabled in formats.items():
                    self.query_one(f"#format_{fmt}").value = enabled
                log.write_line("[bold green]Configuración cargada desde config.json[/bold green]")
            else:
                log.write_line("[bold yellow]No se encontró el archivo config.json[/bold yellow]")
        except Exception as e:
            log.write_line(f"[bold red]Error al cargar configuración: {e}[/bold red]")

    def _start_scraping_job(self) -> None:
        """
        Gathers configuration from the UI, creates a context, and
        starts the ScrapingOrchestrator in a worker thread.
        """
        log = self.query_one(Log)

        # Create the context object
        context = ScrapingContext(
            base_url=self.query_one("#url_input").value,
            auto_mode=self.query_one("#auto_mode").value,
            excluded_patterns_str=self.query_one("#excluded_patterns_input").value,
            proxies_str=self.query_one("#proxies_input").value,
            max_retries_str=self.query_one("#retries_input").value,
            concurrency_limit_str=self.query_one("#concurrency_input").value,
            writers={
                'txt_enabled': self.query_one("#format_txt").value,
                'md_enabled': self.query_one("#format_md").value,
                'csv_enabled': self.query_one("#format_csv").value,
                'json_enabled': self.query_one("#format_json").value,
            },
            log=log,
            progress_bar=self.query_one(ProgressBar),
            stats_label=self.query_one("#stats_label"),
            on_finish=self._on_scraping_finish
        )
        # Create and run the orchestrator in a separate thread
        orchestrator = ScrapingOrchestrator(context)
        orchestrator.run()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
