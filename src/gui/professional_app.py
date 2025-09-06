"""
Interfaz Profesional WebScraper PRO - Sistema de IA Avanzado
Versión con Robot Face Transformers y Chat Inteligente
"""

import sys
from datetime import datetime

from PyQt6.QtCore import QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QAction, QFontDatabase, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QSystemTrayIcon,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .advanced_analytics import AdvancedAnalyticsWidget, DataExportWidget
from .brain_explorer import BrainExplorerWidget
from .learning_history import LearningHistoryWidget
from .robot_widget import RobotFaceWidget


class ChatMessage(QWidget):
    """Widget para mostrar mensajes del chat con animaciones."""

    def __init__(self, message: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setup_ui()
        self.animate_appearance()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Avatar del robot o usuario
        avatar_label = QLabel()
        if self.is_user:
            avatar_label.setText("👤")
            avatar_label.setStyleSheet(
                """
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    border-radius: 15px;
                    color: white;
                    font-size: 16px;
                    padding: 8px;
                }
            """
            )
        else:
            avatar_label.setText("🤖")
            avatar_label.setStyleSheet(
                """
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2196F3, stop:1 #1976D2);
                    border-radius: 15px;
                    color: white;
                    font-size: 16px;
                    padding: 8px;
                }
            """
            )
        avatar_label.setFixedSize(30, 30)
        layout.addWidget(avatar_label)

        # Contenedor del mensaje
        message_container = QWidget()
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)

        # Texto del mensaje
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            f"""
            QLabel {{
                background: {'#E3F2FD' if self.is_user else '#F5F5F5'};
                border-radius: 10px;
                padding: 10px 15px;
                margin: 2px;
                color: {'#2E7D32' if self.is_user else '#1565C0'};
                font-size: 12px;
                border: 1px solid {'#4CAF50' if self.is_user else '#BDBDBD'};
            }}
        """
        )

        message_layout.addWidget(message_label)

        # Timestamp
        timestamp = QLabel(datetime.now().strftime("%H:%M:%S"))
        timestamp.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 8px;
                margin-left: 10px;
            }
        """
        )
        message_layout.addWidget(timestamp)

        layout.addWidget(message_container)
        layout.addStretch()

        if self.is_user:
            layout.setDirection(QHBoxLayout.Direction.RightToLeft)

    def animate_appearance(self):
        """Animación de aparición del mensaje."""
        self.setMaximumHeight(0)
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.start()


class ChatWidget(QWidget):
    """Widget principal del chat con funcionalidades avanzadas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Área de mensajes con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: #FAFAFA;
            }
            QScrollBar:vertical {
                background: #E0E0E0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
        """
        )

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.addStretch()
        self.scroll_area.setWidget(self.messages_container)

        layout.addWidget(self.scroll_area)

        # Área de entrada
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Escribe tu mensaje aquí...")
        self.message_input.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #BDBDBD;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 12px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """
        )
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("📤")
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 20px;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
            QPushButton:pressed {
                background: #0D47A1;
            }
        """
        )
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def add_message(self, message: str, is_user: bool = False):
        """Agrega un mensaje al chat."""
        message_widget = ChatMessage(message, is_user)
        self.messages_layout.insertWidget(
            self.messages_layout.count() - 1, message_widget
        )
        self.messages.append(message_widget)

        # Auto-scroll al final
        QTimer.singleShot(
            100,
            lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            ),
        )

    def send_message(self):
        """Envía un mensaje."""
        message = self.message_input.text().strip()
        if message:
            self.add_message(message, is_user=True)
            self.message_input.clear()
            # Aquí iría la lógica para procesar el mensaje con IA
            QTimer.singleShot(1000, lambda: self.simulate_ai_response(message))

    def simulate_ai_response(self, user_message: str):
        """Simula una respuesta de IA (placeholder)."""
        responses = [
            "Entiendo tu consulta. Déjame procesar la información...",
            "Estoy analizando los datos que proporcionaste.",
            "¡Excelente pregunta! Permíteme investigar eso.",
            "Procesando tu solicitud en tiempo real...",
            "Gracias por tu mensaje. Estoy trabajando en ello.",
        ]
        import random

        response = random.choice(responses)
        self.add_message(f"🤖 {response}")


class ControlPanel(QWidget):
    """Panel de control principal con múltiples opciones."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("🚀 PANEL DE CONTROL")
        title.setStyleSheet(
            """
            QLabel {
                color: #1565C0;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Grupo de URL
        url_group = QGroupBox("🎯 Configuración de URLs")
        url_layout = QVBoxLayout(url_group)

        # allow multiple URLs (one per line)
        from PyQt6.QtWidgets import QTextEdit

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "https://ejemplo.com\nhttps://otro-ejemplo.com"
        )
        self.url_input.setStyleSheet(
            """
            QTextEdit {
                border: 2px solid #BDBDBD;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                background: white;
            }
            QTextEdit:focus {
                border-color: #2196F3;
            }
        """
        )
        self.url_input.setFixedHeight(80)

        url_layout.addWidget(QLabel("URLs (una por línea):"))
        url_layout.addWidget(self.url_input)

        layout.addWidget(url_group)

        # Grupo de opciones
        options_group = QGroupBox("⚙️ Opciones Avanzadas")
        options_layout = QGridLayout(options_group)

        self.concurrency_combo = QComboBox()
        self.concurrency_combo.addItems(["1", "2", "3", "5", "8", "10", "15", "20"])
        self.concurrency_combo.setCurrentText("5")

        self.respect_robots = QPushButton("🤖 Robots.txt")
        self.respect_robots.setCheckable(True)
        self.respect_robots.setChecked(True)

        self.use_ai = QPushButton("🧠 IA Avanzada")
        self.use_ai.setCheckable(True)
        self.use_ai.setChecked(True)

        self.offline_mode = QPushButton("📴 Modo Offline")
        self.offline_mode.setCheckable(True)

        options_layout.addWidget(QLabel("Concurrencia:"), 0, 0)
        options_layout.addWidget(self.concurrency_combo, 0, 1)
        options_layout.addWidget(self.respect_robots, 1, 0)
        options_layout.addWidget(self.use_ai, 1, 1)
        options_layout.addWidget(self.offline_mode, 2, 0)

        layout.addWidget(options_group)

        # Botones de acción
        buttons_layout = QVBoxLayout()

        self.start_button = QPushButton("▶ INICIAR SCRAPING")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #45a049, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: #2E7D32;
            }
        """
        )

        self.stop_button = QPushButton("⏹️ DETENER")
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D32F2F, stop:1 #B71C1C);
            }
        """
        )
        self.stop_button.setEnabled(False)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)

        layout.addLayout(buttons_layout)

        # Sequential processor for scraping
        try:
            from ..scraper.sequential_processor import SequentialProcessor
        except Exception:
            # local relative import fallback
            from src.scraper.sequential_processor import SequentialProcessor

        self._processor = SequentialProcessor()
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #BDBDBD;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
            }
        """
        )
        layout.addWidget(self.progress_bar)

        layout.addStretch()

    def _on_start_clicked(self):
        """Handler for start button: parse URLs, enqueue and run in background."""
        try:
            text = self.url_input.toPlainText()
        except Exception:
            # fallback for single-line inputs
            text = self.url_input.text() if hasattr(self.url_input, "text") else ""

        urls = [line.strip() for line in text.splitlines() if line.strip()]
        if not urls:
            return

        self._processor.enqueue(urls)
        self._processor.start_background()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _on_stop_clicked(self):
        """Handler for stop button: clear pending queue."""
        try:
            with self._processor._lock:
                self._processor.queue.clear()
        except Exception:
            pass
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


