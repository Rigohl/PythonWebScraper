import logging
from pathlib import Path

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
    Static,
    TabbedContent,
    TabPane,
)
from textual.worker import Worker, WorkerState

from ..runner import run_crawler, setup_logging
from ..settings import settings
from .ui_prefs import load_prefs, save_prefs

# Importaciones para AI Assistant
try:
    from ..ai_assistant_integrator import AIAssistantIntegrator

    AI_ASSISTANT_AVAILABLE = True
except ImportError:
    AI_ASSISTANT_AVAILABLE = False
    logging.warning("AI Assistant modules not available")


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
            total = self._current_stats["processed"] or 1
            success = self._current_stats["SUCCESS"]
            failed = self._current_stats["FAILED"]
            retry = self._current_stats["RETRY"]
            success_rate = success / total
            fail_rate = failed / total
            retry_rate = retry / total

            # Colorear según umbrales
            if success_rate >= 0.8:
                success_color = "green"
            elif success_rate >= 0.5:
                success_color = "yellow"
            else:
                success_color = "red"

            if fail_rate >= 0.4:
                fail_color = "red"
            elif fail_rate >= 0.2:
                fail_color = "yellow"
            else:
                fail_color = "green"

            if retry_rate >= 0.3:
                retry_color = "yellow"
            else:
                retry_color = "green"

            self.query_one("#queue_label").update(
                f"Cola: [bold]{self._current_stats['queue_size']}[/]"
            )
            self.query_one("#processed_label").update(
                f"Procesadas: [bold]{self._current_stats['processed']}[/]"
            )
            self.query_one("#success_label").update(
                f"Éxitos: [bold {success_color}]{success}[/] ({success_rate:.0%})"
            )
            self.query_one("#failed_label").update(
                f"Fallos: [bold {fail_color}]{failed}[/] ({fail_rate:.0%})"
            )
            self.query_one("#retry_label").update(
                f"Reintentos: [bold {retry_color}]{retry}[/] ({retry_rate:.0%})"
            )
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
        table.add_columns(
            "Dominio", "Backoff", "Scraped", "Baja Calidad", "Vacío", "Fallos"
        )
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
                backoff = metrics.get("current_backoff_factor", 0)
                failed = metrics.get("failed", 0)
                low_q = metrics.get("low_quality", 0)
                scraped = metrics.get("total_scraped", 0)
                # Derivar ratios
                fail_rate = (failed / scraped) if scraped else 0
                low_rate = (low_q / scraped) if scraped else 0

                def colorize(val, rate):
                    if rate >= 0.5:
                        return f"[red]{val}[/]"
                    elif rate >= 0.2:
                        return f"[yellow]{val}[/]"
                    else:
                        return f"[green]{val}[/]"

                backoff_txt = (
                    f"[yellow]{backoff:.2f}[/]"
                    if backoff > 2
                    else f"[green]{backoff:.2f}[/]"
                )
                scraped_txt = f"{scraped}"
                low_txt = colorize(low_q, low_rate)
                empty_txt = (
                    f"[yellow]{metrics.get('empty', 0)}[/]"
                    if metrics.get("empty", 0) > 0
                    else "0"
                )
                failed_txt = colorize(failed, fail_rate)
                rows.append(
                    (domain, backoff_txt, scraped_txt, low_txt, empty_txt, failed_txt)
                )

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
        table.add_columns(
            "Dominio", "Visitas", "Éxito%", "Error%", "LinkYield", "Prioridad"
        )
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

            def rate_color(r):
                if r >= 0.8:
                    return "green"
                if r >= 0.5:
                    return "yellow"
                return "red"

            def yield_color(y):
                if y >= 1.5:
                    return "green"
                if y >= 0.5:
                    return "yellow"
                return "red"

            sr_txt = f"[{rate_color(success_rate)}]{success_rate:.2f}[/]"
            er_txt = f"[{rate_color(error_rate)}]{error_rate:.2f}[/]"
            ly_txt = f"[{yield_color(link_yield)}]{link_yield:.2f}[/]"
            pr_txt = f"[{rate_color(priority)}]{priority:.2f}[/]"
            rows.append((domain, visits, sr_txt, er_txt, ly_txt, pr_txt))
        for row in rows:
            table.add_row(*row)
        # Recent events
        log = self.query_one("#brain_recent_events", Log)
        log.clear()
        for ev in recent_events[-10:]:
            log.write(
                f"{ev.get('status')} | {ev.get('domain')} | links={ev.get('new_links')} rt={ev.get('response_time')}"
            )

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
            "last_learning": "Nunca",
        }

    def compose(self) -> ComposeResult:
        yield Static(
            "🧠 Sistema de Inteligencia Autónoma", classes="intelligence-title"
        )
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
            (
                "Tasa de Éxito Promedio",
                f"{self._intelligence_data['avg_success_rate']:.1%}",
            ),
            ("Patrones Identificados", self._intelligence_data["patterns_identified"]),
            (
                "Estrategias Optimizadas",
                self._intelligence_data["strategies_optimized"],
            ),
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
            "last_learning": "Nunca",
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
        ("p", "pause_resume", "Pausar/Resume"),
        ("r", "toggle_robots", "Toggle Robots.txt"),
        ("e", "toggle_ethics", "Toggle Ética"),
        ("o", "toggle_offline", "Toggle Offline"),
        ("?", "help", "Ayuda"),
        ("a", "toggle_autoscroll", "AutoScroll Log"),
        ("c", "clear_log", "Limpiar Log"),
        ("/", "focus_url", "Foco URL"),
        ("l", "toggle_log_panel", "Mostrar/Ocultar Log"),
        ("x", "export_markdown", "Export MD"),
        ("i", "ai_search", "🔍 AI Search"),
        ("v", "voice_chat", "🎤 Voice Chat"),
        ("h", "ai_history", "📋 AI History"),
    ]

    class IntelligenceBanner(Static):
        """Barra superior mostrando el estado inteligente del sistema."""

        def on_mount(self):  # type: ignore[override]
            self.update("[bold green]Inicializando Inteligencia...[/]")

    class HelpOverlay(Static):
        """Overlay simple con ayuda de atajos."""

        DEFAULT_HELP = (
            "[bold underline]Atajos Clave[/]\n"
            "s: Iniciar  |  t: Detener  |  p: Pausa/Resume  |  q: Salir\n"
            "r: Robots  |  e: Ética  |  o: Offline  |  d: Tema oscuro\n"
            "l: Mostrar/Ocultar Log  |  x: Export MD  |  a: Autoscroll\n"
            "c: Limpiar log  |  /: Foco URL | Enter (en URL): iniciar\n"
            "[bold cyan]🤖 AI Assistant:[/]\n"
            "i: Búsqueda Inteligente  |  v: Chat por Voz  |  h: Historial AI\n"
            "Persistencia: autoscroll & visibilidad log se recuerdan\n"
            "Navegación tablas: cursores / tab  |  Esc: cerrar overlays\n"
        )

        def __init__(self):
            super().__init__(self.DEFAULT_HELP, id="help_overlay")
            self.visible = False

        def toggle(self):
            self.visible = not self.visible
            self.display = "block" if self.visible else "none"

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
        self._autoscroll_log = True

        # AI Assistant integration
        self.ai_assistant: AIAssistantIntegrator | None = None
        self.ai_worker: Worker | None = None
        self.ai_initialized = False

    def compose(self) -> ComposeResult:
        """Crea los widgets de la aplicación."""
        # Toast container para notificaciones
        yield self.toast_container

        with Grid(id="app-grid"):
            with Container(id="left-pane"):
                yield Header()
                yield self.IntelligenceBanner(id="intelligence_banner")
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
                    with TabPane("🤖 AI Assistant", id="ai-tab"):
                        yield Label("🔍 Búsqueda Inteligente:")
                        yield Input(
                            placeholder="Buscar información sobre...",
                            id="ai_search_topic",
                        )
                        yield Button("Buscar", variant="primary", id="ai_search_button")
                        yield Label("📄 Generar Documentos:")
                        with Container(id="doc-format-container"):
                            yield Checkbox("Markdown", value=True, id="format_md")
                            yield Checkbox(
                                "Word (.docx)", value=False, id="format_docx"
                            )
                            yield Checkbox(
                                "Excel (.xlsx)", value=False, id="format_xlsx"
                            )
                            yield Checkbox(
                                "PowerPoint (.pptx)", value=False, id="format_pptx"
                            )
                        yield Button(
                            "🎤 Iniciar Chat por Voz",
                            variant="success",
                            id="voice_chat_button",
                        )
                        yield Button(
                            "📋 Ver Historial",
                            variant="default",
                            id="ai_history_button",
                        )
                        yield Static("Estado AI: No inicializado", id="ai_status")
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
                    yield Button(
                        "Exportar MD",
                        variant="default",
                        id="export_md_button",
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
        yield self.HelpOverlay()
        yield Label("Status: listo", id="status_bar")

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
        # Actualizar banner de inteligencia inicial
        self.update_intelligence_banner()
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
        # Cargar preferencias de UI
        self._prefs = load_prefs()
        self._autoscroll_log = self._prefs.get("autoscroll_log", True)
        self._show_log_panel = self._prefs.get("show_log_panel", True)
        if not self._show_log_panel:
            try:
                self.query_one("#right-pane").display = "none"
            except Exception:
                pass
        # Mostrar toast de bienvenida
        self.show_toast("¡Bienvenido a Scraper PRO!", "info", 2.0)

        # Inicializar AI Assistant automáticamente
        if AI_ASSISTANT_AVAILABLE:
            self.call_later(self.initialize_ai_assistant)
        else:
            self.query_one("#ai_status").update(
                "Estado AI: Dependencias no disponibles"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Maneja los clics de los botones."""
        if event.button.id == "start_button":
            self.action_start_crawl()
        elif event.button.id == "stop_button":
            self.action_stop_crawl()
        elif event.button.id == "quit_button":
            self.action_quit()
        elif event.button.id == "ai_search_button":
            self.action_ai_search()
        elif event.button.id == "voice_chat_button":
            self.action_voice_chat()
        elif event.button.id == "ai_history_button":
            self.action_ai_history()

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
        self.update_intelligence_banner()

    def action_toggle_ethics(self) -> None:
        """Toggle ethics checks."""
        checkbox = self.query_one("#ethics_checks", Checkbox)
        checkbox.value = not checkbox.value
        settings.ETHICS_CHECKS_ENABLED = checkbox.value
        logging.info(f"Ethics checks: {checkbox.value}")
        self.update_intelligence_banner()

    def action_toggle_offline(self) -> None:
        """Toggle offline mode."""
        checkbox = self.query_one("#offline_mode", Checkbox)
        checkbox.value = not checkbox.value
        settings.OFFLINE_MODE = checkbox.value
        logging.info(f"Offline mode: {checkbox.value}")
        self.update_intelligence_banner()

    def action_help(self) -> None:
        """Muestra/oculta overlay de ayuda."""
        try:
            overlay = self.query_one("#help_overlay", self.HelpOverlay)
            overlay.toggle()
        except Exception:
            pass

    def action_toggle_autoscroll(self) -> None:
        """Activa o desactiva auto scroll del log y persiste preferencia."""
        self._autoscroll_log = not self._autoscroll_log
        if not hasattr(self, "_prefs"):
            self._prefs = {}
        self._prefs["autoscroll_log"] = self._autoscroll_log
        save_prefs(self._prefs)
        try:
            status = "ON" if self._autoscroll_log else "OFF"
            self.show_toast(f"Autoscroll Log {status}", "info")
        except Exception:
            pass

    def action_clear_log(self) -> None:
        """Limpia el widget de log."""
        try:
            self.query_one("#log_view", Log).clear()
            self.show_toast("Log limpiado", "success")
        except Exception:
            pass

    def action_focus_url(self) -> None:
        """Pone foco en el campo URL."""
        try:
            self.query_one("#start_url", Input).focus()
        except Exception:
            pass

    def action_toggle_log_panel(self) -> None:
        """Muestra u oculta el panel de log y persiste preferencia."""
        try:
            pane = self.query_one("#right-pane")
            currently = pane.display != "none"
            pane.display = "none" if currently else "block"
            if not hasattr(self, "_prefs"):
                self._prefs = {}
            self._prefs["show_log_panel"] = not currently
            save_prefs(self._prefs)
            self.show_toast("Log oculto" if currently else "Log visible", "info")
        except Exception:
            pass

    def action_pause_resume(self) -> None:
        """Pausa o reanuda la actualización de UI (buffer stats)."""
        self._paused = not getattr(self, "_paused", False)
        state = "Pausado" if self._paused else "Reanudado"
        self.show_toast(f"{state}", "warning" if self._paused else "success")

    def action_export_markdown(self) -> None:
        """Exporta un reporte markdown manualmente usando la base de datos configurada."""
        try:
            from ..database import DatabaseManager  # type: ignore
        except Exception:
            self.show_toast("Export no disponible", "error")
            return
        try:
            db = DatabaseManager(settings.DB_PATH)
            md_path = Path("exports/manual_export.md")
            md_path.parent.mkdir(parents=True, exist_ok=True)
            with md_path.open("w", encoding="utf-8") as f:
                f.write(db.export_to_markdown())
            self.show_toast(f"MD exportado: {md_path}", "success", 4.0)
        except Exception:
            self.show_toast("Error exportando MD", "error")

    def update_intelligence_banner(self) -> None:
        """Construye y actualiza la línea de estado de inteligencia con anomalías."""
        try:
            banner = self.query_one("#intelligence_banner", self.IntelligenceBanner)
        except Exception:
            return

        parts: list[str] = []
        parts.append("[bold green]Scraper PRO Inteligente[/]")
        parts.append(
            "🤖 Robots:"
            + ("[green]ON[/]" if settings.ROBOTS_ENABLED else "[red]OFF[/]")
        )
        parts.append(
            "⚖ Ética:"
            + ("[green]ON[/]" if settings.ETHICS_CHECKS_ENABLED else "[yellow]OFF[/]")
        )
        parts.append(
            "📡 Offline:"
            + ("[yellow]ON[/]" if settings.OFFLINE_MODE else "[green]OFF[/]")
        )
        try:
            rl_enabled = self.query_one("#use_rl", Checkbox).value
        except Exception:
            rl_enabled = False
        parts.append("🧪 RL:" + ("[green]ON[/]" if rl_enabled else "[grey]OFF[/]"))
        try:
            processed = self.live_stats_data.get("processed", 0)
            success = self.live_stats_data.get("SUCCESS", 0)
            failed = self.live_stats_data.get("FAILED", 0)
            if processed > 0:
                rate = success / processed
                fail_rate = failed / processed
                if rate >= 0.8:
                    color = "green"
                elif rate >= 0.5:
                    color = "yellow"
                else:
                    color = "red"
                parts.append(f"🎯 Éxito:[bold {color}]{rate:.0%}[/]")
                if fail_rate >= 0.4:
                    parts.append(f"⚠ [bold red]Fallas {fail_rate:.0%}[/]")
        except Exception:
            pass
        # Backoff máximo
        try:
            max_backoff = 0
            for m in self.domain_metrics.values():
                bf = m.get("current_backoff_factor", 0)
                if bf > max_backoff:
                    max_backoff = bf
            if max_backoff > 2:
                parts.append(f"⏳ Backoff:[bold yellow]{max_backoff:.1f}x[/]")
        except Exception:
            pass
        if getattr(self, "_paused", False):
            parts.append("[bold yellow]PAUSADO[/]")
        banner.update("  |  ".join(parts))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Cuando el usuario presiona Enter en un input, iniciar si es el campo URL."""
        if event.input.id == "start_url":
            # Simular pulsar iniciar
            self.action_start_crawl()

    def stats_update_callback(self, update: dict):
        """Callback que el orquestador llamará para actualizar las estadísticas."""
        if getattr(self, "_paused", False):
            # Buffer de datos sin refrescar UI para mantener rendimiento
            self.live_stats_data["processed"] += update.get("processed", 0)
            status = update.get("status")
            if status in self.live_stats_data:
                self.live_stats_data[status] += 1
            dm = update.get("domain_metrics")
            if dm:
                self.domain_metrics = dm
            return
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
        if not self._ui_update_scheduled and (
            current_time - self._last_update_time > self._ui_update_interval
        ):
            self._last_update_time = current_time
            self._update_ui_now()
        elif not self._ui_update_scheduled:
            self._ui_update_scheduled = True
            self.call_after_refresh(self._update_ui_batch)

        # Actualizar barra de progreso basada en processed/(processed+queue)
        try:
            total_est = (
                self.live_stats_data["processed"] + self.live_stats_data["queue_size"]
            )
            if total_est > 0:
                ratio = self.live_stats_data["processed"] / total_est
                progress_bar = self.query_one(ProgressBar)
                progress_bar.update(progress=int(ratio * 100))
        except Exception:
            pass

        # Actualizar barra de estado (throughput + éxito + elapsed + pausa)
        try:
            processed = self.live_stats_data["processed"]
            success = self.live_stats_data.get("SUCCESS", 0)
            failed = self.live_stats_data.get("FAILED", 0)
            total = processed or 1
            success_rate = success / total
            from time import time

            if not hasattr(self, "_start_time"):
                self._start_time = time()
            elapsed = max(time() - self._start_time, 0.001)
            throughput = processed / elapsed
            mm = int(elapsed // 60)
            ss = int(elapsed % 60)
            if success_rate >= 0.8:
                rate_color = "green"
            elif success_rate >= 0.5:
                rate_color = "yellow"
            else:
                rate_color = "red"
            paused_flag = (
                " [yellow][PAUSADO][/]" if getattr(self, "_paused", False) else ""
            )
            self.query_one("#status_bar", Label).update(
                f"Status: {processed} ok=[{rate_color}]{success}[/] fail={failed} rate=[bold {rate_color}]{success_rate:.0%}[/] TPS={throughput:.2f} t={mm:02d}:{ss:02d}{paused_flag}"
            )
        except Exception:
            pass
        # Actualizar banner para anomalías y estado de pausa
        self.update_intelligence_banner()

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
        # Reiniciar cronómetro de sesión
        try:
            from time import time as _now

            self._start_time = _now()
        except Exception:
            pass

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
                self.query_one("#stats_label").update("¡Crawling completado!")
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
                    self.query_one("#stage_label").update(
                        "[red]Error during crawling[/]"
                    )
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

    async def initialize_ai_assistant(self) -> None:
        """Inicializa el AI Assistant de forma asíncrona."""
        if not AI_ASSISTANT_AVAILABLE:
            self.show_toast(
                "AI Assistant no disponible - dependencias faltantes", "warning", 5.0
            )
            self.query_one("#ai_status").update("Estado AI: No disponible")
            return

        try:
            self.query_one("#ai_status").update("Estado AI: Inicializando...")
            self.ai_assistant = AIAssistantIntegrator()

            # Ejecutar inicialización en un worker para no bloquear UI
            self.ai_worker = self.run_worker(
                self.ai_initialization_worker(),
                name="ai_initialization",
                description="Inicializando AI Assistant",
            )

        except Exception as e:
            logging.error(f"Error inicializando AI Assistant: {e}")
            self.show_toast(f"Error: {e}", "error", 5.0)
            self.query_one("#ai_status").update("Estado AI: Error")

    async def ai_initialization_worker(self) -> None:
        """Worker para inicializar el AI Assistant."""
        try:
            if self.ai_assistant:
                init_result = await self.ai_assistant.initialize_system()

                if init_result["status"] in ["success", "partial"]:
                    self.ai_initialized = True
                    active_components = sum(
                        1
                        for status in init_result["components"].values()
                        if status == "success"
                    )
                    self.call_from_thread(
                        self.query_one("#ai_status").update,
                        f"Estado AI: Activo ({active_components}/4 componentes)",
                    )
                    self.call_from_thread(
                        self.show_toast,
                        f"AI Assistant inicializado: {active_components}/4 componentes activos",
                        "success",
                        4.0,
                    )
                else:
                    self.call_from_thread(
                        self.query_one("#ai_status").update,
                        "Estado AI: Error en inicialización",
                    )
                    self.call_from_thread(
                        self.show_toast,
                        "Error inicializando AI Assistant",
                        "error",
                        5.0,
                    )

        except Exception as e:
            logging.error(f"Error en worker de inicialización AI: {e}")
            self.call_from_thread(
                self.query_one("#ai_status").update, "Estado AI: Error"
            )

    def action_ai_search(self) -> None:
        """Inicia búsqueda inteligente."""
        if not self.ai_initialized or not self.ai_assistant:
            self.show_toast("AI Assistant no está inicializado", "warning", 3.0)
            return

        search_input = self.query_one("#ai_search_topic", Input)
        topic = search_input.value.strip()

        if not topic:
            self.show_toast("Ingresa un tema para buscar", "warning", 3.0)
            search_input.focus()
            return

        # Obtener formatos seleccionados
        selected_formats = []
        if self.query_one("#format_md", Checkbox).value:
            selected_formats.append("md")
        if self.query_one("#format_docx", Checkbox).value:
            selected_formats.append("docx")
        if self.query_one("#format_xlsx", Checkbox).value:
            selected_formats.append("xlsx")
        if self.query_one("#format_pptx", Checkbox).value:
            selected_formats.append("pptx")

        if not selected_formats:
            selected_formats = ["md"]  # Por defecto markdown

        # Ejecutar búsqueda en worker
        self.ai_worker = self.run_worker(
            self.ai_search_worker(topic, selected_formats),
            name="ai_search",
            description=f"Buscando: {topic}",
        )

        self.show_toast(f"Iniciando búsqueda sobre: {topic}", "info", 3.0)
        logging.info(
            f"AI: Iniciando búsqueda sobre '{topic}' con formatos {selected_formats}"
        )

    async def ai_search_worker(self, topic: str, formats: list) -> None:
        """Worker para realizar búsqueda inteligente."""
        try:
            if not self.ai_assistant:
                return

            # Procesar solicitud con el AI Assistant
            request = f"Busca información detallada sobre {topic} y genera documentos en formatos {', '.join(formats)}"

            result = await self.ai_assistant.process_user_request(request, "text")

            if result["status"] == "completed":
                final_response = result.get("final_response", {})
                summary = final_response.get("summary", "Búsqueda completada")
                artifacts = final_response.get("artifacts_generated", [])

                # Mostrar resultados en UI
                self.call_from_thread(
                    self.show_toast,
                    f"Búsqueda completada: {len(artifacts)} documentos generados",
                    "success",
                    5.0,
                )

                # Log detallado
                logging.info(f"AI Search completada para '{topic}':")
                logging.info(f"Resumen: {summary[:200]}...")

                for artifact in artifacts:
                    logging.info(
                        f"Generado: {artifact['format'].upper()} - {artifact['location']}"
                    )

            else:
                error_msg = result.get("error", "Error desconocido")
                self.call_from_thread(
                    self.show_toast, f"Error en búsqueda: {error_msg}", "error", 5.0
                )
                logging.error(f"Error en AI Search: {error_msg}")

        except Exception as e:
            logging.error(f"Error en worker de búsqueda AI: {e}")
            self.call_from_thread(
                self.show_toast, f"Error inesperado: {e}", "error", 5.0
            )

    def action_voice_chat(self) -> None:
        """Inicia chat por voz."""
        if not self.ai_initialized or not self.ai_assistant:
            self.show_toast("AI Assistant no está inicializado", "warning", 3.0)
            return

        # Ejecutar chat por voz en worker
        self.ai_worker = self.run_worker(
            self.voice_chat_worker(),
            name="voice_chat",
            description="Chat por voz activo",
        )

        self.show_toast("Iniciando chat por voz... Habla ahora", "info", 4.0)
        logging.info("AI: Iniciando conversación por voz")

    async def voice_chat_worker(self) -> None:
        """Worker para chat por voz."""
        try:
            if not self.ai_assistant:
                return

            conversation_result = await self.ai_assistant.execute_voice_conversation()

            if conversation_result["status"] == "completed":
                self.call_from_thread(
                    self.show_toast, "Conversación por voz completada", "success", 3.0
                )
                logging.info("Conversación por voz completada exitosamente")
            else:
                error_msg = conversation_result.get("reason", "Voz no disponible")
                self.call_from_thread(
                    self.show_toast, f"Chat por voz: {error_msg}", "warning", 4.0
                )
                logging.warning(f"Chat por voz no disponible: {error_msg}")

        except Exception as e:
            logging.error(f"Error en chat por voz: {e}")
            self.call_from_thread(
                self.show_toast, f"Error en chat por voz: {e}", "error", 5.0
            )

    def action_ai_history(self) -> None:
        """Muestra historial del AI Assistant."""
        if not self.ai_initialized or not self.ai_assistant:
            self.show_toast("AI Assistant no está inicializado", "warning", 3.0)
            return

        try:
            history = self.ai_assistant.get_session_history(5)

            if not history:
                self.show_toast("No hay historial disponible", "info", 3.0)
                return

            # Mostrar historial en el log
            log_widget = self.query_one("#log_view", Log)
            log_widget.write("\n" + "=" * 60)
            log_widget.write("[bold cyan]HISTORIAL AI ASSISTANT[/]")
            log_widget.write("=" * 60)

            for i, session in enumerate(history, 1):
                timestamp = session.get("timestamp", "N/A")
                request = session.get("request", "N/A")[:100] + "..."
                status = session.get("status", "N/A")
                components = ", ".join(session.get("components_used", []))

                log_widget.write(f"\n[bold]{i}. {timestamp}[/]")
                log_widget.write(f"   Solicitud: {request}")
                log_widget.write(f"   Estado: {status}")
                log_widget.write(f"   Componentes: {components}")

            log_widget.write("=" * 60 + "\n")

            self.show_toast(f"Historial mostrado: {len(history)} sesiones", "info", 3.0)

        except Exception as e:
            logging.error(f"Error mostrando historial AI: {e}")
            self.show_toast(f"Error: {e}", "error", 3.0)

    def action_quit(self) -> None:
        """Sale de la aplicación."""
        self.exit()
