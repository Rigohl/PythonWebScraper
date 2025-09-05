import os
import sys
import pytest

# Skip tests if PyQt6 not installed (CI environments without GUI libs)
try:
    from PyQt6.QtWidgets import QApplication
except Exception:  # pragma: no cover
    pytest.skip("PyQt6 not available", allow_module_level=True)

# Ensure src is in path
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(ROOT)
SRC = os.path.join(PROJECT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from gui.app import MainWindow  # type: ignore

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_mainwindow_instantiation(qapp):
    win = MainWindow()
    assert win.windowTitle().startswith("WebScraper PRO")
    assert win.concurrency_spin.value() == 5
    assert win.respect_robots_cb.isChecked() is False  # default OFF
    assert win.use_rl_cb.isChecked() is False
    win.close()


def test_controls_exist(qapp):
    win = MainWindow()
    assert win.start_btn.isEnabled() is True
    assert win.stop_btn.isEnabled() is False
    assert win.log_edit.toPlainText() == ""
    win.close()
