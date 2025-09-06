"""
Explorador del Cerebro IA para WebScraper PRO
Navegador interactivo de la base de conocimientos
"""

import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


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
            print(f"Error cargando base de conocimientos: {e}")

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
