import logging

from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Vertical
from textual.logging import TextualHandler
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Log,
    ProgressBar,
    TabbedContent,
    TabPane,
    Static,
)
from textual.worker import Worker, WorkerState

from ..runner import setup_logging
from ..runner import run_crawler
from ..settings import settings


# New widget for displaying alerts
class AlertsDisplay(Container):
    """Un widget para mostrar alertas críticas."""

    def compose(self) -> ComposeResult:
        yield Log(id="alert_log", classes="alerts")

    def add_alert(self, message: str, level: str = "warning"):
        # Textual Log widget uses markup, so we can style messages
        log = self.query_one("#alert_log")
        if level == "error":
            log.write(f"[bold red]ERROR: {message}[/]")
        elif level == "warning":
            log.write(f"[yellow]WARNING: {message}[/]")
        else:
            log.write(message)

    def reset(self):
        self.query_one("#alert_log").clear()


class ToastNotification(Static):
    """Un widget para mostrar notificaciones toast temporales."""

    def __init__(self, message: str, level: str = "info", duration: float = 3.0):
        super().__init__()
        self.message = message
        self.level = level
        self.duration = duration
        self._timer = None

    def compose(self) -> ComposeResult:
        if self.level == "success":
            self.add_class("toast-success")
            icon = "✓"
        elif self.level == "warning":
            self.add_class("toast-warning")
            icon = "⚠"
        elif self.level == "error":
            self.add_class("toast-error")
            icon = "✗"
        else:
            self.add_class("toast-info")
            icon = "ℹ"

        yield Static(f"{icon} {self.message}", classes="toast-content")

    async def show(self):
        """Muestra la notificación y la oculta después de la duración."""
        self.styles.display = "block"
        self._timer = self.set_timer(self.duration, self.hide)

    def hide(self):
        """Oculta la notificación."""
        self.styles.display = "none"
        if self._timer:
            self._timer.stop()


class ToastContainer(Vertical):
    """Contenedor para mostrar múltiples notificaciones toast."""

    def __init__(self):
        super().__init__()
        self.notifications = []

    def compose(self) -> ComposeResult:
        yield from ()

    def show_toast(self, message: str, level: str = "info", duration: float = 3.0):
        """Muestra una nueva notificación toast."""
        toast = ToastNotification(message, level, duration)
        self.notifications.append(toast)
        self.mount(toast)
        self.call_later(toast.show)

        # Auto-remover después de la duración
        self.set_timer(duration + 0.5, lambda: self.remove_toast(toast))

    def remove_toast(self, toast: ToastNotification):
        """Remueve una notificación toast."""
        if toast in self.notifications:
            self.notifications.remove(toast)
            toast.remove()


class LiveStats(Container):
    """Un widget para mostrar estadísticas en tiempo real."""

    def __init__(self):
        super().__init__()
        self._update_scheduled = False
        self._current_stats = {
            "queue_size": 0,
            "processed": 0,
            "SUCCESS": 0,
            "FAILED": 0,
            "RETRY": 0,
        }

    def compose(self) -> ComposeResult:
        yield Label("URLs en cola: 0", id="queue_label")
        yield Label("Procesadas: 0", id="processed_label")
        yield Label("Éxitos: 0", id="success_label")
        yield Label("Fallos: 0", id="failed_label")
        yield Label("Reintentos: 0", id="retry_label")

    def update_stats(self, stats: dict):
        """Actualiza las estadísticas con estrategia de buffer para evitar parpadeos."""
        # Actualizar los datos internamente
        for key, value in stats.items():
            if key in self._current_stats:
                self._current_stats[key] = value

        # Programar una actualización de UI si no hay una pendiente
        if not self._update_scheduled:
            self._update_scheduled = True
            self.call_after_refresh(self._apply_updates)

    def _apply_updates(self):
        """Aplica las actualizaciones a la UI como un solo lote."""
        try:
            self.query_one("#queue_label").update(
                f"URLs en cola: {self._current_stats['queue_size']}"
            )
            self.query_one("#processed_label").update(
                f"Procesadas: {self._current_stats['processed']}"
            )
            self.query_one("#success_label").update(f"Éxitos: {self._current_stats['SUCCESS']}")
            self.query_one("#failed_label").update(f"Fallos: {self._current_stats['FAILED']}")
            self.query_one("#retry_label").update(f"Reintentos: {self._current_stats['RETRY']}")
        finally:
            self._update_scheduled = False

    def reset(self):
        """Resetea las estadísticas a cero."""
        self._current_stats = {k: 0 for k in self._current_stats}
        for label in self.query(Label):
            base_text = label.renderable.split(":")[0]
            label.update(f"{base_text}: 0")


