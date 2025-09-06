"""
Widget de Análisis Avanzado para WebScraper PRO
Incluye análisis de patrones, predicciones y insights del cerebro IA
"""

import json
import os
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class AdvancedAnalyticsWidget(QWidget):
    """Widget principal de análisis avanzado con múltiples perspectivas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_data = {}
        self.predictions = {}
        self.setup_ui()
        self.load_analytics_data()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_analytics)
        self.update_timer.start(10000)  # Actualizar cada 10 segundos

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Título principal
        title = QLabel("🔬 ANÁLISIS AVANZADO & PREDICCIONES")
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

        # Tabs principales
        self.main_tabs = QTabWidget()

        # Tab de patrones
        self.patterns_tab = self.create_patterns_tab()
        self.main_tabs.addTab(self.patterns_tab, "🔍 Patrones")

        # Tab de predicciones
        self.predictions_tab = self.create_predictions_tab()
        self.main_tabs.addTab(self.predictions_tab, "🔮 Predicciones")

        # Tab de correlaciones
        self.correlations_tab = self.create_correlations_tab()
        self.main_tabs.addTab(self.correlations_tab, "📊 Correlaciones")

        # Tab de insights
        self.insights_tab = self.create_insights_tab()
        self.main_tabs.addTab(self.insights_tab, "💡 Insights IA")

        layout.addWidget(self.main_tabs)

    def create_patterns_tab(self):
        """Crear tab de análisis de patrones."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título
        pattern_title = QLabel("🔍 ANÁLISIS DE PATRONES")
        pattern_title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        pattern_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pattern_title)

        # Splitter para gráficos y lista
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel de gráficos
        charts_panel = QWidget()
        charts_layout = QVBoxLayout(charts_panel)

        self.patterns_chart = self.create_chart_widget("Patrones de Error")
        charts_layout.addWidget(self.patterns_chart)

        self.success_patterns_chart = self.create_chart_widget("Patrones de Éxito")
        charts_layout.addWidget(self.success_patterns_chart)

        splitter.addWidget(charts_panel)

        # Panel de lista de patrones
        patterns_list_panel = QWidget()
        patterns_list_layout = QVBoxLayout(patterns_list_panel)

        patterns_list_title = QLabel("📋 Patrones Identificados")
        patterns_list_title.setStyleSheet("color: #C9D1D9; font-weight: bold;")
        patterns_list_layout.addWidget(patterns_list_title)

        self.patterns_list = QListWidget()
        self.patterns_list.setStyleSheet(
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
        """
        )
        patterns_list_layout.addWidget(self.patterns_list)

        splitter.addWidget(patterns_list_panel)

        # Configurar splitter
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)

        return widget

    def create_predictions_tab(self):
        """Crear tab de predicciones."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título
        prediction_title = QLabel("🔮 PREDICCIONES DEL SISTEMA")
        prediction_title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        prediction_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(prediction_title)

        # Panel de predicciones
        predictions_layout = QHBoxLayout()

        # Predicción de rendimiento
        performance_group = QGroupBox("🎯 Rendimiento Predicho")
        performance_layout = QVBoxLayout(performance_group)

        self.predicted_success_label = QLabel("0%")
        self.predicted_success_label.setStyleSheet(
            """
            QLabel {
                color: #4CAF50;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }
        """
        )
        self.predicted_success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prediction_confidence_label = QLabel("Confianza: 0%")
        self.prediction_confidence_label.setStyleSheet(
            """
            QLabel {
                color: #FF9800;
                font-size: 12px;
                text-align: center;
            }
        """
        )
        self.prediction_confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        performance_layout.addWidget(QLabel("Tasa de Éxito Predicha:"))
        performance_layout.addWidget(self.predicted_success_label)
        performance_layout.addWidget(self.prediction_confidence_label)
        performance_layout.addStretch()

        predictions_layout.addWidget(performance_group)

        # Recomendaciones
        recommendations_group = QGroupBox("💡 Recomendaciones")
        recommendations_layout = QVBoxLayout(recommendations_group)

        self.recommendations_list = QListWidget()
        self.recommendations_list.setStyleSheet(
            """
            QListWidget {
                border: none;
                background: #161B22;
                color: #C9D1D9;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #30363D;
            }
        """
        )
        recommendations_layout.addWidget(self.recommendations_list)

        predictions_layout.addWidget(recommendations_group)

        layout.addLayout(predictions_layout)

        # Gráfico de tendencias futuras
        self.future_trends_chart = self.create_chart_widget("Tendencias Futuras")
        layout.addWidget(self.future_trends_chart)

        return widget

    def create_correlations_tab(self):
        """Crear tab de análisis de correlaciones."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título
        correlation_title = QLabel("📊 ANÁLISIS DE CORRELACIONES")
        correlation_title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        correlation_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(correlation_title)

        # Matriz de correlación
        correlation_grid = QGridLayout()

        # Variables a correlacionar
        variables = ["Tasa Éxito", "Tiempo Respuesta", "Intentos", "Delay Óptimo"]

        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i == j:
                    # Diagonal principal
                    label = QLabel(f"{var1}")
                    label.setStyleSheet(
                        """
                        QLabel {
                            color: #58A6FF;
                            font-weight: bold;
                            text-align: center;
                            padding: 5px;
                        }
                    """
                    )
                else:
                    # Correlación
                    correlation_value = QLabel("0.00")
                    correlation_value.setStyleSheet(
                        """
                        QLabel {
                            color: #C9D1D9;
                            text-align: center;
                            padding: 5px;
                            background: #21262D;
                            border-radius: 3px;
                        }
                    """
                    )
                    label = correlation_value

                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                correlation_grid.addWidget(label, i, j)

        correlation_group = QGroupBox("Matriz de Correlación")
        correlation_group.setLayout(correlation_grid)
        layout.addWidget(correlation_group)

        # Gráfico de correlación principal
        self.correlation_chart = self.create_chart_widget("Correlación Principal")
        layout.addWidget(self.correlation_chart)

        return widget

    def create_insights_tab(self):
        """Crear tab de insights de IA."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título
        insights_title = QLabel("💡 INSIGHTS INTELIGENTES")
        insights_title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        insights_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(insights_title)

        # Panel de insights
        insights_splitter = QSplitter(Qt.Orientation.Vertical)

        # Insights principales
        insights_panel = QWidget()
        insights_layout = QVBoxLayout(insights_panel)

        self.insights_list = QListWidget()
        self.insights_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #30363D;
                border-radius: 6px;
                background: #161B22;
                color: #C9D1D9;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #30363D;
            }
        """
        )

        # Agregar insights de ejemplo
        insights = [
            "🚀 El dominio 'test.com' muestra el mejor rendimiento con 60% de éxito",
            "⚡ Los delays óptimos están entre 1.0-1.5 segundos para la mayoría de dominios",
            "🎯 Los user agents personalizados mejoran la tasa de éxito en un 15%",
            "📈 Se detectó un patrón de mejora continua en los últimos 7 días",
            "🔧 Se recomienda optimizar el backoff para dominios con alta tasa de error",
        ]

        for insight in insights:
            item = QListWidgetItem(insight)
            self.insights_list.addItem(item)

        insights_layout.addWidget(self.insights_list)

        insights_splitter.addWidget(insights_panel)

        # Panel de métricas detalladas
        metrics_panel = QWidget()
        metrics_layout = QVBoxLayout(metrics_panel)

        metrics_title = QLabel("📈 Métricas Detalladas del Cerebro")
        metrics_title.setStyleSheet("color: #C9D1D9; font-weight: bold;")
        metrics_layout.addWidget(metrics_title)

        self.brain_metrics_text = QTextBrowser()
        self.brain_metrics_text.setStyleSheet(
            """
            QTextBrowser {
                border: 1px solid #30363D;
                border-radius: 6px;
                background: #161B22;
                color: #C9D1D9;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """
        )
        metrics_layout.addWidget(self.brain_metrics_text)

        insights_splitter.addWidget(metrics_panel)

        # Configurar splitter
        insights_splitter.setSizes([300, 200])
        layout.addWidget(insights_splitter)

        return widget

    def create_chart_widget(self, title: str):
        """Crear un widget de gráfico básico."""
        from .metrics_dashboard import MetricsChartWidget

        return MetricsChartWidget(title)

    def load_analytics_data(self):
        """Cargar datos para análisis avanzado."""
        try:
            # Cargar datos de aprendizaje
            learning_file = os.path.join("data", "learning_history.json")
            if os.path.exists(learning_file):
                with open(learning_file, encoding="utf-8") as f:
                    learning_data = json.load(f)
                    self.analytics_data["learning"] = learning_data

            # Cargar datos del cerebro
            brain_file = os.path.join("data", "brain_state.json")
            if os.path.exists(brain_file):
                with open(brain_file, encoding="utf-8") as f:
                    brain_data = json.load(f)
                    self.analytics_data["brain"] = brain_data

            # Cargar métricas globales
            metrics_file = os.path.join("artifacts", "metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, encoding="utf-8") as f:
                    metrics_data = json.load(f)
                    self.analytics_data["metrics"] = metrics_data

            self.update_analytics_display()

        except Exception as e:
            print(f"Error cargando datos de análisis: {e}")

    def update_analytics_display(self):
        """Actualizar la visualización de análisis."""
        if not self.analytics_data:
            return

        # Actualizar patrones
        self.update_patterns_analysis()

        # Actualizar predicciones
        self.update_predictions()

        # Actualizar correlaciones
        self.update_correlations()

        # Actualizar insights
        self.update_insights()

    def update_patterns_analysis(self):
        """Actualizar análisis de patrones."""
        if "learning" not in self.analytics_data:
            return

        domains = self.analytics_data["learning"].get("domains", [])

        # Analizar patrones de error
        error_patterns = {}
        for domain in domains:
            for error in domain.get("error_patterns", []):
                error_patterns[error] = error_patterns.get(error, 0) + 1

        if error_patterns:
            self.patterns_chart.create_bar_chart(
                error_patterns, "Frecuencia de Patrones de Error"
            )

        # Analizar patrones de éxito
        success_patterns = {}
        for domain in domains:
            success_rate = domain.get("success_rate", 0)
            if success_rate > 0.5:  # Alto rendimiento
                success_patterns[domain["domain"]] = success_rate * 100

        if success_patterns:
            self.success_patterns_chart.create_bar_chart(
                success_patterns, "Dominios de Alto Rendimiento"
            )

        # Actualizar lista de patrones
        self.patterns_list.clear()
        for pattern, count in error_patterns.items():
            item = QListWidgetItem(f"🔴 {pattern}: {count} ocurrencias")
            self.patterns_list.addItem(item)

    def update_predictions(self):
        """Actualizar predicciones del sistema."""
        if "learning" not in self.analytics_data:
            return

        domains = self.analytics_data["learning"].get("domains", [])

        if domains:
            # Calcular tasa de éxito promedio ponderada
            total_attempts = sum(d["total_attempts"] for d in domains)
            weighted_success = (
                sum(d["success_rate"] * d["total_attempts"] for d in domains)
                / total_attempts
                if total_attempts > 0
                else 0
            )

            self.predicted_success_label.setText(f"{weighted_success:.1%}")
            self.prediction_confidence_label.setText(
                f"Confianza: {min(95, len(domains) * 10)}%"
            )

            # Generar recomendaciones
            self.recommendations_list.clear()

            recommendations = []

            # Recomendación basada en delays óptimos
            avg_optimal_delay = sum(d["optimal_delay"] for d in domains) / len(domains)
            if avg_optimal_delay > 1.5:
                recommendations.append("⚡ Considera reducir los delays entre requests")
            elif avg_optimal_delay < 0.8:
                recommendations.append("⏱️ Los delays actuales son muy agresivos")

            # Recomendación basada en tasa de éxito
            low_success_domains = [d for d in domains if d["success_rate"] < 0.3]
            if low_success_domains:
                recommendations.append(
                    f"🎯 Optimizar {len(low_success_domains)} dominios de bajo rendimiento"
                )

            # Recomendación basada en user agents
            ua_variety = len(set(d["preferred_user_agent"] for d in domains))
            if ua_variety < len(domains) * 0.5:
                recommendations.append(
                    "🤖 Diversificar user agents para mejor camuflaje"
                )

            if not recommendations:
                recommendations.append("✅ El sistema está funcionando óptimamente")

            for rec in recommendations:
                self.recommendations_list.addItem(rec)

    def update_correlations(self):
        """Actualizar análisis de correlaciones."""
        if "learning" not in self.analytics_data:
            return

        domains = self.analytics_data["learning"].get("domains", [])

        if len(domains) > 1:
            # Calcular correlaciones simples
            success_rates = [d["success_rate"] for d in domains]
            response_times = [d["avg_response_time"] for d in domains]
            attempts = [d["total_attempts"] for d in domains]
            optimal_delays = [d["optimal_delay"] for d in domains]

            # Correlación entre éxito y tiempo de respuesta
            correlation_data = {
                "Éxito vs Tiempo": self.calculate_correlation(
                    success_rates, response_times
                ),
                "Intentos vs Éxito": self.calculate_correlation(
                    attempts, success_rates
                ),
                "Delay vs Éxito": self.calculate_correlation(
                    optimal_delays, success_rates
                ),
            }

            self.correlation_chart.create_bar_chart(
                correlation_data, "Correlaciones Principales"
            )

    def update_insights(self):
        """Actualizar insights inteligentes."""
        if not self.analytics_data:
            return

        # Generar métricas detalladas del cerebro
        brain_info = []

        if "learning" in self.analytics_data:
            domains = self.analytics_data["learning"].get("domains", [])
            brain_info.append(f"📊 Dominios analizados: {len(domains)}")

            if domains:
                avg_success = sum(d["success_rate"] for d in domains) / len(domains)
                brain_info.append(f"🎯 Tasa de éxito promedio: {avg_success:.1%}")

                best_domain = max(domains, key=lambda x: x["success_rate"])
                brain_info.append(
                    f"🏆 Mejor dominio: {best_domain['domain']} ({best_domain['success_rate']:.1%})"
                )

        if "brain" in self.analytics_data:
            recent_events = self.analytics_data["brain"].get("recent_events", [])
            brain_info.append(f"🕐 Eventos recientes: {len(recent_events)}")

        brain_metrics_text = "\n".join(brain_info)
        self.brain_metrics_text.setPlainText(brain_metrics_text)

    def calculate_correlation(self, x: list[float], y: list[float]) -> float:
        """Calcular correlación de Pearson simple."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y, strict=False))
        sum_x2 = sum(xi**2 for xi in x)
        sum_y2 = sum(yi**2 for yi in y)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)) ** 0.5

        return numerator / denominator if denominator != 0 else 0.0

    def refresh_analytics(self):
        """Refrescar análisis periódicamente."""
        self.load_analytics_data()


class DataExportWidget(QWidget):
    """Widget para exportar datos y reportes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("📤 EXPORTACIÓN DE DATOS")
        title.setStyleSheet(
            """
            QLabel {
                color: #58A6FF;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Panel de opciones de exportación
        export_group = QGroupBox("Opciones de Exportación")
        export_layout = QGridLayout(export_group)

        # Formatos disponibles
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JSON", "CSV", "Excel", "Markdown", "PDF"])

        # Datos a exportar
        self.data_combo = QComboBox()
        self.data_combo.addItems(
            [
                "Métricas Globales",
                "Historial de Aprendizaje",
                "Base de Conocimientos",
                "Estado del Cerebro",
                "Análisis Completo",
            ]
        )

        # Rango de fechas
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText("YYYY-MM-DD")
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText("YYYY-MM-DD")

        export_layout.addWidget(QLabel("Formato:"), 0, 0)
        export_layout.addWidget(self.format_combo, 0, 1)
        export_layout.addWidget(QLabel("Datos:"), 1, 0)
        export_layout.addWidget(self.data_combo, 1, 1)
        export_layout.addWidget(QLabel("Desde:"), 2, 0)
        export_layout.addWidget(self.date_from, 2, 1)
        export_layout.addWidget(QLabel("Hasta:"), 3, 0)
        export_layout.addWidget(self.date_to, 3, 1)

        layout.addWidget(export_group)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        self.export_button = QPushButton("📤 Exportar")
        self.export_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #238636, stop:1 #1A7F37);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2EA043, stop:1 #238636);
            }
        """
        )
        self.export_button.clicked.connect(self.export_data)

        self.preview_button = QPushButton("👁️ Vista Previa")
        self.preview_button.clicked.connect(self.preview_data)

        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Área de preview
        self.preview_area = QTextBrowser()
        self.preview_area.setStyleSheet(
            """
            QTextBrowser {
                border: 1px solid #30363D;
                border-radius: 6px;
                background: #161B22;
                color: #C9D1D9;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """
        )
        layout.addWidget(self.preview_area)

    def export_data(self):
        """Exportar datos en el formato seleccionado."""
        # Implementar lógica de exportación aquí
        print(
            f"Exportando {self.data_combo.currentText()} en formato {self.format_combo.currentText()}"
        )

    def preview_data(self):
        """Mostrar vista previa de los datos a exportar."""
        data_type = self.data_combo.currentText()

        if data_type == "Métricas Globales":
            self.show_metrics_preview()
        elif data_type == "Historial de Aprendizaje":
            self.show_learning_preview()
        elif data_type == "Base de Conocimientos":
            self.show_knowledge_preview()
        elif data_type == "Estado del Cerebro":
            self.show_brain_preview()
        elif data_type == "Análisis Completo":
            self.show_full_analysis_preview()

    def show_metrics_preview(self):
        """Mostrar preview de métricas."""
        try:
            with open("artifacts/metrics.json", encoding="utf-8") as f:
                data = json.load(f)
                self.preview_area.setPlainText(json.dumps(data, indent=2))
        except:
            self.preview_area.setPlainText("Error cargando métricas")

    def show_learning_preview(self):
        """Mostrar preview de historial de aprendizaje."""
        try:
            with open("data/learning_history.json", encoding="utf-8") as f:
                data = json.load(f)
                # Mostrar solo primeros 3 dominios para preview
                preview_data = data.copy()
                preview_data["domains"] = data["domains"][:3]
                self.preview_area.setPlainText(json.dumps(preview_data, indent=2))
        except:
            self.preview_area.setPlainText("Error cargando historial de aprendizaje")

    def show_knowledge_preview(self):
        """Mostrar preview de base de conocimientos."""
        try:
            with open("data/knowledge_base.json", encoding="utf-8") as f:
                data = json.load(f)
                # Mostrar solo primeros 3 items para preview
                preview_data = data[:3] if isinstance(data, list) else data
                self.preview_area.setPlainText(json.dumps(preview_data, indent=2))
        except:
            self.preview_area.setPlainText("Error cargando base de conocimientos")

    def show_brain_preview(self):
        """Mostrar preview de estado del cerebro."""
        try:
            with open("data/brain_state.json", encoding="utf-8") as f:
                data = json.load(f)
                # Mostrar resumen del estado
                preview = {
                    "total_events": len(data.get("recent_events", [])),
                    "domain_stats": data.get("domain_stats", {}),
                    "error_summary": "Datos disponibles",
                }
                self.preview_area.setPlainText(json.dumps(preview, indent=2))
        except:
            self.preview_area.setPlainText("Error cargando estado del cerebro")

    def show_full_analysis_preview(self):
        """Mostrar preview de análisis completo."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "summary": "Análisis completo del sistema WebScraper PRO",
            "components": [
                "Métricas globales",
                "Historial de aprendizaje",
                "Base de conocimientos",
                "Estado del cerebro IA",
                "Patrones identificados",
                "Predicciones del sistema",
            ],
        }
        self.preview_area.setPlainText(json.dumps(analysis, indent=2))
