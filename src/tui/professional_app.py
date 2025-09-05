# src/tui/professional_app.py

from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, TabbedContent, TabPane, Button, Input, Label,
    Checkbox, ProgressBar, Static, DataTable, Switch, RadioSet,
    RadioButton, ListView, ListItem, Tree, Collapsible,
    LoadingIndicator, Digits, RichLog
)
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual.worker import get_current_worker
from textual import events
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box
from datetime import datetime
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional

from ..intelligence import language_utils
from ..intelligence.hybrid_brain import HybridBrain
from ..intelligence.intent_recognizer import IntentRecognizer, IntentType

class ChatOverlay(Static):
    """Overlay flotante de chat persistente (bilingüe)."""
    DEFAULT_CSS = """
    ChatOverlay {
        layer: overlay;
        dock: right;
        width: 48;
        height: 60%;
        margin: 1 1 1 0;
        background: #001100;
        border: solid #00aa00;
    }
    ChatOverlay > .chat-title {
        background: #002200;
        color: #00ff00;
        padding: 0 1;
    }
    ChatOverlay RichLog {
        height: 1fr;
        background: #000000;
        border: solid #004400;
        color: #00ff00;
    }
    ChatOverlay Input {
        border: solid #00aa00;
        background: #002200;
        color: #00ff00;
    }
    ChatOverlay Input:focus { border: solid #00ff00; }
    .chat-hidden { display: none; }
    """

    class ChatMessage(Message):
        def __init__(self, user_text: str):
            self.user_text = user_text
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("💬 Chat IA (EN/ES) - F9 toggle", classes="chat-title")
        yield RichLog(id="chat_log", highlight=True, markup=True, wrap=True)
        yield Input(placeholder="Escribe aquí / Type here...", id="chat_input")

    def on_mount(self):
        log = self.query_one("#chat_log", RichLog)
        log.write("[bold green]Chat listo. Bilingüe activado.[/]")
        log.write("[dim]Escribe '/help' para ver comandos disponibles[/]")

    def key_enter(self):
        input_box = self.query_one("#chat_input", Input)
        text = input_box.value.strip()
        if not text:
            return
        self.post_message(self.ChatMessage(text))
        input_box.value = ""

    def key_f9(self):
        # Permitir toggle desde aquí también
        app = self.app
        if hasattr(app, "action_toggle_chat"):
            app.action_toggle_chat()

    def add_response(self, user_text: str, es: str, en: str):
        log = self.query_one("#chat_log", RichLog)
        log.write(f"[cyan][Tú][/]: {user_text}")
        log.write(f"[green][IA-ES][/]: {es}")
        log.write(f"[yellow][IA-EN][/]: {en}")


from .dashboard_widgets import (
    ProfessionalMetricsPanel, IntelligenceControlCenter, AdvancedOperationsPanel,
    RealTimeMonitor, DomainIntelligencePanel, AIAssistantInterface, SystemStatusBar
)
from ..runner import run_crawler
from .. import settings

logger = logging.getLogger(__name__)