class DomainStats(Container):
    """Widget que muestra estadísticas de cada dominio."""

    def __init__(self):
        super().__init__()
        self._current_metrics = {}
        self._last_update_time = 0
        self._update_scheduled = False

    def compose(self) -> ComposeResult:
        table = DataTable(classes="domain-stats-table")
        # Textual < 0.50 no soporta kwarg 'headers'; añadimos columnas manualmente
        table.add_columns("Dominio", "Backoff", "Scraped", "Baja Calidad", "Vacío", "Fallos")
        yield table
        self.border_title = "Métricas por Dominio"

    def update_stats(self, domain_metrics: dict):
        """Actualiza las métricas por dominio con control de frecuencia para estabilidad."""
        # Actualizar métricas internamente
        self._current_metrics = domain_metrics.copy()

        # Limitar la frecuencia de actualización a máximo una vez cada 0.5 segundos
        import time
        current_time = time.time()
        if current_time - self._last_update_time < 0.5 and not self._update_scheduled:
            self._update_scheduled = True
            self.call_after_refresh(self._apply_updates)
        elif not self._update_scheduled:
            self._last_update_time = current_time
            self._apply_updates()

    def _apply_updates(self):
        """Actualiza la tabla con las métricas más recientes."""
        import time
        try:
            table = self.query_one(DataTable)
            table.clear()

            # Crear filas en lote para evitar múltiples refrescos
            rows = []
            for domain, metrics in self._current_metrics.items():
                rows.append((
                    domain,
                    f"{metrics.get('current_backoff_factor', 0):.2f}",
                    metrics.get("total_scraped", 0),
                    metrics.get("low_quality", 0),
                    metrics.get("empty", 0),
                    metrics.get("failed", 0),
                ))

            # Agregar todas las filas de una vez
            for row in rows:
                table.add_row(*row)
        finally:
            self._update_scheduled = False
            self._last_update_time = time.time()

    def reset(self):
        """Resetea la tabla de métricas."""
        self._current_metrics = {}
        self.query_one(DataTable).clear()


class BrainStats(Container):
    """Widget que muestra métricas del Brain adaptativo."""

    def __init__(self):
        super().__init__()
        self._last_snapshot = None

    def compose(self) -> ComposeResult:
        table = DataTable(classes="brain-stats-table", id="brain_stats_table")
        table.add_columns("Dominio", "Visitas", "Éxito%", "Error%", "LinkYield", "Prioridad")
        yield table
        yield Log(id="brain_recent_events", highlight=False)
        self.border_title = "Brain"

    def update_brain(self, snapshot: dict | None):
        if not snapshot:
            return
        self._last_snapshot = snapshot
        # Support hybrid snapshot structure
        if snapshot.get("hybrid_system"):
            # In hybrid, simple brain stats nested under 'simple_brain'
            domains = snapshot.get("simple_brain", {}).get("domains", {})
            recent_events = snapshot.get("simple_brain", {}).get("recent_events", [])
        else:
            domains = snapshot.get("domains", {})
            recent_events = snapshot.get("recent_events", [])
        table = self.query_one("#brain_stats_table", DataTable)
        table.clear()
        rows = []
        for domain, stats in domains.items():
            visits = stats.get("visits", 0)
            success_rate = (stats.get("success", 0) / visits) if visits else 0
            error_rate = (stats.get("errors", 0) / visits) if visits else 0
            link_yield = (stats.get("total_new_links", 0) / visits) if visits else 0
            priority = success_rate * 0.6 + link_yield * 0.4
            rows.append((domain, visits, f"{success_rate:.2f}", f"{error_rate:.2f}", f"{link_yield:.2f}", f"{priority:.2f}"))
        for row in rows:
            table.add_row(*row)
        # Recent events
        log = self.query_one("#brain_recent_events", Log)
        log.clear()
        for ev in recent_events[-10:]:
            log.write(f"{ev.get('status')} | {ev.get('domain')} | links={ev.get('new_links')} rt={ev.get('response_time')}")

    def reset(self):
        try:
            self.query_one("#brain_stats_table", DataTable).clear()
            self.query_one("#brain_recent_events", Log).clear()
        except Exception:
            pass


