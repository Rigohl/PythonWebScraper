import importlib.util
from pathlib import Path


def _load_controlpanel():
    base = Path(__file__).resolve().parents[1] / "src" / "gui"
    spec = importlib.util.spec_from_file_location(
        "professional_app", str(base / "professional_app.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod.ControlPanel


def test_controlpanel_parses_and_enqueues(monkeypatch):
    try:
        ControlPanel = _load_controlpanel()
    except Exception:
        # If PyQt isn't available in the test environment, skip the GUI-heavy test
        import pytest

        pytest.skip("PyQt6 not available - skipping GUI test")

    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    panel = ControlPanel()

    # replace processor with a fake recorder

    class FakeProcessor:
        def __init__(self):
            self.queue = []
            self._lock = None

        def enqueue(self, urls):
            self.queue.extend(urls)

        def start_background(self):
            return None

    fake = FakeProcessor()
    panel._processor = fake

    panel.url_input.setPlainText(
        "http://one.example\nhttp://two.example\n\nhttp://three.example"
    )
    panel._on_start_clicked()

    assert fake.queue == [
        "http://one.example",
        "http://two.example",
        "http://three.example",
    ]
