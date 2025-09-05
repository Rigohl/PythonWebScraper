import os
import sys
import pytest

try:
    from PyQt6.QtWidgets import QApplication
except Exception:  # pragma: no cover
    pytest.skip("PyQt6 not available", allow_module_level=True)

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


def test_default_toggles(qapp):
    win = MainWindow()
    assert win.respect_robots_cb.isChecked() is False
    assert win.use_rl_cb.isChecked() is False
    assert win.hot_reload_cb.isChecked() is False
    win.close()
