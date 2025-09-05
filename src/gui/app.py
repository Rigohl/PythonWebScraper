import logging
import os
from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QLabel, QSpinBox, QCheckBox, QStatusBar, QGroupBox,
    QSizePolicy
)

from .log_handler import QtLogSignalEmitter, QtLogHandler
from .controller import ScraperController, ScraperConfig
from .robot_widget import RobotFaceWidget

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebScraper PRO – Hacker Control GUI")
        self.resize(1280, 760)

        # Central widget
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)

        # Top panel: Robot + Controls
        top_panel = QHBoxLayout()
        root_layout.addLayout(top_panel)

        # Robot face
        self.robot = RobotFaceWidget()
        self.robot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top_panel.addWidget(self.robot, 2)

        # Control box
        control_box = QGroupBox("Scraper Control")
        control_layout = QVBoxLayout(control_box)
        top_panel.addWidget(control_box, 3)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Start URLs (comma separated)")
        control_layout.addWidget(self._labeled("Start URLs", self.url_input))

        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 100)
        self.concurrency_spin.setValue(5)
        control_layout.addWidget(self._labeled("Concurrency", self.concurrency_spin))

        self.respect_robots_cb = QCheckBox("Respect robots.txt")
        self.respect_robots_cb.setChecked(True)
        control_layout.addWidget(self.respect_robots_cb)

        self.use_rl_cb = QCheckBox("Use Reinforcement Learning")
        control_layout.addWidget(self.use_rl_cb)

        self.hot_reload_cb = QCheckBox("Hot Reload Scrapers")
        control_layout.addWidget(self.hot_reload_cb)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶ Start")
        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        control_layout.addLayout(btn_row)

        self.status_label = QLabel("Status: IDLE")
        control_layout.addWidget(self.status_label)

        # Logs panel
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMinimumHeight(280)
        root_layout.addWidget(self._grouped("Real-Time Logs", self.log_edit))

        # Stats panel placeholder
        self.stats_edit = QTextEdit()
        self.stats_edit.setReadOnly(True)
        self.stats_edit.setMinimumHeight(160)
        root_layout.addWidget(self._grouped("Intelligence / Stats", self.stats_edit))

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Controller
        self.controller = ScraperController()

        # Logging emitter
        self.log_emitter = QtLogSignalEmitter()
        self.log_emitter.log_record.connect(self._append_log)

        # Attach logging handler (only once)
        self.qt_handler = QtLogHandler(self.log_emitter)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        self.qt_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.qt_handler)

        # Wire controller signals
        self.controller.status_changed.connect(self._on_status)
        self.controller.stats_update.connect(self._on_stats)
        self.controller.brain_activity.connect(self._on_brain_activity)

        # Connect buttons
        self.start_btn.clicked.connect(self._start)
        self.stop_btn.clicked.connect(self._stop)

        self._load_styles()

    def _labeled(self, label: str, widget: QWidget) -> QWidget:
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0,0,0,0)
        lab = QLabel(label)
        lab.setStyleSheet("color:#4dd0e1;font-weight:bold;")
        lay.addWidget(lab)
        lay.addWidget(widget)
        return box

    def _grouped(self, title: str, widget: QWidget) -> QGroupBox:
        box = QGroupBox(title)
        lay = QVBoxLayout(box)
        lay.addWidget(widget)
        return box

    def _load_styles(self):
        try:
            qss_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
            with open(qss_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except Exception:
            pass

    def _start(self):
        urls_text = self.url_input.text().strip()
        if not urls_text:
            self._append_log("WARNING", "GUI", "No URLs provided")
            return
        urls = [u.strip() for u in urls_text.split(',') if u.strip()]
        cfg = ScraperConfig(
            start_urls=urls,
            concurrency=self.concurrency_spin.value(),
            respect_robots=self.respect_robots_cb.isChecked(),
            use_rl=self.use_rl_cb.isChecked(),
            hot_reload=self.hot_reload_cb.isChecked(),
        )
        self.controller.start(cfg)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def _stop(self):
        self.controller.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _append_log(self, level: str, name: str, message: str):
        self.log_edit.append(f"<span style='color:#7ec9d9;'>[{level}]</span> <b>{name}</b>: {message}")
        self.log_edit.moveCursor(self.log_edit.textCursor().MoveOperation.End)

    def _on_status(self, status: str):
        self.status_label.setText(f"Status: {status}")
        self.status_bar.showMessage(f"Scraper status: {status}")

    def _on_stats(self, stats: dict):
        try:
            lines = []
            for k, v in stats.items():
                lines.append(f"{k}: {v}")
            self.stats_edit.setPlainText('\n'.join(lines))
        except Exception:
            pass

    def _on_brain_activity(self, value: float):
        self.robot.set_activity(value)


def run_gui():
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_gui()
