"""
Historial de Aprendizaje para WebScraper PRO
Visualización del aprendizaje autónomo y evolución del sistema
"""

import json
import os
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


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

        # Panel de filtros
        filter_layout = QHBoxLayout()

        self.domain_filter = QComboBox()
        self.domain_filter.addItem("Todos los dominios")
        self.domain_filter.currentTextChanged.connect(self.filter_learning)

        self.sort_filter = QComboBox()
        self.sort_filter.addItems(["Más reciente", "Más antiguo", "Mejor rendimiento"])
        self.sort_filter.currentTextChanged.connect(self.sort_learning)

        filter_layout.addWidget(QLabel("Dominio:"))
        filter_layout.addWidget(self.domain_filter)
        filter_layout.addWidget(QLabel("Ordenar:"))
        filter_layout.addWidget(self.sort_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Splitter para lista y detalles
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Lista de aprendizaje
        self.learning_list = QListWidget()
        self.learning_list.setStyleSheet(
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
        self.learning_list.itemClicked.connect(self.show_learning_details)
        splitter.addWidget(self.learning_list)

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

    def load_learning_history(self):
        """Cargar el historial de aprendizaje."""
        try:
            # Cargar datos de aprendizaje autónomo
            autonomous_file = os.path.join("data", "autonomous_learning.json")
            if os.path.exists(autonomous_file):
                with open(autonomous_file, encoding="utf-8") as f:
                    autonomous_data = json.load(f)
                    self.process_autonomous_data(autonomous_data)

            # Cargar datos de inteligencia ML
            ml_file = os.path.join("data", "ml_intelligence.json")
            if os.path.exists(ml_file):
                with open(ml_file, encoding="utf-8") as f:
                    ml_data = json.load(f)
                    self.process_ml_data(ml_data)

            # Cargar datos de enriquecimiento del cerebro
            enrichment_file = os.path.join("data", "brain_enrichment.json")
            if os.path.exists(enrichment_file):
                with open(enrichment_file, encoding="utf-8") as f:
                    enrichment_data = json.load(f)
                    self.process_enrichment_data(enrichment_data)

            # Actualizar filtros
            self.update_filters()
            self.update_learning_list()

        except Exception as e:
            print(f"Error cargando historial de aprendizaje: {e}")

    def process_autonomous_data(self, data):
        """Procesar datos de aprendizaje autónomo."""
        for domain, domain_data in data.items():
            if isinstance(domain_data, dict):
                success_rate = domain_data.get("success_rate", 0)
                optimal_delay = domain_data.get("optimal_delay", 0)
                total_attempts = domain_data.get("total_attempts", 0)

                learning_item = {
                    "type": "autonomous",
                    "domain": domain,
                    "title": f"Aprendizaje autónomo - {domain}",
                    "success_rate": success_rate,
                    "optimal_delay": optimal_delay,
                    "total_attempts": total_attempts,
                    "timestamp": datetime.now().isoformat(),
                    "details": f"Éxito: {success_rate:.1f}%, Retraso óptimo: {optimal_delay}s, Intentos: {total_attempts}",
                }
                self.learning_data.append(learning_item)

    def process_ml_data(self, data):
        """Procesar datos de inteligencia ML."""
        for strategy, strategy_data in data.items():
            if isinstance(strategy_data, dict):
                performance = strategy_data.get("performance", 0)
                learning_rate = strategy_data.get("learning_rate", 0)

                learning_item = {
                    "type": "ml",
                    "domain": strategy,
                    "title": f"Inteligencia ML - {strategy}",
                    "performance": performance,
                    "learning_rate": learning_rate,
                    "timestamp": datetime.now().isoformat(),
                    "details": f"Rendimiento: {performance:.2f}, Tasa de aprendizaje: {learning_rate}",
                }
                self.learning_data.append(learning_item)

    def process_enrichment_data(self, data):
        """Procesar datos de enriquecimiento del cerebro."""
        for session, session_data in data.items():
            if isinstance(session_data, dict):
                events = session_data.get("events", [])
                patterns = session_data.get("patterns", {})

                learning_item = {
                    "type": "enrichment",
                    "domain": session,
                    "title": f"Enriquecimiento - {session}",
                    "events_count": len(events),
                    "patterns_count": len(patterns),
                    "timestamp": datetime.now().isoformat(),
                    "details": f"Eventos: {len(events)}, Patrones: {len(patterns)}",
                }
                self.learning_data.append(learning_item)

    def update_filters(self):
        """Actualizar filtros de dominio."""
        domains = set()
        for item in self.learning_data:
            domains.add(item.get("domain", "Sin dominio"))

        self.domain_filter.clear()
        self.domain_filter.addItem("Todos los dominios")
        for domain in sorted(domains):
            self.domain_filter.addItem(domain)

    def update_learning_list(self):
        """Actualizar la lista de aprendizaje."""
        self.learning_list.clear()

        for item in self.learning_data:
            title = item.get("title", "Sin título")
            domain = item.get("domain", "Sin dominio")
            item_type = item.get("type", "desconocido")

            display_text = f"[{item_type.upper()}] {title}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.learning_list.addItem(list_item)

    def filter_learning(self):
        """Filtrar la lista de aprendizaje por dominio."""
        selected_domain = self.domain_filter.currentText()

        for i in range(self.learning_list.count()):
            item = self.learning_list.item(i)
            item_data = item.data(Qt.ItemDataRole.UserRole)

            matches_domain = (
                selected_domain == "Todos los dominios"
                or item_data.get("domain") == selected_domain
            )

            item.setHidden(not matches_domain)

    def sort_learning(self):
        """Ordenar la lista de aprendizaje."""
        sort_option = self.sort_filter.currentText()

        if sort_option == "Más reciente":
            self.learning_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        elif sort_option == "Más antiguo":
            self.learning_data.sort(key=lambda x: x.get("timestamp", ""))
        elif sort_option == "Mejor rendimiento":
            self.learning_data.sort(
                key=lambda x: x.get("success_rate", x.get("performance", 0)),
                reverse=True,
            )

        self.update_learning_list()

    def show_learning_details(self, item):
        """Mostrar detalles del elemento seleccionado."""
        item_data = item.data(Qt.ItemDataRole.UserRole)

        self.details_title.setText(item_data.get("title", "Sin título"))

        content = f"""
<b>Tipo:</b> {item_data.get('type', 'N/A')}<br>
<b>Dominio:</b> {item_data.get('domain', 'N/A')}<br>
<b>Timestamp:</b> {item_data.get('timestamp', 'N/A')}<br><br>

<b>Detalles:</b><br>
{item_data.get('details', 'Sin detalles')}
        """

        if "success_rate" in item_data:
            content += f"<br><b>Tasa de éxito:</b> {item_data['success_rate']:.1f}%"
        if "performance" in item_data:
            content += f"<br><b>Rendimiento:</b> {item_data['performance']:.2f}"
        if "learning_rate" in item_data:
            content += f"<br><b>Tasa de aprendizaje:</b> {item_data['learning_rate']}"

        self.details_content.setHtml(content)