class StatsWidget(QWidget):
    """Widget para mostrar estadísticas en tiempo real."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📊 ESTADÍSTICAS EN TIEMPO REAL")
        title.setStyleSheet(
            """
            QLabel {
                color: #1565C0;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Estadísticas principales
        stats_grid = QGridLayout()

        self.urls_processed = QLabel("0")
        self.urls_queued = QLabel("0")
        self.success_rate = QLabel("0%")
        self.errors_count = QLabel("0")

        stats = [
            ("URLs Procesadas:", self.urls_processed),
            ("URLs en Cola:", self.urls_queued),
            ("Tasa de Éxito:", self.success_rate),
            ("Errores:", self.errors_count),
        ]

        for i, (label_text, value_label) in enumerate(stats):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; color: #424242;")
            value_label.setStyleSheet(
                """
                QLabel {
                    color: #1976D2;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 5px;
                    background: #E3F2FD;
                    border-radius: 5px;
                }
            """
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            stats_grid.addWidget(label, i // 2, (i % 2) * 2)
            stats_grid.addWidget(value_label, i // 2, (i % 2) * 2 + 1)

        layout.addLayout(stats_grid)

        # Lista de dominios
        domains_group = QGroupBox("🌐 Dominios Procesados")
        domains_layout = QVBoxLayout(domains_group)

        self.domains_list = QListWidget()
        self.domains_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                background: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background: #E3F2FD;
                color: #1976D2;
            }
        """
        )
        domains_layout.addWidget(self.domains_list)

        layout.addWidget(domains_group)


class ProfessionalMainWindow(QMainWindow):
    """Ventana principal profesional con robot face y chat integrado."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 WebScraper PRO - IA Avanzada")
        self.resize(1400, 900)
        self.setup_menus()
        self.setup_ui()
        self.setup_system_tray()
        self.apply_styles()

    def setup_menus(self):
        """Configura la barra de menús profesional."""
        menubar = self.menuBar()

        # Menú Archivo
        file_menu = menubar.addMenu("📁 Archivo")

        new_action = QAction("🆕 Nuevo Proyecto", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("📂 Abrir Proyecto", self)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("📤 Exportar")
        export_csv = QAction("CSV", self)
        export_json = QAction("JSON", self)
        export_md = QAction("Markdown", self)
        export_menu.addAction(export_csv)
        export_menu.addAction(export_json)
        export_menu.addAction(export_md)

        file_menu.addSeparator()

        exit_action = QAction("🚪 Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú Editar
        edit_menu = menubar.addMenu("✏️ Editar")

        settings_action = QAction("⚙️ Configuración", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)

        # Menú Ver
        view_menu = menubar.addMenu("👁️ Ver")

        toggle_robot = QAction("🤖 Mostrar/Ocultar Robot", self)
        toggle_robot.setCheckable(True)
        toggle_robot.setChecked(True)
        toggle_robot.triggered.connect(self.toggle_robot_face)
        view_menu.addAction(toggle_robot)

        toggle_chat = QAction("💬 Mostrar/Ocultar Chat", self)
        toggle_chat.setCheckable(True)
        toggle_chat.setChecked(True)
        toggle_chat.triggered.connect(self.toggle_chat)
        view_menu.addAction(toggle_chat)

        # Menú Herramientas
        tools_menu = menubar.addMenu("🛠️ Herramientas")

        ai_assistant = QAction("🧠 Asistente IA", self)
        ai_assistant.triggered.connect(self.show_ai_assistant)
        tools_menu.addAction(ai_assistant)

        database_tool = QAction("🗄️ Herramientas de Base de Datos", self)
        database_tool.triggered.connect(self.show_database_tools)
        tools_menu.addAction(database_tool)

        # Menú Datos y Analytics
        data_menu = menubar.addMenu("📊 Datos & Analytics")

        # Submenú Métricas
        metrics_menu = data_menu.addMenu("📈 Métricas")
        dashboard_action = QAction("🎯 Dashboard de Métricas", self)
        dashboard_action.triggered.connect(self.show_metrics_dashboard)
        metrics_menu.addAction(dashboard_action)

        analytics_action = QAction("🔬 Análisis Avanzado", self)
        analytics_action.triggered.connect(self.show_advanced_analytics)
        metrics_menu.addAction(analytics_action)

        # Submenú Cerebro IA
        brain_menu = data_menu.addMenu("🧠 Cerebro IA")
        knowledge_action = QAction("📚 Base de Conocimientos", self)
        knowledge_action.triggered.connect(self.show_knowledge_base)
        brain_menu.addAction(knowledge_action)

        learning_action = QAction("🎓 Historial de Aprendizaje", self)
        learning_action.triggered.connect(self.show_learning_history)
        brain_menu.addAction(learning_action)

        brain_status_action = QAction("🔍 Estado del Cerebro", self)
        brain_status_action.triggered.connect(self.show_brain_status)
        brain_menu.addAction(brain_status_action)

        # Submenú Exportación
        export_menu = data_menu.addMenu("📤 Exportar")
        export_data_action = QAction("💾 Exportar Datos", self)
        export_data_action.triggered.connect(self.show_data_export)
        export_menu.addAction(export_data_action)

        export_report_action = QAction("📋 Generar Reporte", self)
        export_report_action.triggered.connect(self.generate_report)
        export_menu.addAction(export_report_action)

        # Menú Ayuda
        help_menu = menubar.addMenu("❓ Ayuda")

        about_action = QAction("ℹ️ Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("📚 Documentación", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)

    def setup_ui(self):
        """Configura la interfaz de usuario principal."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Splitter principal
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo: Robot + Controles
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Robot face con título
        robot_container = QWidget()
        robot_layout = QVBoxLayout(robot_container)

        robot_title = QLabel("🤖 INTELIGENCIA ARTIFICIAL")
        robot_title.setStyleSheet(
            """
            QLabel {
                color: #1565C0;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 5px;
            }
        """
        )
        robot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        robot_layout.addWidget(robot_title)

        self.robot_face = RobotFaceWidget()
        robot_layout.addWidget(self.robot_face)

        left_layout.addWidget(robot_container)

        # Panel de control
        self.control_panel = ControlPanel()
        left_layout.addWidget(self.control_panel)

        self.main_splitter.addWidget(left_panel)

        # Panel derecho: Tabs con Chat, Stats, Logs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #BDBDBD;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #F5F5F5;
                border: 1px solid #BDBDBD;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
            QTabBar::tab:hover {
                background: #E3F2FD;
            }
        """
        )

        # Tab de Chat
        self.chat_widget = ChatWidget()
        self.tab_widget.addTab(self.chat_widget, "💬 Chat IA")

        # Tab de Estadísticas
        self.stats_widget = StatsWidget()
        self.tab_widget.addTab(self.stats_widget, "📊 Estadísticas")

        # Tab de Logs
        self.logs_widget = QTextBrowser()
        self.logs_widget.setStyleSheet(
            """
            QTextBrowser {
                border: none;
                background: #1E1E1E;
                color: #D4D4D4;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """
        )
        self.tab_widget.addTab(self.logs_widget, "📋 Logs")

        right_layout.addWidget(self.tab_widget)

        self.main_splitter.addWidget(right_panel)

        # Configurar splitter
        self.main_splitter.setSizes([400, 1000])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.main_splitter)

        # Barra de estado
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Listo para iniciar scraping")
        self.status_bar.addWidget(self.status_label)

        # Conectar señales
        self.control_panel.start_button.clicked.connect(self.start_scraping)
        self.control_panel.stop_button.clicked.connect(self.stop_scraping)

        # Mensaje de bienvenida en el chat
        self.chat_widget.add_message(
            "🤖 ¡Hola! Soy tu asistente de IA. ¿En qué puedo ayudarte hoy?"
        )

    def setup_system_tray(self):
        """Configura el icono de la bandeja del sistema."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon())  # Usar un icono por defecto
            self.tray_icon.setToolTip("WebScraper PRO")

            tray_menu = QMenu()
            show_action = QAction("Mostrar", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            quit_action = QAction("Salir", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def apply_styles(self):
        """Aplica estilos globales a la aplicación."""
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FAFAFA, stop:1 #F5F5F5);
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #BDBDBD;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QLabel {
                color: #424242;
            }
        """
        )

    def new_project(self):
        """Crear un nuevo proyecto."""
        QMessageBox.information(
            self, "Nuevo Proyecto", "Funcionalidad próximamente disponible."
        )

    def open_project(self):
        """Abrir un proyecto existente."""
        QMessageBox.information(
            self, "Abrir Proyecto", "Funcionalidad próximamente disponible."
        )

    def show_settings(self):
        """Mostrar configuración."""
        QMessageBox.information(
            self, "Configuración", "Funcionalidad próximamente disponible."
        )

    def toggle_robot_face(self):
        """Mostrar/ocultar el rostro del robot."""
        self.robot_face.setVisible(not self.robot_face.isVisible())

    def toggle_chat(self):
        """Mostrar/ocultar el chat."""
        chat_tab_index = self.tab_widget.indexOf(self.chat_widget)
        if chat_tab_index != -1:
            self.tab_widget.setTabVisible(
                chat_tab_index, not self.tab_widget.isTabVisible(chat_tab_index)
            )

    def show_ai_assistant(self):
        """Mostrar asistente de IA."""
        QMessageBox.information(
            self, "Asistente IA", "Funcionalidad próximamente disponible."
        )

    def show_database_tools(self):
        """Mostrar herramientas de base de datos."""
        QMessageBox.information(
            self, "Herramientas BD", "Funcionalidad próximamente disponible."
        )

    def show_metrics_dashboard(self):
        """Mostrar el dashboard de métricas."""
        from .metrics_dashboard import MetricsDashboard

        dashboard = MetricsDashboard()
        dashboard.setWindowTitle("Dashboard de Métricas - WebScraper PRO")
        dashboard.resize(1200, 800)
        dashboard.show()

    def show_advanced_analytics(self):
        """Mostrar análisis avanzado."""
        analytics = AdvancedAnalyticsWidget()
        analytics.setWindowTitle("Análisis Avanzado - WebScraper PRO")
        analytics.resize(1000, 700)
        analytics.show()

    def show_knowledge_base(self):
        """Mostrar base de conocimientos."""
        explorer = BrainExplorerWidget()
        explorer.setWindowTitle("Explorador del Cerebro IA - WebScraper PRO")
        explorer.resize(1000, 700)
        explorer.show()

    def show_learning_history(self):
        """Mostrar historial de aprendizaje."""
        history = LearningHistoryWidget()
        history.setWindowTitle("Historial de Aprendizaje - WebScraper PRO")
        history.resize(1000, 700)
        history.show()

    def show_brain_status(self):
        """Mostrar estado del cerebro IA."""
        # Crear un widget simple para mostrar el estado del cerebro
        from PyQt6.QtWidgets import QDialog, QTextBrowser, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Estado del Cerebro IA")
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        status_text = QTextBrowser()
        status_text.setHtml(
            """
        <h2>🧠 Estado del Cerebro IA</h2>
        <p><b>Estado:</b> Activo y funcionando</p>
        <p><b>Conocimientos:</b> Base de datos cargada</p>
        <p><b>Aprendizaje:</b> Sistema de aprendizaje autónomo activo</p>
        <p><b>Memoria:</b> Datos de sesiones anteriores disponibles</p>
        <p><b>Inteligencia ML:</b> Modelos de predicción entrenados</p>
        """
        )

        layout.addWidget(status_text)
        dialog.exec()

    def show_data_export(self):
        """Mostrar opciones de exportación de datos."""
        export_widget = DataExportWidget()
        export_widget.setWindowTitle("Exportar Datos - WebScraper PRO")
        export_widget.resize(800, 600)
        export_widget.show()

    def generate_report(self):
        """Generar reporte."""
        from PyQt6.QtWidgets import (
            QDialog,
            QLabel,
            QPushButton,
            QTextBrowser,
            QVBoxLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Generar Reporte")
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        title = QLabel("📋 Generador de Reportes")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        report_content = QTextBrowser()
        report_content.setHtml(
            """
        <h3>Reporte de Actividad - WebScraper PRO</h3>
        <p><b>Fecha de generación:</b> {}</p>
        <p><b>Estado del sistema:</b> Operativo</p>
        <p><b>Métricas recopiladas:</b> Disponibles</p>
        <p><b>Base de conocimientos:</b> Actualizada</p>
        <p><b>Historial de aprendizaje:</b> Registrado</p>
        """.format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        layout.addWidget(report_content)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def show_about(self):
        """Mostrar información sobre la aplicación."""
        QMessageBox.about(
            self,
            "Acerca de WebScraper PRO",
            "🚀 WebScraper PRO v2.1\n\n"
            "Sistema de scraping web inteligente con IA avanzada\n"
            "Interfaz profesional con robot face Transformers\n\n"
            "© 2025 - Tecnología de vanguardia",
        )

    def show_documentation(self):
        """Mostrar documentación."""
        QMessageBox.information(
            self, "Documentación", "Funcionalidad próximamente disponible."
        )

    def start_scraping(self):
        """Iniciar el proceso de scraping."""
        url = self.control_panel.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingresa una URL válida.")
            return

        self.control_panel.start_button.setEnabled(False)
        self.control_panel.stop_button.setEnabled(True)
        self.status_label.setText("Scraping en progreso...")
        self.robot_face.set_activity(0.8)

        # Simular progreso
        self.control_panel.progress_bar.setRange(0, 100)
        for i in range(101):
            QTimer.singleShot(
                i * 50, lambda i=i: self.control_panel.progress_bar.setValue(i)
            )

        # Mensaje en el chat
        self.chat_widget.add_message(f"🚀 Iniciando scraping de: {url}", is_user=True)

    def stop_scraping(self):
        """Detener el proceso de scraping."""
        self.control_panel.start_button.setEnabled(True)
        self.control_panel.stop_button.setEnabled(False)
        self.status_label.setText("Scraping detenido")
        self.robot_face.set_activity(0.0)
        self.chat_widget.add_message("⏹️ Scraping detenido por el usuario")

    def closeEvent(self, event):
        """Manejar el evento de cierre."""
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Estás seguro de que quieres salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, "tray_icon"):
                self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()


def run_professional_gui():
    """Función principal para ejecutar la interfaz profesional."""
    app = QApplication(sys.argv)
    app.setApplicationName("WebScraper PRO")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("WebScraper Team")

    # Configurar fuente
    font_db = QFontDatabase()
    font_db.addApplicationFont(":/fonts/Roboto-Regular.ttf")  # Placeholder

    window = ProfessionalMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_professional_gui()
