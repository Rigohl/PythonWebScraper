"""
Dashboard de Métricas Avanzado para WebScraper PRO
Incluye gráficos interactivos, análisis en tiempo real y visualización de datos
"""

import json
import logging
import os
from datetime import datetime

from PyQt6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QLineSeries,
    QPieSeries,
    QValueAxis,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class MetricsChartWidget(QWidget):
    """Widget para gráficos de métricas con PyQt6 Charts."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.chart_view = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title_label = QLabel(f"📊 {self.title}")
        title_label.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet(
            """
            QChartView {
                border: 1px solid #30363D;
                border-radius: 8px;
                background: #161B22;
            }
        """
        )
        layout.addWidget(self.chart_view)

    def create_bar_chart(self, data: dict[str, float], title: str):
        """Crear gráfico de barras."""
        series = QBarSeries()

        bar_set = QBarSet("Valor")
        categories = []

        for category, value in data.items():
            bar_set.append(value)
            categories.append(category)

        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(data.values()) * 1.2)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)

    def create_line_chart(self, data: list[tuple], title: str):
        """Crear gráfico de líneas."""
        series = QLineSeries()
        series.setName("Tendencia")

        for x, y in data:
            series.append(x, y)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QValueAxis()
        axis_x.setRange(0, len(data))
        axis_x.setLabelFormat("%d")
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        y_values = [y for _, y in data]
        axis_y.setRange(min(y_values), max(y_values) * 1.2)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)

    def create_pie_chart(self, data: dict[str, float], title: str):
        """Crear gráfico circular."""
        series = QPieSeries()

        for category, value in data.items():
            slice_item = series.append(category, value)
            slice_item.setLabelVisible(True)
            slice_item.setLabelColor(Qt.GlobalColor.white)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.chart_view.setChart(chart)


class MetricsDashboard(QWidget):
    """Dashboard principal de métricas con múltiples visualizaciones."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_data = {}
        self.brain_data = {}
        self.learning_data = {}
        self.setup_ui()
        self.load_data()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(5000)  # Actualizar cada 5 segundos

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Título principal
        title = QLabel("🎯 DASHBOARD DE MÉTRICAS AVANZADO")
        title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Splitter principal
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Panel superior: Métricas principales
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)

        # Métricas globales
        self.global_metrics_group = QGroupBox("📈 Métricas Globales")
        global_layout = QGridLayout(self.global_metrics_group)

        self.total_scrapes_label = QLabel("0")
        self.success_rate_label = QLabel("0%")
        self.avg_response_time_label = QLabel("0s")
        self.active_domains_label = QLabel("0")

        metrics = [
            ("Total Scrapes:", self.total_scrapes_label),
            ("Tasa de Éxito:", self.success_rate_label),
            ("Tiempo Promedio:", self.avg_response_time_label),
            ("Dominios Activos:", self.active_domains_label),
        ]

        for i, (label_text, value_label) in enumerate(metrics):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; color: #C9D1D9;")
            value_label.setStyleSheet(
                """
                QLabel {
                    color: #58A6FF;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 5px;
                    background: #21262D;
                    border-radius: 5px;
                }
            """
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            global_layout.addWidget(label, i // 2, (i % 2) * 2)
            global_layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)

        top_layout.addWidget(self.global_metrics_group)

        # Gráfico de éxito por dominio
        self.success_chart = MetricsChartWidget("Éxito por Dominio")
        top_layout.addWidget(self.success_chart)

        main_splitter.addWidget(top_panel)

        # Panel inferior: Tabs con diferentes análisis
        bottom_panel = QTabWidget()

        # Tab de tendencias
        trends_tab = QWidget()
        trends_layout = QVBoxLayout(trends_tab)

        self.trends_chart = MetricsChartWidget("Tendencias de Rendimiento")
        trends_layout.addWidget(self.trends_chart)

        # Controles de filtro
        filter_layout = QHBoxLayout()

        self.time_filter = QComboBox()
        self.time_filter.addItems(
            ["Última hora", "Últimas 24h", "Última semana", "Todo"]
        )
        self.time_filter.currentTextChanged.connect(self.apply_filters)

        self.domain_filter = QLineEdit()
        self.domain_filter.setPlaceholderText("Filtrar por dominio...")
        self.domain_filter.textChanged.connect(self.apply_filters)

        filter_layout.addWidget(QLabel("Periodo:"))
        filter_layout.addWidget(self.time_filter)
        filter_layout.addWidget(QLabel("Dominio:"))
        filter_layout.addWidget(self.domain_filter)
        filter_layout.addStretch()

        trends_layout.addLayout(filter_layout)
        bottom_panel.addTab(trends_tab, "📈 Tendencias")

        # Tab de dominios
        domains_tab = QWidget()
        domains_layout = QVBoxLayout(domains_tab)

        self.domains_table = QTableWidget()
        self.domains_table.setColumnCount(5)
        self.domains_table.setHorizontalHeaderLabels(
            ["Dominio", "Total", "Éxito", "Tasa", "Tiempo Promedio"]
        )
        self.domains_table.setStyleSheet(
            """
            QTableWidget {
                background: #161B22;
                color: #C9D1D9;
                border: 1px solid #30363D;
                border-radius: 6px;
            }
            QHeaderView::section {
                background: #21262D;
                color: #58A6FF;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #30363D;
            }
            QTableWidget::item:selected {
                background: #30363D;
            }
        """
        )
        domains_layout.addWidget(self.domains_table)

        bottom_panel.addTab(domains_tab, "🌐 Dominios")

        # Tab de análisis de cerebro
        brain_tab = QWidget()
        brain_layout = QVBoxLayout(brain_tab)

        self.brain_chart = MetricsChartWidget("Análisis del Cerebro IA")
        brain_layout.addWidget(self.brain_chart)

        # Estadísticas del cerebro
        brain_stats_layout = QHBoxLayout()

        self.knowledge_snippets_label = QLabel("0")
        self.learning_sessions_label = QLabel("0")
        self.brain_patterns_label = QLabel("0")

        brain_stats = [
            ("Snippets de Conocimiento:", self.knowledge_snippets_label),
            ("Sesiones de Aprendizaje:", self.learning_sessions_label),
            ("Patrones Identificados:", self.brain_patterns_label),
        ]

        for label_text, value_label in brain_stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setContentsMargins(0, 0, 0, 0)

            stat_label = QLabel(label_text)
            stat_label.setStyleSheet("color: #C9D1D9; font-size: 11px;")
            value_label.setStyleSheet(
                """
                QLabel {
                    color: #58A6FF;
                    font-size: 14px;
                    font-weight: bold;
                }
            """
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stat_layout.addWidget(stat_label)
            stat_layout.addWidget(value_label)
            brain_stats_layout.addWidget(stat_widget)

        brain_layout.addLayout(brain_stats_layout)
        bottom_panel.addTab(brain_tab, "🧠 Cerebro IA")

        main_splitter.addWidget(bottom_panel)

        # Configurar splitter
        main_splitter.setSizes([300, 500])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        layout.addWidget(main_splitter)

    def load_data(self):
        """Cargar datos de métricas desde archivos."""
        try:
            # Cargar métricas globales
            metrics_file = os.path.join("artifacts", "metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, encoding="utf-8") as f:
                    self.metrics_data = json.load(f)

            # Cargar datos del cerebro
            brain_file = os.path.join("data", "brain_state.json")
            if os.path.exists(brain_file):
                with open(brain_file, encoding="utf-8") as f:
                    self.brain_data = json.load(f)

            # Cargar datos de aprendizaje
            learning_file = os.path.join("data", "learning_history.json")
            if os.path.exists(learning_file):
                with open(learning_file, encoding="utf-8") as f:
                    self.learning_data = json.load(f)

            self.update_display()

        except Exception as e:
            logger.exception("Error cargando datos: %s", e)

    def update_display(self):
        """Actualizar la visualización con los datos cargados."""
        # Actualizar métricas globales
        if self.metrics_data:
            self.total_scrapes_label.setText(
                str(self.metrics_data.get("total_scrapes", 0))
            )
            self.success_rate_label.setText(
                f"{self.metrics_data.get('success_rate_percent', 0):.1f}%"
            )
            self.avg_response_time_label.setText(
                f"{self.metrics_data.get('average_response_time_seconds', 0):.1f}s"
            )

        # Actualizar gráfico de éxito por dominio
        if self.brain_data and "domain_stats" in self.brain_data:
            domain_success = {}
            for domain, stats in self.brain_data["domain_stats"].items():
                success_rate = stats.get("success_rate", 0)
                domain_success[domain] = success_rate

            if domain_success:
                self.success_chart.create_bar_chart(
                    domain_success, "Tasa de Éxito por Dominio"
                )

        # Actualizar tabla de dominios
        if self.learning_data and "domains" in self.learning_data:
            self.domains_table.setRowCount(len(self.learning_data["domains"]))

            for row, domain_data in enumerate(self.learning_data["domains"]):
                self.domains_table.setItem(
                    row, 0, QTableWidgetItem(domain_data["domain"])
                )
                self.domains_table.setItem(
                    row, 1, QTableWidgetItem(str(domain_data["total_attempts"]))
                )
                self.domains_table.setItem(
                    row, 2, QTableWidgetItem(f"{domain_data['success_rate']:.1%}")
                )
                self.domains_table.setItem(
                    row, 3, QTableWidgetItem(f"{domain_data['avg_response_time']:.2f}s")
                )
                self.domains_table.setItem(
                    row, 4, QTableWidgetItem(f"{domain_data['optimal_delay']:.1f}s")
                )

        # Actualizar estadísticas del cerebro
        knowledge_file = os.path.join("data", "knowledge_base.json")
        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, encoding="utf-8") as f:
                    knowledge_data = json.load(f)
                    if isinstance(knowledge_data, list):
                        self.knowledge_snippets_label.setText(str(len(knowledge_data)))
            except Exception as e:
                logger.exception("Error leyendo knowledge_base.json: %s", e)

        if self.learning_data and "domains" in self.learning_data:
            self.learning_sessions_label.setText(
                str(len(self.learning_data["domains"]))
            )

        # Crear gráfico de tendencias (simulado con datos históricos)
        if self.brain_data and "recent_events" in self.brain_data:
            trends_data = []
            for i, event in enumerate(self.brain_data["recent_events"][:10]):
                trends_data.append((i, event.get("response_time", 0)))

            if trends_data:
                self.trends_chart.create_line_chart(
                    trends_data, "Tiempos de Respuesta Recientes"
                )

    def apply_filters(self):
        """Aplicar filtros a los datos mostrados."""
        # Implementar lógica de filtrado aquí
        pass

    def refresh_data(self):
        """Refrescar datos periódicamente."""
        self.load_data()


class BrainExplorerWidget(QWidget):
    """Widget para explorar y navegar la base de conocimientos del cerebro."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.knowledge_data = []
        self.setup_ui()
        self.load_knowledge_base()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("🧠 EXPLORADOR DEL CEREBRO IA")
        title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Panel de búsqueda y filtros
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en base de conocimientos...")
        self.search_input.textChanged.connect(self.filter_knowledge)

        self.category_filter = QComboBox()
        self.category_filter.addItem("Todas las categorías")
        self.category_filter.currentTextChanged.connect(self.filter_knowledge)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.category_filter)
        layout.addLayout(search_layout)

        # Splitter para lista y detalles
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista de conocimientos
        self.knowledge_list = QListWidget()
        self.knowledge_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #30363D;
                border-radius: 6px;
                background: #161B22;
                color: #C9D1D9;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #30363D;
            }
            QListWidget::item:selected {
                background: #30363D;
                color: #58A6FF;
            }
        """
        )
        self.knowledge_list.itemClicked.connect(self.show_knowledge_details)
        splitter.addWidget(self.knowledge_list)

        # Panel de detalles
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        self.details_title = QLabel("Selecciona un elemento")
        self.details_title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )

        self.details_content = QTextBrowser()
        self.details_content.setStyleSheet(
            """
            QTextBrowser {
                border: 1px solid #30363D;
                border-radius: 6px;
                background: #161B22;
                color: #C9D1D9;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """
        )

        details_layout.addWidget(self.details_title)
        details_layout.addWidget(self.details_content)

        splitter.addWidget(details_widget)

        # Configurar splitter
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)

    def load_knowledge_base(self):
        """Cargar la base de conocimientos."""
        try:
            knowledge_file = os.path.join("data", "knowledge_base.json")
            if os.path.exists(knowledge_file):
                with open(knowledge_file, encoding="utf-8") as f:
                    self.knowledge_data = json.load(f)

                # Actualizar filtro de categorías
                categories = set()
                for item in self.knowledge_data:
                    if "category" in item:
                        categories.add(item["category"])

                self.category_filter.clear()
                self.category_filter.addItem("Todas las categorías")
                for category in sorted(categories):
                    self.category_filter.addItem(category)

                self.update_knowledge_list()

        except Exception as e:
            logger.exception("Error cargando base de conocimientos: %s", e)

    def update_knowledge_list(self):
        """Actualizar la lista de conocimientos."""
        self.knowledge_list.clear()

        for item in self.knowledge_data:
            title = item.get("title", "Sin título")
            category = item.get("category", "Sin categoría")
            quality = item.get("quality_score", 0)

            display_text = f"[{category}] {title} (Calidad: {quality})"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.knowledge_list.addItem(list_item)

    def filter_knowledge(self):
        """Filtrar la lista de conocimientos."""
        search_text = self.search_input.text().lower()
        selected_category = self.category_filter.currentText()

        for i in range(self.knowledge_list.count()):
            item = self.knowledge_list.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)

            # Filtro de búsqueda
            matches_search = (
                search_text in item_data.get("title", "").lower()
                or search_text in item_data.get("content", "").lower()
                or search_text in item_data.get("category", "").lower()
            )

            # Filtro de categoría
            matches_category = (
                selected_category == "Todas las categorías"
                or item_data.get("category") == selected_category
            )

            item.setHidden(not (matches_search and matches_category))

    def show_knowledge_details(self, item):
        """Mostrar detalles del elemento seleccionado."""
        item_data = item.data(Qt.ItemDataRole.UserRole)

        self.details_title.setText(item_data.get("title", "Sin título"))

        content = f"""
<b>Categoría:</b> {item_data.get('category', 'N/A')}<br>
<b>Calidad:</b> {item_data.get('quality_score', 0)}<br>
<b>Etiquetas:</b> {', '.join(item_data.get('tags', []))}<br>
<b>ID:</b> {item_data.get('id', 'N/A')}<br><br>

<b>Contenido:</b><br>
{item_data.get('content', 'Sin contenido')}
        """

        self.details_content.setHtml(content)


