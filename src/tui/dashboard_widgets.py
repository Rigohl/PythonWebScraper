# src/tui/dashboard_widgets.py

from datetime import datetime
from typing import Any, Dict

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Digits,
    Label,
    ListView,
    ProgressBar,
    RadioButton,
    RadioSet,
    RichLog,
    Sparkline,
    Static,
    Switch,
    TabbedContent,
    TabPane,
)


class ProfessionalMetricsPanel(Static):
    """Panel de métricas profesional con indicadores avanzados"""

    def __init__(self, title: str = "Métricas del Sistema", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.metrics_data = {}

    def compose(self) -> ComposeResult:
        with Container(classes="metrics-panel"):
            yield Label(f"[bold cyan]📊 {self.title}[/]", classes="panel-title")
            with Grid(classes="metrics-grid"):
                # KPIs principales
                with Container(classes="kpi-container"):
                    yield Label("[dim]🎯 URLs Procesadas[/]", classes="kpi-label")
                    yield Digits("0", id="urls_processed", classes="kpi-value")

                with Container(classes="kpi-container"):
                    yield Label("[dim]⚡ Velocidad (URLs/min)[/]", classes="kpi-label")
                    yield Digits("0.0", id="processing_speed", classes="kpi-value")

                with Container(classes="kpi-container"):
                    yield Label("[dim]🎯 Tasa de Éxito[/]", classes="kpi-label")
                    yield Digits("0%", id="success_rate", classes="kpi-value")

                with Container(classes="kpi-container"):
                    yield Label("[dim]💾 Datos Extraídos (KB)[/]", classes="kpi-label")
                    yield Digits("0", id="data_extracted", classes="kpi-value")

    def update_metrics(self, data: Dict[str, Any]):
        """Actualiza las métricas mostradas"""
        self.metrics_data.update(data)

        # Actualizar KPIs
        if "urls_processed" in data:
            self.query_one("#urls_processed", Digits).update(
                str(data["urls_processed"])
            )
        if "processing_speed" in data:
            self.query_one("#processing_speed", Digits).update(
                f"{data['processing_speed']:.1f}"
            )
        if "success_rate" in data:
            self.query_one("#success_rate", Digits).update(
                f"{data['success_rate']:.1f}%"
            )
        if "data_extracted" in data:
            self.query_one("#data_extracted", Digits).update(
                str(data["data_extracted"])
            )


class IntelligenceControlCenter(Static):
    """Centro de control de inteligencia con monitoreo avanzado"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brain_active = reactive(False)
        self.ai_mode = reactive("hybrid")

    def compose(self) -> ComposeResult:
        with Container(classes="intelligence-center"):
            yield Label(
                "[bold magenta]🧠 Centro de Inteligencia Artificial[/]",
                classes="panel-title",
            )

            with Grid(classes="intelligence-grid"):
                # Estado del cerebro
                with Container(classes="brain-status-container"):
                    yield Label(
                        "[dim]Estado del HybridBrain[/]", classes="status-label"
                    )
                    yield Switch(value=True, id="brain_toggle", classes="brain-switch")
                    yield Label(
                        "[green]● ACTIVO[/]",
                        id="brain_status",
                        classes="status-indicator",
                    )

                # Modo de IA
                with Container(classes="ai-mode-container"):
                    yield Label("[dim]Modo de Inteligencia[/]", classes="mode-label")
                    with RadioSet(id="ai_mode_selector", classes="mode-selector"):
                        yield RadioButton(
                            "Hybrid (IA-A + IA-B)", value=True, id="mode_hybrid"
                        )
                        yield RadioButton("Neural Only", id="mode_neural")
                        yield RadioButton("Legacy", id="mode_legacy")

                # Métricas de IA
                with Container(classes="ai-metrics-container"):
                    yield Label(
                        "[dim]Aprendizaje Autónomo[/]", classes="learning-label"
                    )
                    yield ProgressBar(
                        total=100,
                        progress=75,
                        id="learning_progress",
                        show_eta=False,
                        show_percentage=True,
                    )
                    yield Label(
                        "[dim]Sesiones: 127 | Patrones: 45 | Efectividad: 94.2%[/]",
                        id="learning_stats",
                        classes="learning-details",
                    )


class AdvancedOperationsPanel(Static):
    """Panel de operaciones avanzadas"""

    def compose(self) -> ComposeResult:
        with Container(classes="operations-panel"):
            yield Label(
                "[bold yellow]⚙️ Operaciones Avanzadas[/]", classes="panel-title"
            )

            with TabbedContent(initial="scraping-tab", classes="ops-tabs"):
                with TabPane("🕷️ Scraping", id="scraping-tab"):
                    with Vertical(classes="scraping-controls"):
                        yield Label(
                            "[dim]Configuración de Scraping[/]", classes="section-label"
                        )
                        yield Checkbox(
                            "Respeto robots.txt", value=True, id="robots_check"
                        )
                        yield Checkbox(
                            "Verificaciones éticas", value=True, id="ethics_check"
                        )
                        yield Checkbox("Modo stealth", value=False, id="stealth_check")
                        yield Checkbox("Auto-healing", value=True, id="healing_check")

                with TabPane("🤖 IA/ML", id="ai-tab"):
                    with Vertical(classes="ai-controls"):
                        yield Label(
                            "[dim]Configuración de IA[/]", classes="section-label"
                        )
                        yield Checkbox("LLM Enhancement", value=True, id="llm_check")
                        yield Checkbox("RL Agent", value=False, id="rl_check")
                        yield Checkbox(
                            "Continuous Learning", value=True, id="learning_check"
                        )
                        yield Checkbox("Self-Repair", value=True, id="repair_check")

                with TabPane("📊 Exportación", id="export-tab"):
                    with Vertical(classes="export-controls"):
                        yield Label(
                            "[dim]Formatos de Exportación[/]", classes="section-label"
                        )
                        yield Checkbox("CSV", value=True, id="csv_check")
                        yield Checkbox("JSON", value=True, id="json_check")
                        yield Checkbox("Markdown", value=False, id="md_check")
                        yield Checkbox("Excel (.xlsx)", value=False, id="xlsx_check")
                        yield Checkbox("Word (.docx)", value=False, id="docx_check")


class RealTimeMonitor(Static):
    """Monitor en tiempo real con logs y alertas"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_entries = []

    def compose(self) -> ComposeResult:
        with Container(classes="monitor-panel"):
            yield Label(
                "[bold green]📡 Monitor en Tiempo Real[/]", classes="panel-title"
            )

            with TabbedContent(initial="activity-tab", classes="monitor-tabs"):
                with TabPane("🔄 Actividad", id="activity-tab"):
                    yield RichLog(
                        highlight=True,
                        markup=True,
                        id="activity_log",
                        classes="activity-log",
                    )

                with TabPane("⚠️ Alertas", id="alerts-tab"):
                    yield ListView(id="alerts_list", classes="alerts-list")

                with TabPane("📈 Gráficos", id="charts-tab"):
                    with Vertical(classes="charts-container"):
                        yield Label(
                            "[dim]Rendimiento por Minuto[/]", classes="chart-label"
                        )
                        yield Sparkline(
                            data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                            id="performance_sparkline",
                            classes="performance-chart",
                        )
                        yield Label("[dim]Uso de Memoria[/]", classes="chart-label")
                        yield ProgressBar(
                            total=100,
                            progress=45,
                            id="memory_usage",
                            show_percentage=True,
                        )


class DomainIntelligencePanel(Static):
    """Panel de inteligencia por dominio"""

    def compose(self) -> ComposeResult:
        with Container(classes="domain-panel"):
            yield Label(
                "[bold blue]🌐 Inteligencia de Dominios[/]", classes="panel-title"
            )

            with Container(classes="domain-content"):
                yield DataTable(id="domain_table", classes="domain-table")

                # Configurar tabla
                table = self.query_one("#domain_table", DataTable)
                table.add_columns("Dominio", "URLs", "Éxito %", "Patrones", "IA Score")

                # Datos de ejemplo
                table.add_rows(
                    [
                        ("books.toscrape.com", "1,247", "98.5%", "12", "A+"),
                        ("quotes.toscrape.com", "892", "95.2%", "8", "A"),
                        ("scrape.center", "456", "87.1%", "5", "B+"),
                        ("example.com", "123", "92.3%", "3", "B"),
                    ]
                )


class AIAssistantInterface(Static):
    """Interfaz del asistente de IA integrado"""

    def compose(self) -> ComposeResult:
        with Container(classes="ai-assistant-panel"):
            yield Label("[bold purple]🤖 Asistente de IA[/]", classes="panel-title")

            with Vertical(classes="assistant-content"):
                yield Label(
                    "[dim]Estado: Conectado y listo[/]", classes="assistant-status"
                )

                with Container(classes="assistant-actions"):
                    yield Button(
                        "🔍 Análisis Inteligente",
                        variant="primary",
                        id="ai_analyze",
                        classes="assistant-button",
                    )
                    yield Button(
                        "🛠️ Auto-Reparación",
                        variant="success",
                        id="ai_repair",
                        classes="assistant-button",
                    )
                    yield Button(
                        "📊 Generar Reporte",
                        variant="warning",
                        id="ai_report",
                        classes="assistant-button",
                    )
                    yield Button(
                        "🧠 Brain Snapshot",
                        variant="default",
                        id="ai_snapshot",
                        classes="assistant-button",
                    )


class SystemStatusBar(Static):
    """Barra de estado del sistema"""

    def compose(self) -> ComposeResult:
        with Horizontal(classes="status-bar"):
            yield Label(
                "[green]●[/] Sistema: OPERATIVO",
                id="system_status",
                classes="status-item",
            )
            yield Label("🧠 Brain: HÍBRIDO", id="brain_mode", classes="status-item")
            yield Label("🔄 Workers: 8/8", id="workers_status", classes="status-item")
            yield Label("📊 DB: CONECTADA", id="db_status", classes="status-item")
            yield Label(
                f"⏰ {datetime.now().strftime('%H:%M:%S')}",
                id="current_time",
                classes="status-item",
            )


class ProfessionalDashboard(Container):
    """Dashboard principal profesional que integra todos los widgets"""

    def compose(self) -> ComposeResult:
        with Grid(id="dashboard-grid", classes="professional-dashboard"):
            # Fila superior: Métricas principales
            with Container(classes="top-row"):
                yield ProfessionalMetricsPanel(title="Métricas de Rendimiento")
                yield IntelligenceControlCenter()

            # Fila media: Operaciones y monitoreo
            with Container(classes="middle-row"):
                yield AdvancedOperationsPanel()
                yield RealTimeMonitor()

            # Fila inferior: Inteligencia y asistente
            with Container(classes="bottom-row"):
                yield DomainIntelligencePanel()
                yield AIAssistantInterface()

            # Barra de estado
            yield SystemStatusBar()