class WebScraperProfessionalApp(App):
    """
    Interfaz TUI Profesional para Web Scraper PRO

    Una aplicación de terminal moderna y profesional que representa
    todas las capacidades avanzadas del scraper de manera intuitiva.
    """

    CSS_PATH = "professional_styles.css"
    TITLE = "🕷️ Web Scraper PRO - Professional Dashboard"
    SUB_TITLE = "Sistema Avanzado de Extracción Web con IA Híbrida"

    # Keybindings profesionales
    BINDINGS = [
        # Acciones principales
        Binding("f1", "show_help", "Ayuda", show=True, priority=True),
        Binding("f2", "toggle_dashboard", "Dashboard", show=True),
        Binding("f3", "quick_start", "Quick Start", show=True),
        Binding("f4", "ai_assistant", "Asistente IA", show=True),
        Binding("f9", "toggle_chat", "Chat", show=True),

        # Controles de scraping
        Binding("ctrl+s", "start_scraping", "Iniciar", show=True),
        Binding("ctrl+t", "stop_scraping", "Detener", show=True),
        Binding("ctrl+p", "pause_resume", "Pausar/Reanudar", show=True),

        # Visualización
        Binding("ctrl+l", "toggle_logs", "Logs", show=False),
        Binding("ctrl+m", "toggle_metrics", "Métricas", show=False),
        Binding("ctrl+i", "toggle_intelligence", "Inteligencia", show=False),

        # Sistema
        Binding("ctrl+r", "refresh_data", "Actualizar", show=False),
        Binding("ctrl+q", "quit", "Salir", show=True),
        Binding("escape", "cancel_action", "Cancelar", show=False),
    ]

    # Estados reactivos
    scraping_active = reactive(False)
    current_mode = reactive("dashboard")
    intelligence_enabled = reactive(True)
    total_urls_processed = reactive(0)
    current_speed = reactive(0.0)
    success_rate = reactive(100.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scraper_worker = None
        self.metrics_data = {}
        self.start_time = None
        self.console = Console()
        self._brain: Optional[HybridBrain] = None

    def compose(self) -> ComposeResult:
        """Compone la interfaz principal"""

        # Header personalizado
        yield Header(show_clock=True, name="Web Scraper PRO", id="main_header")

        # Contenido principal con tabs
        with TabbedContent(initial="dashboard-tab", id="main_tabs"):

            # Tab 1: Dashboard Principal
            with TabPane("🏠 Dashboard", id="dashboard-tab"):
                self._create_dashboard_view()

            # Tab 2: Control de Scraping
            with TabPane("🕷️ Scraper Control", id="scraper-tab"):
                self._create_scraper_control_view()

            # Tab 3: Inteligencia IA
            with TabPane("🧠 AI Intelligence", id="intelligence-tab"):
                self._create_intelligence_view()

            # Tab 4: Monitoreo en Tiempo Real
            with TabPane("📊 Real-Time Monitor", id="monitor-tab"):
                self._create_monitoring_view()

            # Tab 5: Exportación y Reportes
            with TabPane("📤 Export & Reports", id="export-tab"):
                self._create_export_view()

            # Tab 6: Configuración Avanzada
            with TabPane("⚙️ Advanced Config", id="config-tab"):
                self._create_config_view()

        # Footer con información del sistema
        yield Footer()

    def _create_dashboard_view(self) -> ComposeResult:
        """Crea la vista del dashboard principal"""
        with Container(id="dashboard-container", classes="dashboard-view"):
            # Grid principal del dashboard
            with Grid(id="dashboard-main-grid", classes="dashboard-grid"):

                # Sección superior: KPIs principales
                with Container(classes="kpis-section"):
                    with Horizontal(classes="kpis-row"):
                        with Container(classes="kpi-card urls-kpi"):
                            yield Label("🎯 URLs Procesadas", classes="kpi-title")
                            yield Digits("0", id="kpi_urls", classes="kpi-number")
                            yield Label("Total acumulado", classes="kpi-subtitle")

                        with Container(classes="kpi-card speed-kpi"):
                            yield Label("⚡ Velocidad", classes="kpi-title")
                            yield Digits("0.0", id="kpi_speed", classes="kpi-number")
                            yield Label("URLs por minuto", classes="kpi-subtitle")

                        with Container(classes="kpi-card success-kpi"):
                            yield Label("✅ Tasa de Éxito", classes="kpi-title")
                            yield Digits("100.0%", id="kpi_success", classes="kpi-number")
                            yield Label("Promedio global", classes="kpi-subtitle")

                        with Container(classes="kpi-card brain-kpi"):
                            yield Label("🧠 IA Score", classes="kpi-title")
                            yield Digits("A+", id="kpi_brain", classes="kpi-number")
                            yield Label("Efectividad IA", classes="kpi-subtitle")

                # Sección media: Gráficos y estado
                with Container(classes="charts-section"):
                    with Horizontal(classes="charts-row"):
                        # Panel de progreso actual
                        with Container(classes="progress-panel"):
                            yield Label("[bold cyan]📈 Progreso Actual[/]", classes="panel-title")
                            yield ProgressBar(total=100, progress=0, id="main_progress",
                                            show_percentage=True, show_eta=True)
                            yield Label("Esperando inicio...", id="progress_status", classes="status-text")

                        # Panel de inteligencia
                        with Container(classes="intelligence-panel"):
                            yield Label("[bold magenta]🧠 Estado de IA[/]", classes="panel-title")
                            yield Label("[green]● HybridBrain ACTIVO[/]", id="brain_status", classes="status-text")
                            yield Label("🔄 Aprendizaje Continuo: ON", classes="status-text")
                            yield Label("🛠️ Auto-Reparación: ON", classes="status-text")

                # Sección inferior: Controles rápidos
                with Container(classes="quick-actions-section"):
                    yield Label("[bold yellow]⚡ Acciones Rápidas[/]", classes="section-title")
                    with Horizontal(classes="quick-buttons-row"):
                        yield Button("🚀 Inicio Rápido", variant="primary", id="quick_start_btn",
                                   classes="quick-action-btn")
                        yield Button("📊 Ver Estadísticas", variant="success", id="view_stats_btn",
                                   classes="quick-action-btn")
                        yield Button("🔧 Auto-Configurar", variant="warning", id="auto_config_btn",
                                   classes="quick-action-btn")
                        yield Button("🧠 Brain Snapshot", variant="default", id="brain_snapshot_btn",
                                   classes="quick-action-btn")

        # No explicit return needed

    def _create_scraper_control_view(self) -> ComposeResult:
        """Crea la vista de control del scraper"""
        with Container(id="scraper-control-container", classes="scraper-view"):
            with Grid(classes="scraper-grid"):

                # Panel de configuración
                with Container(classes="config-panel"):
                    yield Label("[bold green]🕷️ Configuración de Scraping[/]", classes="panel-title")

                    with Vertical(classes="config-form"):
                        yield Label("URL de Inicio:", classes="field-label")
                        yield Input(placeholder="https://books.toscrape.com/",
                                  id="start_url_input", classes="url-input")

                        yield Label("Concurrencia:", classes="field-label")
                        yield Input(value=str(settings.CONCURRENCY),
                                  id="concurrency_input", classes="number-input")

                        with Horizontal(classes="checkboxes-row"):
                            yield Checkbox("Respetar robots.txt", value=True, id="robots_check")
                            yield Checkbox("Verificaciones éticas", value=True, id="ethics_check")
                            yield Checkbox("Modo stealth", value=False, id="stealth_check")

                        with Horizontal(classes="ai-checkboxes-row"):
                            yield Checkbox("Usar IA Híbrida", value=True, id="hybrid_ai_check")
                            yield Checkbox("Agente RL", value=False, id="rl_agent_check")
                            yield Checkbox("LLM Enhancement", value=True, id="llm_check")

                # Panel de controles
                with Container(classes="controls-panel"):
                    yield Label("[bold blue]🎮 Controles[/]", classes="panel-title")

                    with Vertical(classes="control-buttons"):
                        yield Button("🚀 INICIAR SCRAPING", variant="primary",
                                   id="start_scraping_btn", classes="control-btn")
                        yield Button("⏸️ PAUSAR", variant="warning",
                                   id="pause_scraping_btn", classes="control-btn", disabled=True)
                        yield Button("⏹️ DETENER", variant="error",
                                   id="stop_scraping_btn", classes="control-btn", disabled=True)
                        yield Button("🔄 REINICIAR", variant="default",
                                   id="restart_scraping_btn", classes="control-btn")

                # Panel de estado en tiempo real
                with Container(classes="status-panel"):
                    yield Label("[bold cyan]📡 Estado en Tiempo Real[/]", classes="panel-title")
                    yield RichLog(highlight=True, markup=True, id="realtime_log",
                                classes="realtime-log")

    # No explicit return needed

    def _create_intelligence_view(self) -> ComposeResult:
        """Crea la vista de inteligencia IA"""
        with Container(id="intelligence-container", classes="intelligence-view"):
            with Grid(classes="intelligence-grid"):

                # Panel de control de IA
                with Container(classes="ai-control-panel"):
                    yield Label("[bold magenta]🧠 Control de Inteligencia Artificial[/]", classes="panel-title")

                    with Vertical(classes="ai-controls"):
                        yield Label("Modo de Operación:", classes="field-label")
                        with RadioSet(id="ai_mode_radio"):
                            yield RadioButton("HybridBrain (IA-A + IA-B)", value=True, id="hybrid_mode")
                            yield RadioButton("Neural Brain Only", id="neural_mode")
                            yield RadioButton("Legacy Mode", id="legacy_mode")

                        with Horizontal(classes="ai-toggles"):
                            yield Switch(value=True, id="consciousness_switch", classes="ai-switch")
                            yield Label("Procesamiento Consciente", classes="switch-label")

                        with Horizontal(classes="ai-toggles"):
                            yield Switch(value=True, id="learning_switch", classes="ai-switch")
                            yield Label("Aprendizaje Continuo", classes="switch-label")

                        with Horizontal(classes="ai-toggles"):
                            yield Switch(value=True, id="repair_switch", classes="ai-switch")
                            yield Label("Auto-Reparación", classes="switch-label")

                # Panel de métricas de IA
                with Container(classes="ai-metrics-panel"):
                    yield Label("[bold yellow]📊 Métricas de Inteligencia[/]", classes="panel-title")

                    with Vertical(classes="ai-metrics"):
                        yield Label("Sesiones de Aprendizaje: 0", id="learning_sessions", classes="metric-item")
                        yield Label("Patrones Detectados: 0", id="patterns_detected", classes="metric-item")
                        yield Label("Efectividad IA: 0%", id="ai_effectiveness", classes="metric-item")
                        yield Label("Sugerencias Generadas: 0", id="suggestions_generated", classes="metric-item")

                # Panel de acciones de IA
                with Container(classes="ai-actions-panel"):
                    yield Label("[bold purple]🤖 Acciones de IA[/]", classes="panel-title")

                    with Vertical(classes="ai-action-buttons"):
                        yield Button("🔍 Análisis Inteligente", variant="primary",
                                   id="ai_analyze_btn", classes="ai-action-btn")
                        yield Button("🛠️ Ejecutar Auto-Reparación", variant="success",
                                   id="ai_repair_btn", classes="ai-action-btn")
                        yield Button("📸 Brain Snapshot", variant="warning",
                                   id="brain_snapshot_action_btn", classes="ai-action-btn")
                        yield Button("📚 Consultar Knowledge Base", variant="default",
                                   id="query_kb_btn", classes="ai-action-btn")

    # No explicit return needed

    def _create_monitoring_view(self) -> ComposeResult:
        """Crea la vista de monitoreo en tiempo real"""
        with Container(id="monitoring-container", classes="monitoring-view"):
            with Grid(classes="monitoring-grid"):

                # Panel de estadísticas por dominio
                with Container(classes="domain-stats-panel"):
                    yield Label("[bold blue]🌐 Estadísticas por Dominio[/]", classes="panel-title")
                    yield DataTable(id="domain_stats_table", classes="domain-table")

                # Panel de alertas
                with Container(classes="alerts-panel"):
                    yield Label("[bold red]⚠️ Alertas del Sistema[/]", classes="panel-title")
                    yield ListView(id="alerts_list", classes="alerts-list")

                # Panel de rendimiento
                with Container(classes="performance-panel"):
                    yield Label("[bold green]📈 Rendimiento del Sistema[/]", classes="panel-title")
                    with Vertical(classes="performance-metrics"):
                        yield Label("CPU: 0%", id="cpu_usage", classes="perf-metric")
                        yield Label("Memoria: 0 MB", id="memory_usage", classes="perf-metric")
                        yield Label("Red: 0 KB/s", id="network_usage", classes="perf-metric")
                        yield Label("Disco: 0 MB", id="disk_usage", classes="perf-metric")

    # No explicit return needed

    def _create_export_view(self) -> ComposeResult:
        """Crea la vista de exportación y reportes"""
        with Container(id="export-container", classes="export-view"):
            with Grid(classes="export-grid"):

                # Panel de formatos de exportación
                with Container(classes="export-formats-panel"):
                    yield Label("[bold cyan]📤 Formatos de Exportación[/]", classes="panel-title")

                    with Vertical(classes="format-checkboxes"):
                        yield Checkbox("CSV (Comma Separated Values)", value=True, id="csv_export")
                        yield Checkbox("JSON (JavaScript Object Notation)", value=True, id="json_export")
                        yield Checkbox("Markdown (.md)", value=False, id="md_export")
                        yield Checkbox("Excel (.xlsx)", value=False, id="xlsx_export")
                        yield Checkbox("Word (.docx)", value=False, id="docx_export")

                # Panel de opciones de reporte
                with Container(classes="report-options-panel"):
                    yield Label("[bold yellow]📋 Opciones de Reporte[/]", classes="panel-title")

                    with Vertical(classes="report-checkboxes"):
                        yield Checkbox("Incluir métricas de rendimiento", value=True, id="perf_metrics")
                        yield Checkbox("Incluir análisis de IA", value=True, id="ai_analysis")
                        yield Checkbox("Incluir estadísticas por dominio", value=True, id="domain_stats")
                        yield Checkbox("Incluir logs detallados", value=False, id="detailed_logs")

                # Panel de acciones de exportación
                with Container(classes="export-actions-panel"):
                    yield Label("[bold green]🚀 Acciones[/]", classes="panel-title")

                    with Vertical(classes="export-buttons"):
                        yield Button("📊 Generar Reporte Completo", variant="primary",
                                   id="generate_report_btn", classes="export-btn")
                        yield Button("💾 Exportar Datos Actuales", variant="success",
                                   id="export_current_btn", classes="export-btn")
                        yield Button("📈 Reporte de IA", variant="warning",
                                   id="ai_report_btn", classes="export-btn")
                        yield Button("🗂️ Abrir Carpeta de Exportación", variant="default",
                                   id="open_exports_btn", classes="export-btn")

    # No explicit return needed

    def _create_config_view(self) -> ComposeResult:
        """Crea la vista de configuración avanzada"""
        with Container(id="config-container", classes="config-view"):
            with Grid(classes="config-grid"):

                # Panel de configuración del sistema
                with Container(classes="system-config-panel"):
                    yield Label("[bold red]⚙️ Configuración del Sistema[/]", classes="panel-title")

                    with Vertical(classes="system-settings"):
                        yield Label("Workers Concurrentes:", classes="field-label")
                        yield Input(value="8", id="workers_config", classes="number-input")

                        yield Label("Timeout (segundos):", classes="field-label")
                        yield Input(value="30", id="timeout_config", classes="number-input")

                        yield Label("Max Retries:", classes="field-label")
                        yield Input(value="3", id="retries_config", classes="number-input")

                # Panel de configuración de IA
                with Container(classes="ai-config-panel"):
                    yield Label("[bold purple]🧠 Configuración de IA[/]", classes="panel-title")

                    with Vertical(classes="ai-settings"):
                        yield Label("Frecuencia de Sync IA:", classes="field-label")
                        yield Input(value="50", id="ia_sync_config", classes="number-input")

                        yield Label("Umbral de Confianza:", classes="field-label")
                        yield Input(value="0.8", id="confidence_config", classes="number-input")

                        yield Checkbox("Modo Debug IA", value=False, id="ai_debug")
                        yield Checkbox("Logging Detallado", value=False, id="verbose_logging")

                # Panel de acciones de configuración
                with Container(classes="config-actions-panel"):
                    yield Label("[bold green]💾 Acciones[/]", classes="panel-title")

                    with Vertical(classes="config-buttons"):
                        yield Button("💾 Guardar Configuración", variant="primary",
                                   id="save_config_btn", classes="config-btn")
                        yield Button("🔄 Restaurar Defaults", variant="warning",
                                   id="restore_defaults_btn", classes="config-btn")
                        yield Button("📋 Exportar Config", variant="default",
                                   id="export_config_btn", classes="config-btn")

    # No explicit return needed

    async def on_mount(self) -> None:
        """Se ejecuta cuando la app se monta"""
        self.sub(SystemStatusBar.SystemUpdate, self.on_system_update)

        # Inicializar tablas
        await self._initialize_domain_table()

        # Configurar actualizaciones periódicas
        self.set_interval(1.0, self._update_time_display)
        self.set_interval(5.0, self._update_system_metrics)

        # Añadir overlay chat (persistente)
        try:
            if not self.query("ChatOverlay"):
                overlay = ChatOverlay(id="chat_overlay")
                await self.mount(overlay)
                self._chat_visible = True

                # Inicio de inicialización temprana del cerebro
                log = overlay.query_one("#chat_log", RichLog)
                log.write("[bold green]💬 Chat listo. Bilingüe activado.[/]")
                log.write("[dim]Inicializando HybridBrain... (esto puede tardar unos segundos)[/]")

                # Iniciar el cerebro en segundo plano para no bloquear la UI
                async def init_brain_background():
                    try:
                        await self._ensure_brain_initialized(log)
                    except Exception as e:
                        logger.error(f"Error en inicialización background: {e}")

                # Programar la inicialización para después de que la UI esté lista
                self.call_later(init_brain_background)
        except Exception as e:
            logger.error(f"No se pudo montar ChatOverlay: {e}")

    async def handle_chat_overlay_chat_message(self, message: ChatOverlay.ChatMessage):  # type: ignore
        """Procesa mensajes del chat."""
        user_text = message.user_text
        try:
            overlay: ChatOverlay = self.query_one("ChatOverlay")  # type: ignore
            log = overlay.query_one("#chat_log", RichLog)

            # Comandos (prefijo /)
            if user_text.startswith('/'):
                await self._process_chat_command(user_text[1:], overlay, log)
                return

            # Inicializar cerebro si es necesario
            await self._ensure_brain_initialized(log)

            # Reconocer intención del mensaje
            intent = IntentRecognizer.recognize(user_text)
            intent_prefix_es = ""
            intent_prefix_en = ""

            # Si la intención es reconocida con confianza, procesarla
            if intent.confidence > 0.6 and intent.type != IntentType.UNKNOWN:
                # Preparar mensaje sobre la intención detectada
                if intent.type == IntentType.SEARCH:
                    query = intent.parameters.get("query", "")
                    intent_prefix_es = f"[bold blue]Detectada intención:[/] búsqueda de \"{query}\"\n\n"
                    intent_prefix_en = f"[bold blue]Intent detected:[/] search for \"{query}\"\n\n"
                    # Simular comando /kb
                    if query:
                        await self._process_chat_command(f"kb {query}", overlay, log, show_cmd=False)

                elif intent.type == IntentType.CRAWL:
                    url = intent.parameters.get("url", "")
                    intent_prefix_es = f"[bold green]Detectada intención:[/] iniciar scraping\n\n"
                    intent_prefix_en = f"[bold green]Intent detected:[/] start crawling\n\n"
                    # Simular comando /crawl
                    if url:
                        await self._process_chat_command(f"crawl {url}", overlay, log, show_cmd=False)

                elif intent.type == IntentType.KNOWLEDGE:
                    topic = intent.parameters.get("topic", "")
                    intent_prefix_es = f"[bold yellow]Detectada intención:[/] consulta sobre \"{topic}\"\n\n"
                    intent_prefix_en = f"[bold yellow]Intent detected:[/] query about \"{topic}\"\n\n"
                    # Simular comando /kb
                    if topic:
                        await self._process_chat_command(f"kb {topic}", overlay, log, show_cmd=False)

                elif intent.type == IntentType.SNAPSHOT:
                    intent_prefix_es = f"[bold purple]Detectada intención:[/] generar snapshot\n\n"
                    intent_prefix_en = f"[bold purple]Intent detected:[/] generate snapshot\n\n"
                    # Simular comando /snapshot
                    await self._process_chat_command("snapshot", overlay, log, show_cmd=False)

                elif intent.type == IntentType.STATUS:
                    intent_prefix_es = f"[bold cyan]Detectada intención:[/] consulta de estado\n\n"
                    intent_prefix_en = f"[bold cyan]Intent detected:[/] status query\n\n"
                    # Simular comando /status
                    await self._process_chat_command("status", overlay, log, show_cmd=False)

                elif intent.type == IntentType.EDIT:
                    file = intent.parameters.get("file", "")
                    old_content = intent.parameters.get("old_content", "")
                    new_content = intent.parameters.get("new_content", "")

                    intent_prefix_es = f"[bold orange]Detectada intención:[/] editar archivo"
                    intent_prefix_en = f"[bold orange]Intent detected:[/] edit file"

                    if file:
                        intent_prefix_es += f" '{file}'"
                        intent_prefix_en += f" '{file}'"

                    intent_prefix_es += "\n\n"
                    intent_prefix_en += "\n\n"

                    # Implementamos el comando edit
                    await self._process_edit_intent(file, old_content, new_content, log)

                elif intent.type == IntentType.TERMINAL:
                    command = intent.parameters.get("command", "")

                    intent_prefix_es = f"[bold magenta]Detectada intención:[/] ejecutar comando en terminal"
                    intent_prefix_en = f"[bold magenta]Intent detected:[/] execute terminal command"

                    if command:
                        intent_prefix_es += f" '{command}'"
                        intent_prefix_en += f" '{command}'"

                    intent_prefix_es += "\n\n"
                    intent_prefix_en += "\n\n"

                    # Implementamos el comando de terminal
                    await self._process_terminal_intent(command, log)

            # Preprocesar texto y enriquecer
            lang, enriched_es, enriched_en = language_utils.enrich_text_bilingual(user_text)

            # Añadir prefijo de intención a las respuestas
            enriched_es = intent_prefix_es + enriched_es
            enriched_en = intent_prefix_en + enriched_en

            # Consultar la KB
            kb_summary_es = kb_summary_en = ""
            numbered_lines_es: List[str] = []
            numbered_lines_en: List[str] = []

            # Intentar obtener respuesta del cerebro
            if self._brain:
                try:
                    # Primero intentamos consulta al cerebro para respuesta semántica
                    brain_response = None
                    if hasattr(self._brain, 'get_response') and callable(getattr(self._brain, 'get_response')):
                        try:
                            brain_response = self._brain.get_response(user_text)
                            if brain_response:
                                # Si el cerebro tiene una respuesta directa, la usamos
                                enriched_es = brain_response.get('es', enriched_es)
                                enriched_en = brain_response.get('en', enriched_en)
                        except Exception:
                            # Si falla, seguimos con el flujo normal
                            pass

                    # Consulta a la base de conocimiento
                    kb_results = self._brain.query_knowledge_base(user_text)
                    if kb_results:
                        for idx, r in enumerate(kb_results[:5], start=1):
                            title = r.get('title') or r.get('id','') or 'sin_titulo'
                            content = r.get('content', '')[:50] + '...' if r.get('content') else ''
                            numbered_lines_es.append(f"[bold]{idx}.[/] {title}")
                            numbered_lines_en.append(f"[bold]{idx}.[/] {title}")
                        kb_summary_es = "\n\n[bold green]Coincidencias en KB:[/]\n" + "\n".join(numbered_lines_es)
                        kb_summary_en = "\n\n[bold yellow]KB Matches:[/]\n" + "\n".join(numbered_lines_en)
                    else:
                        kb_summary_es = "\n\n[dim]Sin resultados relevantes en la base de conocimiento[/]"
                        kb_summary_en = "\n\n[dim]No relevant results in knowledge base[/]"
                except Exception as kb_e:
                    kb_summary_es = f"\n\n[red]Error consultando KB: {kb_e}[/]"
                    kb_summary_en = f"\n\n[red]Error querying KB: {kb_e}[/]"
            else:
                kb_summary_es = "\n\n[red]Cerebro no inicializado[/]"
                kb_summary_en = "\n\n[red]Brain not initialized[/]"

            response_es = f"{enriched_es}{kb_summary_es}"
            response_en = f"{enriched_en}{kb_summary_en}"
            overlay.add_response(user_text, response_es, response_en)
        except Exception as e:
            try:
                self.query_one("#chat_log", RichLog).write(f"[red]Error IA: {e}[/]")
            except Exception:
                logger.error(f"Chat error: {e}")

    def action_toggle_chat(self) -> None:
        """Muestra/oculta el overlay de chat sin destruirlo."""
        try:
            overlay = self.query_one("ChatOverlay")
            if "chat-hidden" in overlay.classes:
                overlay.remove_class("chat-hidden")
            else:
                overlay.add_class("chat-hidden")
        except Exception as e:
            logger.error(f"toggle_chat error: {e}")

    async def _ensure_brain_initialized(self, log: Optional[RichLog] = None):
        """Inicializa el cerebro de manera asíncrona si no está ya inicializado."""
        if self._brain is not None:
            return

        if log:
            log.write("[dim]Inicializando HybridBrain... (esto puede tomar un momento)[/]")

        try:
            # Inicializar en segundo plano
            async def init_brain():
                try:
                    return HybridBrain()
                except Exception as e:
                    logger.error(f"Error en inicialización cerebro: {e}")
                    return None

            # Ejecutar inicialización en worker
            worker = self.run_worker(init_brain(), name="BrainInitWorker")
            self._brain = await worker.wait()

            if log:
                if self._brain:
                    log.write("[bold green]🧠 HybridBrain listo y conectado.[/]")
                else:
                    log.write("[red]⚠️ HybridBrain no pudo inicializarse.[/]")

        except Exception as e:
            if log:
                log.write(f"[red]⛔ Error inicializando HybridBrain: {e}[/]")
            logger.error(f"Error inicializando HybridBrain: {e}")
            self._brain = None

    async def _process_chat_command(self, command_text: str, overlay: ChatOverlay, log: RichLog, show_cmd: bool = True):
        """Procesa comandos del chat con diversos prefijos '/'."""
        parts = command_text.strip().split(maxsplit=1)
        cmd = parts[0].lower()

        # Si show_cmd es True, mostrar el comando en el chat
        if show_cmd:
            log.write(f"[bold magenta]/{cmd}[/] {parts[1] if len(parts) > 1 else ''}")
        arg = parts[1].strip() if len(parts) > 1 else ""

        # Comandos de ayuda
        if cmd in ("help", "ayuda", "?"):
            commands = [
                "[bold yellow]== COMANDOS DISPONIBLES ==[/]",
                "[cyan]/crawl URL[/] - Inicia scraping en URL indicada",
                "[cyan]/kb CONSULTA[/] - Busca en la base de conocimiento",
                "[cyan]/snapshot[/] - Genera snapshot del cerebro",
                "[cyan]/stop[/] - Detiene el scraping activo",
                "[cyan]/status[/] - Muestra estado actual del scraping",
                "[cyan]/edit ARCHIVO CONTENIDO[/] - Edita o muestra un archivo",
                "[cyan]/terminal COMANDO[/] - Ejecuta comando en terminal",
                "[cyan]/buscar TEXTO[/] - Busca en archivos del sistema",
                "[cyan]/crear TAREA[/] - Crea nueva tarea de scraping",
                "[cyan]/brain[/] - Estado del cerebro y métricas",
                "[cyan]/config[/] - Muestra/modifica configuración",
                "[cyan]/clear[/] - Limpia el chat",
                "[cyan]/help[/] - Muestra esta ayuda"
            ]
            log.write("\n".join(commands))
            return

        # Comandos de scraping
        if cmd in ("crawl", "scrapear", "extraer"):
            if not arg:
                log.write("[red]⛔ Uso: /crawl URL[/]")
                return
            self.query_one("#start_url_input", Input).value = arg
            self.action_start_scraping()
            log.write(f"[bold green]🚀 Iniciando scraping en: {arg}[/]")
            return

        if cmd in ("stop", "parar", "detener"):
            self.action_stop_scraping()
            log.write("[bold red]⏹️ Scraping detenido por comando de usuario[/]")
            return

        if cmd in ("status", "estado"):
            active = "[bold green]ACTIVO[/]" if self.scraping_active else "[red]INACTIVO[/]"
            log.write(f"[cyan]📊 Estado scraping: {active}")
            log.write(f"[cyan]📈 URLs procesadas: {self.total_urls_processed}")
            if self.scraping_active and hasattr(self, 'start_time'):
                elapsed = datetime.now() - self.start_time if self.start_time else None
                if elapsed:
                    log.write(f"[cyan]⏱️ Tiempo activo: {elapsed.total_seconds():.0f} segundos")
            return

        # Comandos de conocimiento
        if cmd in ("kb", "conocimiento", "buscar"):
            if not arg:
                log.write("[red]⛔ Uso: /kb CONSULTA[/]")
                return
            await self._ensure_brain_initialized(log)
            if self._brain:
                try:
                    log.write(f"[dim]Buscando '{arg}' en base de conocimiento...[/]")
                    results = self._brain.query_knowledge_base(arg) or []
                    if results:
                        lines = ["[bold magenta]📚 Resultados encontrados:[/]"]
                        for i, r in enumerate(results[:8], 1):
                            title = r.get('title') or r.get('id','') or 'sin_titulo'
                            content_preview = r.get('content', '')[:50] + '...' if r.get('content') else ''
                            lines.append(f"[bold cyan]{i}.[/] {title}")
                            if content_preview:
                                lines.append(f"   [dim]{content_preview}[/]")
                        log.write("\n".join(lines))
                    else:
                        log.write("[yellow]⚠️ Sin resultados en base de conocimiento[/]")
                except Exception as ke:
                    log.write(f"[red]⛔ Error consultando KB: {ke}[/]")
            else:
                log.write("[red]⛔ Cerebro no inicializado. Intenta más tarde.[/]")
            return

        if cmd in ("snapshot", "cerebro"):
            await self._ensure_brain_initialized(log)
            if self._brain:
                try:
                    log.write("[dim]Generando snapshot del cerebro...[/]")
                    snapshot = self._brain.get_snapshot() if hasattr(self._brain, 'get_snapshot') else {}
                    summary = snapshot.get('meta', {}).get('summary', 'Snapshot listo')
                    stats = snapshot.get('stats', {})

                    lines = ["[bold green]🧠 BRAIN SNAPSHOT[/]"]
                    lines.append(f"[cyan]📝 Resumen: {summary}[/]")

                    if stats:
                        lines.append("[yellow]📊 Estadísticas:[/]")
                        for key, value in stats.items():
                            if isinstance(value, (int, float, str)):
                                lines.append(f"  • {key}: {value}")

                    log.write("\n".join(lines))
                except Exception as se:
                    log.write(f"[red]⛔ Error generando snapshot: {se}[/]")
            else:
                log.write("[red]⛔ Cerebro no inicializado. Intenta más tarde.[/]")
            return

        # Comandos de edición
        if cmd in ("edit", "editar"):
            parts = arg.split(' ', 1)
            if not parts:
                log.write("[red]⛔ Uso: /edit <archivo> <contenido>[/]")
                return

            file = parts[0] if parts else ""
            content = parts[1] if len(parts) > 1 else ""
            await self._process_edit_intent(file, "", content, log)
            return

        # Comandos de terminal
        if cmd in ("terminal", "cmd", "powershell", "ps", "shell"):
            if not arg:
                log.write("[red]⛔ Uso: /terminal <comando>[/]")
                return

            await self._process_terminal_intent(arg, log)
            return

        # Comandos de utilidad
        if cmd in ("clear", "limpiar", "cls"):
            log.clear()
            log.write("[green]Chat limpiado.[/]")
            return

        if cmd in ("crear", "create", "nueva"):
            log.write(f"[yellow]⚠️ Creación de tareas '{arg}' será implementada próximamente[/]")
            return

        if cmd == "config":
            # Mostrar configuración actual
            config_lines = [
                "[bold cyan]⚙️ CONFIGURACIÓN ACTUAL[/]",
                f"• Cerebro: {'[green]Activo[/]' if self._brain else '[red]Inactivo[/]'}",
                f"• Scraping: {'[green]Activo[/]' if self.scraping_active else '[red]Inactivo[/]'}",
                f"• Mode: {getattr(self, 'current_mode', 'dashboard')}"
            ]
            log.write("\n".join(config_lines))
            return

        if cmd == "brain":
            # Estado del cerebro
            brain_status = "INICIALIZADO" if self._brain else "NO INICIALIZADO"
            brain_lines = [
                "[bold magenta]🧠 ESTADO DEL CEREBRO[/]",
                f"Estado: {brain_status}"
            ]

            if self._brain:
                # Intentar obtener métricas del cerebro si están disponibles
                try:
                    if hasattr(self._brain, "get_metrics"):
                        metrics = self._brain.get_metrics() or {}
                        for key, value in metrics.items():
                            brain_lines.append(f"• {key}: {value}")
                except Exception as be:
                    brain_lines.append(f"[red]Error obteniendo métricas: {be}[/]")

            log.write("\n".join(brain_lines))
            return

        # Comando no reconocido
        log.write(f"[red]⛔ Comando no reconocido: /{cmd}[/]")
        log.write("[dim]Escribe /help para ver comandos disponibles[/]")

    async def _initialize_domain_table(self):
        """Inicializa la tabla de estadísticas por dominio"""
        try:
            table = self.query_one("#domain_stats_table", DataTable)
            table.add_columns("Dominio", "URLs", "Éxito %", "Velocidad", "IA Score")

            # Datos de ejemplo
            table.add_rows([
                ("books.toscrape.com", "0", "0%", "0/min", "-"),
                ("quotes.toscrape.com", "0", "0%", "0/min", "-"),
                ("Pending...", "0", "0%", "0/min", "-")
            ])
        except Exception as e:
            logger.error(f"Error initializing domain table: {e}")

    def _update_time_display(self):
        """Actualiza la visualización del tiempo"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            # Actualizar header si es necesario
        except Exception as e:
            logger.error(f"Error updating time: {e}")

    def _update_system_metrics(self):
        """Actualiza las métricas del sistema"""
        try:
            try:
                import psutil  # type: ignore
            except Exception:
                return

            # Actualizar métricas de sistema
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            # Actualizar UI (si los elementos existen)
            try:
                self.query_one("#cpu_usage", Label).update(f"CPU: {cpu_percent:.1f}%")
                self.query_one("#memory_usage", Label).update(f"Memoria: {memory.used // (1024*1024)} MB")
            except:
                pass  # Elementos no existen aún

        except ImportError:
            # psutil no disponible
            pass
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")

    def on_system_update(self, message):
        """Maneja actualizaciones del sistema"""
        pass

    # Acciones de teclado
    def action_show_help(self) -> None:
        """Muestra la ayuda"""
        self.push_screen("help")

    def action_quick_start(self) -> None:
        """Inicio rápido"""
        # Cambiar a tab de scraper y configurar valores por defecto
        self.query_one("#main_tabs", TabbedContent).active = "scraper-tab"
        self.query_one("#start_url_input", Input).value = "https://books.toscrape.com/"

    def action_start_scraping(self) -> None:
        """Inicia el scraping"""
        if not self.scraping_active:
            self._start_scraping_process()

    def action_stop_scraping(self) -> None:
        """Detiene el scraping"""
        if self.scraping_active:
            self._stop_scraping_process()

    def _start_scraping_process(self):
        """Proceso interno para iniciar scraping"""
        try:
            # Obtener configuración
            start_url = self.query_one("#start_url_input", Input).value
            if not start_url:
                start_url = "https://books.toscrape.com/"

            concurrency = int(self.query_one("#concurrency_input", Input).value or "8")

            # Actualizar estado
            self.scraping_active = True
            self.start_time = datetime.now()

            # Actualizar UI
            self.query_one("#start_scraping_btn", Button).disabled = True
            self.query_one("#pause_scraping_btn", Button).disabled = False
            self.query_one("#stop_scraping_btn", Button).disabled = False

            # Log de inicio
            log = self.query_one("#realtime_log", RichLog)
            log.write(f"[green]🚀 Iniciando scraping desde: {start_url}[/]")
            log.write(f"[cyan]⚙️ Configuración: {concurrency} workers[/]")

            # Iniciar worker
            self.scraper_worker = self.run_worker(
                self._scraping_worker(start_url, concurrency),
                name="ScrapingWorker"
            )

        except Exception as e:
            logger.error(f"Error starting scraping: {e}")
            self._stop_scraping_process()

    def _stop_scraping_process(self):
        """Proceso interno para detener scraping"""
        try:
            if self.scraper_worker:
                self.scraper_worker.cancel()

            # Actualizar estado
            self.scraping_active = False

            # Actualizar UI
            self.query_one("#start_scraping_btn", Button).disabled = False
            self.query_one("#pause_scraping_btn", Button).disabled = True
            self.query_one("#stop_scraping_btn", Button).disabled = True
        except Exception as e:
            self.log_error(f"Error al detener scraping: {e}")

    async def _scraping_worker(self, start_url: str, concurrency: int):
        """Worker para el proceso de scraping"""
        try:
            # Simular scraping por ahora
            for i in range(100):
                if not self.scraping_active:
                    break

                await asyncio.sleep(0.1)

                # Actualizar métricas
                self.total_urls_processed = i + 1
                self.current_speed = (i + 1) / max((datetime.now() - self.start_time).total_seconds() / 60, 0.1)

                # Actualizar UI
                self.query_one("#kpi_urls", Digits).update(str(self.total_urls_processed))
                self.query_one("#kpi_speed", Digits).update(f"{self.current_speed:.1f}")
                self.query_one("#main_progress", ProgressBar).update(progress=i + 1)

                # Log progreso
                if i % 10 == 0:
                    log = self.query_one("#realtime_log", RichLog)
                    log.write(f"[cyan]📊 Procesadas {i + 1} URLs - Velocidad: {self.current_speed:.1f}/min[/]")

            # Completado
            log = self.query_one("#realtime_log", RichLog)
            log.write("[green]✅ Scraping completado exitosamente[/]")

        except Exception as e:
            logger.error(f"Error in scraping worker: {e}")
            log = self.query_one("#realtime_log", RichLog)
            log.write(f"[red]❌ Error en scraping: {e}[/]")
        finally:
            self._stop_scraping_process()


async def run_professional_app():
    """Ejecuta la aplicación profesional"""
    app = WebScraperProfessionalApp()
    await app.run_async()