class LearningHistoryWidget(QWidget):
    """Widget para visualizar el historial de aprendizaje del sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.learning_data = []
        self.setup_ui()
        self.load_learning_history()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("📚 HISTORIAL DE APRENDIZAJE")
        title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Filtros
        filter_layout = QHBoxLayout()

        self.domain_filter = QComboBox()
        self.domain_filter.addItem("Todos los dominios")
        self.domain_filter.currentTextChanged.connect(self.filter_history)

        self.sort_by = QComboBox()
        self.sort_by.addItems(["Fecha", "Éxito", "Tiempo de respuesta", "Intentos"])
        self.sort_by.currentTextChanged.connect(self.sort_history)

        filter_layout.addWidget(QLabel("Dominio:"))
        filter_layout.addWidget(self.domain_filter)
        filter_layout.addWidget(QLabel("Ordenar por:"))
        filter_layout.addWidget(self.sort_by)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Tabla de historial
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            [
                "Dominio",
                "Intentos",
                "Éxito",
                "Tasa",
                "Tiempo Promedio",
                "Delay Óptimo",
                "Última Actualización",
            ]
        )
        self.history_table.setStyleSheet(
            """
            QTableWidget {
                background: #161B22;
                color: #C9D1D9;
                border: 1px solid #30363D;
                border-radius: 6px;
            }
            QHeaderView::section {
                background: #21262D;
                color: #58A6FF;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #30363D;
            }
            QTableWidget::item:selected {
                background: #30363D;
            }
        """
        )
        layout.addWidget(self.history_table)

        # Gráfico de rendimiento
        self.performance_chart = MetricsChartWidget("Rendimiento por Dominio")
        layout.addWidget(self.performance_chart)

    def load_learning_history(self):
        """Cargar el historial de aprendizaje."""
        try:
            learning_file = os.path.join("data", "learning_history.json")
            if os.path.exists(learning_file):
                with open(learning_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.learning_data = data.get("domains", [])

                # Actualizar filtro de dominios
                self.domain_filter.clear()
                self.domain_filter.addItem("Todos los dominios")
                for domain_data in self.learning_data:
                    self.domain_filter.addItem(domain_data["domain"])

                self.update_history_table()
                self.update_performance_chart()

        except Exception as e:
            print(f"Error cargando historial de aprendizaje: {e}")

    def update_history_table(self):
        """Actualizar la tabla de historial."""
        filtered_data = self.get_filtered_data()

        self.history_table.setRowCount(len(filtered_data))

        for row, domain_data in enumerate(filtered_data):
            self.history_table.setItem(row, 0, QTableWidgetItem(domain_data["domain"]))
            self.history_table.setItem(
                row, 1, QTableWidgetItem(str(domain_data["total_attempts"]))
            )
            self.history_table.setItem(
                row, 2, QTableWidgetItem(f"{domain_data['success_rate']:.1%}")
            )
            self.history_table.setItem(
                row, 3, QTableWidgetItem(f"{domain_data['avg_response_time']:.2f}s")
            )
            self.history_table.setItem(
                row, 4, QTableWidgetItem(f"{domain_data['optimal_delay']:.1f}s")
            )

            # Última actualización
            timestamp = domain_data.get("last_updated", 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                self.history_table.setItem(
                    row, 5, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M"))
                )
            else:
                self.history_table.setItem(row, 5, QTableWidgetItem("N/A"))

    def update_performance_chart(self):
        """Actualizar el gráfico de rendimiento."""
        if self.learning_data:
            performance_data = {}
            for domain_data in self.learning_data:
                performance_data[domain_data["domain"]] = (
                    domain_data.get("success_rate", 0) * 100
                )

            self.performance_chart.create_bar_chart(
                performance_data, "Tasa de Éxito por Dominio"
            )

    def get_filtered_data(self):
        """Obtener datos filtrados."""
        selected_domain = self.domain_filter.currentText()

        if selected_domain == "Todos los dominios":
            return self.learning_data
        else:
            return [d for d in self.learning_data if d["domain"] == selected_domain]

    def filter_history(self):
        """Aplicar filtro de dominio."""
        self.update_history_table()

    def sort_history(self):
        """Ordenar el historial."""
        sort_key = self.sort_by.currentText()

        if sort_key == "Fecha":
            self.learning_data.sort(
                key=lambda x: x.get("last_updated", 0), reverse=True
            )
        elif sort_key == "Éxito":
            self.learning_data.sort(key=lambda x: x["success_rate"], reverse=True)
        elif sort_key == "Tiempo de respuesta":
            self.learning_data.sort(key=lambda x: x["avg_response_time"])
        elif sort_key == "Intentos":
            self.learning_data.sort(key=lambda x: x["total_attempts"], reverse=True)

        self.update_history_table()