class IntelligenceStats(Container):
    """🧠 Widget que muestra estadísticas del sistema de inteligencia autónoma."""

    def __init__(self):
        super().__init__()
        self._intelligence_data = {
            "domains_learned": 0,
            "total_sessions": 0,
            "avg_success_rate": 0.0,
            "patterns_identified": 0,
            "strategies_optimized": 0,
            "last_learning": "Nunca"
        }

    def compose(self) -> ComposeResult:
        yield Static("🧠 Sistema de Inteligencia Autónoma", classes="intelligence-title")
        table = DataTable(classes="intelligence-table")
        table.add_columns("Métrica", "Valor")
        yield table
        self.border_title = "🧠 Inteligencia Autónoma"

    def update_intelligence_stats(self, intelligence_data: dict):
        """Actualiza las métricas de inteligencia."""
        self._intelligence_data.update(intelligence_data)
        self._refresh_display()

    def _refresh_display(self):
        """Actualiza la tabla con las métricas de inteligencia."""
        table = self.query_one(DataTable)
        table.clear()

        rows = [
            ("Dominios Aprendidos", self._intelligence_data["domains_learned"]),
            ("Sesiones de Scraping", self._intelligence_data["total_sessions"]),
            ("Tasa de Éxito Promedio", f"{self._intelligence_data['avg_success_rate']:.1%}"),
            ("Patrones Identificados", self._intelligence_data["patterns_identified"]),
            ("Estrategias Optimizadas", self._intelligence_data["strategies_optimized"]),
            ("Último Aprendizaje", self._intelligence_data["last_learning"]),
        ]

        for row in rows:
            table.add_row(*row)

    def reset(self):
        """Resetea las métricas de inteligencia."""
        self._intelligence_data = {
            "domains_learned": 0,
            "total_sessions": 0,
            "avg_success_rate": 0.0,
            "patterns_identified": 0,
            "strategies_optimized": 0,
            "last_learning": "Nunca"
        }
        self._refresh_display()


class ScraperTUIApp(App):
    """Una interfaz de usuario textual para Web Scraper PRO."""

    CSS_PATH = "styles.css"
    TITLE = "Scraper PRO"
    SUB_TITLE = "Un crawler y archivador web inteligente."

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("d", "toggle_dark", "Modo Oscuro"),
        ("s", "start", "Iniciar Crawling"),
        ("t", "stop", "Detener Crawling"),
        ("r", "toggle_robots", "Toggle Robots.txt"),
        ("e", "toggle_ethics", "Toggle Ética"),
        ("o", "toggle_offline", "Toggle Offline"),
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
        self.toast_container = ToastContainer()
        # Control para actualizaciones por lotes
        self._ui_update_scheduled = False
        self._last_update_time = 0
        self._ui_update_interval = 0.3  # Actualizar UI cada 0.3 segundos como máximo

    def compose(self) -> ComposeResult:
        """Crea los widgets de la aplicación."""
        # Toast container para notificaciones
        yield self.toast_container

        with Grid(id="app-grid"):
            with Container(id="left-pane"):
                yield Header()
                with TabbedContent(initial="crawl-tab"):
                    with TabPane("Crawl", id="crawl-tab"):
                        yield Label("URL de inicio:")
                        yield Input(placeholder="http://toscrape.com/", id="start_url")
                        yield Label("Trabajadores concurrentes:")
                        yield Input(value=str(settings.CONCURRENCY), id="concurrency")
                        yield Checkbox(
                            "Respetar robots.txt",
                            value=settings.ROBOTS_ENABLED,
                            id="respect_robots",
                        )
                        yield Checkbox(
                            "Activar comprobaciones Ética/Compliance",
                            value=settings.ETHICS_CHECKS_ENABLED,
                            id="ethics_checks",
                        )
                        yield Checkbox(
                            "Modo Offline (no LLM remoto)",
                            value=settings.OFFLINE_MODE,
                            id="offline_mode",
                        )
                        yield Checkbox("Usar Agente RL (WIP)", value=False, id="use_rl")
                    with TabPane("Estadísticas", id="stats-tab"):
                        yield LiveStats()
                        yield DomainStats()
                        yield IntelligenceStats()
                        yield BrainStats()

                with Container(id="actions-pane"):
                    yield Button(
                        "Iniciar Crawling",
                        variant="primary",
                        id="start_button",
                    )
                    yield Button(
                        "Detener Crawling",
                        variant="error",
                        id="stop_button",
                        disabled=True,
                    )

                with Container(id="progress-container"):
                    yield Label("Progreso:", id="stats_label")
                    yield ProgressBar(id="progress_bar", total=100, show_eta=False)
                    yield Label("Etapa: idle", id="stage_label")

                yield AlertsDisplay(id="alerts_display")  # New widget for alerts

                yield Button("Salir", variant="default", id="quit_button")

            with Container(id="right-pane"):
                yield Log(id="log_view", highlight=True)
        yield Footer()

    def show_toast(self, message: str, level: str = "info", duration: float = 3.0):
        """Muestra una notificación toast."""
        self.toast_container.show_toast(message, level, duration)

    def on_mount(self) -> None:
        """Se llama cuando la app se monta en el DOM."""
        log_widget = self.query_one("#log_view", Log)
        # Pasamos el handler de la TUI a la configuración de logging
        setup_logging(
            log_file_path=self.log_file_path,
            tui_handler=TextualHandler(log_widget),
        )
        self.query_one("#progress_bar").visible = False
        self.query_one(LiveStats).border_title = "Estadísticas Globales"
        self.query_one(DomainStats).border_title = "Métricas por Dominio"
        try:
            self.query_one(BrainStats).border_title = "Brain"
        except Exception:
            pass
        self.query_one(AlertsDisplay).border_title = "Alertas Críticas"
        self.query_one(AlertsDisplay).reset()  # Clear alerts on mount
        self.query_one("#stats_label").update("Listo para iniciar.")
        # Poner foco inicial en el campo de URL para que no necesites ratón
        try:
            self.query_one("#start_url").focus()
        except Exception:
            pass

        # Mostrar toast de bienvenida
        self.show_toast("¡Bienvenido a Scraper PRO!", "info", 2.0)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja los clics de los botones."""
        if event.button.id == "start_button":
            self.action_start_crawl()
        elif event.button.id == "stop_button":
            self.action_stop_crawl()
        elif event.button.id == "quit_button":
            self.action_quit()

    def action_start(self) -> None:
        """Binding para iniciar crawling vía teclado (s)."""
        self.action_start_crawl()

    def action_stop(self) -> None:
        """Binding para detener crawling vía teclado (t)."""
        self.action_stop_crawl()

    def action_toggle_robots(self) -> None:
        """Toggle respect robots.txt."""
        checkbox = self.query_one("#respect_robots", Checkbox)
        checkbox.value = not checkbox.value
        settings.ROBOTS_ENABLED = checkbox.value
        logging.info(f"Respect robots.txt: {checkbox.value}")

    def action_toggle_ethics(self) -> None:
        """Toggle ethics checks."""
        checkbox = self.query_one("#ethics_checks", Checkbox)
        checkbox.value = not checkbox.value
        settings.ETHICS_CHECKS_ENABLED = checkbox.value
        logging.info(f"Ethics checks: {checkbox.value}")

    def action_toggle_offline(self) -> None:
        """Toggle offline mode."""
        checkbox = self.query_one("#offline_mode", Checkbox)
        checkbox.value = not checkbox.value
        settings.OFFLINE_MODE = checkbox.value
        logging.info(f"Offline mode: {checkbox.value}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Cuando el usuario presiona Enter en un input, iniciar si es el campo URL."""
        if event.input.id == "start_url":
            # Simular pulsar iniciar
            self.action_start_crawl()

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
        self.toast_container = ToastContainer()
        # Control para actualizaciones por lotes
        self._ui_update_scheduled = False
        self._last_update_time = 0
        self._ui_update_interval = 0.3  # Actualizar UI cada 0.3 segundos como máximo

    def stats_update_callback(self, update: dict):
        """Callback que el orquestador llamará para actualizar las estadísticas."""
        # Actualizar estadísticas globales en la estructura de datos
        self.live_stats_data["processed"] += update.get("processed", 0)
        queue_size = update.get("queue_size", self.live_stats_data["queue_size"])
        self.live_stats_data["queue_size"] = queue_size

        status = update.get("status")
        if status in self.live_stats_data:
            self.live_stats_data[status] += 1

        # Actualizar métricas por dominio si están disponibles
        domain_metrics_data = update.get("domain_metrics")
        if domain_metrics_data:
            self.domain_metrics = domain_metrics_data

        # Brain snapshot integration (envía métricas adaptativas a BrainStats)
        brain_snapshot = update.get("brain")
        if brain_snapshot:
            try:
                self.query_one(BrainStats).update_brain(brain_snapshot)
            except Exception:
                pass

        # 🧠 Actualizar métricas de inteligencia si están disponibles
        intelligence_data = update.get("intelligence_metrics")
        if intelligence_data:
            try:
                intelligence_widget = self.query_one(IntelligenceStats)
                intelligence_widget.update_intelligence_stats(intelligence_data)
            except Exception as e:
                # Silently handle if widget not found (during initialization)
                pass

        # Programar actualización de UI si no hay una programada ya
        import time
        current_time = time.time()
        if not self._ui_update_scheduled and (current_time - self._last_update_time > self._ui_update_interval):
            self._last_update_time = current_time
            self._update_ui_now()
        elif not self._ui_update_scheduled:
            self._ui_update_scheduled = True
            self.call_after_refresh(self._update_ui_batch)

        # Actualizar barra de progreso basada en processed/(processed+queue)
        try:
            total_est = self.live_stats_data["processed"] + self.live_stats_data["queue_size"]
            if total_est > 0:
                ratio = self.live_stats_data["processed"] / total_est
                progress_bar = self.query_one(ProgressBar)
                progress_bar.update(progress=int(ratio * 100))
        except Exception:
            pass

    def _update_ui_now(self):
        """Actualiza la UI inmediatamente."""
        # Actualizar el widget de estadísticas en vivo
        self.query_one(LiveStats).update_stats(self.live_stats_data)

        # Actualizar métricas por dominio
        self.query_one(DomainStats).update_stats(self.domain_metrics)

        # Actualizar barra de progreso y etiquetas
        self._update_progress_and_labels()

    def _update_ui_batch(self):
        """Actualiza la UI como un lote después de un período de espera."""
        try:
            self._update_ui_now()
        finally:
            self._ui_update_scheduled = False
            import time
            self._last_update_time = time.time()

    def _update_progress_and_labels(self):
        """Actualiza la barra de progreso y etiquetas relacionadas."""
        processed_count = self.live_stats_data["processed"]
        queue_size = self.live_stats_data["queue_size"]
        total_urls = processed_count + queue_size

        progress_bar = self.query_one(ProgressBar)
        stats_label = self.query_one("#stats_label")

        if total_urls > 0:
            progress_bar.total = total_urls
            progress_bar.progress = processed_count
            percentage = (processed_count / total_urls) * 100
            stats_label.update(
                f"Procesadas: {processed_count}/{total_urls} " f"({percentage:.2f}%)"
            )

        # Actualizar etiqueta de etapa y porcentaje estilo "hacker"
        try:
            percentage = (processed_count / total_urls) * 100 if total_urls > 0 else 0
            # Determinar etapa por condiciones simples
            if total_urls == 0:
                stage = "Idle"
            elif queue_size > 0 and processed_count == 0:
                stage = "Queueing"
            elif processed_count < total_urls:
                stage = "Crawling"
            else:
                stage = "Finalizing"

            stage_text = f"{stage} — {processed_count}/{total_urls} ({percentage:.0f}%)"
            self.query_one("#stage_label").update(f"[green]{stage_text}[/]")
        except Exception:
            pass

    def alert_callback(self, message: str, level: str = "warning"):
        """Callback para que el orquestador envíe alertas a la TUI."""
        self.call_later(self.query_one(AlertsDisplay).add_alert, message, level)

    def action_start_crawl(self) -> None:
        """Inicia el proceso de crawling en un worker."""
        start_url_input = self.query_one("#start_url", Input)
        concurrency_input = self.query_one("#concurrency", Input)
        respect_robots_checkbox = self.query_one("#respect_robots", Checkbox)
        ethics_checkbox = self.query_one("#ethics_checks", Checkbox)
        offline_checkbox = self.query_one("#offline_mode", Checkbox)
        use_rl_checkbox = self.query_one("#use_rl", Checkbox)

        start_url = start_url_input.value
        if not start_url:
            self.query_one("#stats_label").update(
                "[bold red]Error: La URL de inicio es obligatoria.[/]"
            )
            self.show_toast("URL de inicio requerida", "error")
            return

        try:
            concurrency = int(concurrency_input.value)
        except ValueError:
            self.query_one("#stats_label").update(
                "[bold red]Error: La concurrencia debe ser un número.[/]"
            )
            self.show_toast("Valor de concurrencia inválido", "error")
            return

        self.set_ui_for_crawling(True)
        # Reiniciar estadísticas
        self.live_stats_data = {k: 0 for k in self.live_stats_data}
        self.query_one("#stats_label").update("Iniciando...")
        # Mostrar etapa inicial
        try:
            self.query_one("#stage_label").update("[green]Starting... 0%[/]")
        except Exception:
            pass
        self.query_one(ProgressBar).update(total=100, progress=0)
        self.query_one(LiveStats).reset()
        self.query_one(DomainStats).reset()  # Reset domain stats too
        try:
            self.query_one(BrainStats).reset()
        except Exception:
            pass
        self.query_one(AlertsDisplay).reset()  # Reset alerts

        # Mostrar toast de inicio
        self.show_toast(f"Iniciando crawling desde {start_url}", "info")

        # Aplicar toggles runtime a settings global para componentes subsiguientes
        settings.ROBOTS_ENABLED = respect_robots_checkbox.value
        settings.ETHICS_CHECKS_ENABLED = ethics_checkbox.value
        settings.OFFLINE_MODE = offline_checkbox.value

        self.scraper_worker = self.run_worker(
            self.crawl_worker(
                start_urls=[start_url],
                db_path=settings.DB_PATH,
                concurrency=concurrency,
                respect_robots_txt=respect_robots_checkbox.value,
                use_rl=use_rl_checkbox.value,
                stats_callback=self.stats_update_callback,
                alert_callback=self.alert_callback,
            ),
            name="ScraperWorker",
        )

    def action_stop_crawl(self) -> None:
        """Detiene el worker de crawling."""
        if self.scraper_worker:
            logging.warning("Deteniendo el crawling...")
            self.scraper_worker.cancel()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Se llama cuando el estado del worker cambia."""
        if event.worker.name == "ScraperWorker":
            if event.state == WorkerState.SUCCESS:
                logging.info("El proceso de crawling ha finalizado con éxito.")
                self.query_one(ProgressBar).update(total=100, progress=100)
                self.query_one("#stats_label").update(
                    "¡Crawling completado!"
                )
                try:
                    self.query_one("#stage_label").update("[green]Completed — 100%[/]")
                except Exception:
                    pass
                self.show_toast("Crawling completado exitosamente", "success", 4.0)
            elif event.state == WorkerState.CANCELLED:
                logging.warning("El proceso de crawling ha sido cancelado.")
                self.query_one("#stats_label").update(
                    "Proceso detenido por el usuario."
                )
                try:
                    self.query_one("#stage_label").update("[yellow]Cancelled[/]")
                except Exception:
                    pass
                self.show_toast("Crawling cancelado", "warning", 3.0)
            elif event.state == WorkerState.ERROR:
                logging.error(
                    "El worker de crawling ha fallado: %s",
                    event.worker.error,
                )
                self.query_one(ProgressBar).add_class("error")
                self.query_one("#stats_label").update(
                    "[bold red]Error durante el crawling.[/]"
                )
                try:
                    self.query_one("#stage_label").update("[red]Error during crawling[/]")
                except Exception:
                    pass
                self.show_toast("Error durante el crawling", "error", 5.0)

            # En cualquier caso de finalización, restaurar la UI
            if event.state in (
                WorkerState.SUCCESS,
                WorkerState.CANCELLED,
                WorkerState.ERROR,
            ):
                self.set_ui_for_crawling(False)

    def set_ui_for_crawling(self, is_crawling: bool) -> None:
        """Habilita o deshabilita los controles de la UI durante el crawling."""
        self.query_one("#start_button").disabled = is_crawling
        self.query_one("#stop_button").disabled = not is_crawling
        self.query_one("#start_url").disabled = is_crawling
        self.query_one("#concurrency").disabled = is_crawling
        # Permitir cambiar configuraciones en tiempo real durante el crawling
        # self.query_one("#respect_robots").disabled = is_crawling
        # self.query_one("#ethics_checks").disabled = is_crawling
        # self.query_one("#offline_mode").disabled = is_crawling
        # self.query_one("#use_rl").disabled = is_crawling

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
        self,
        start_urls: list[str],
        db_path: str,
        concurrency: int,
        respect_robots_txt: bool,
        use_rl: bool,
        stats_callback,
        alert_callback,
    ) -> None:
        """
        Función de trabajo (worker) que invoca al corredor de crawling centralizado.
        """
        logging.info(f"Iniciando crawling para: {start_urls}")
        await run_crawler(
            start_urls=start_urls,
            db_path=db_path,
            concurrency=concurrency,
            respect_robots_txt=respect_robots_txt,
            use_rl=use_rl,
            stats_callback=stats_callback,
            alert_callback=alert_callback,
        )

    def action_quit(self) -> None:
        """Sale de la aplicación."""
        self.exit()
