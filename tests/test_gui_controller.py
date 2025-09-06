import asyncio
import time

from PyQt6.QtCore import QCoreApplication

from src.gui.controller import ScraperConfig, ScraperController


async def _dummy_runner(**kwargs):
    # Simulate periodic stats callbacks
    stats_cb = kwargs.get("stats_callback")
    if stats_cb:
        for i in range(3):
            await asyncio.sleep(0.01)
            await stats_cb({"pages_crawled": i, "brain": {"events_last_minute": i}})


def test_controller_signals():
    app = QCoreApplication.instance() or QCoreApplication([])

    # Inject dummy runner
    controller = ScraperController(runner=_dummy_runner)

    received = {"status": [], "stats": [], "activity": []}

    def on_status(s):
        received["status"].append(s)

    def on_stats(d):
        received["stats"].append(d)

    def on_activity(v):
        received["activity"].append(v)

    controller.status_changed.connect(on_status)
    controller.stats_update.connect(on_stats)
    controller.brain_activity.connect(on_activity)

    cfg = ScraperConfig(start_urls=["http://example.com"])

    controller.start(cfg)

    # Wait for the thread to run and emit signals
    timeout = time.time() + 2.0
    while time.time() < timeout and len(received["stats"]) < 3:
        app.processEvents()
        time.sleep(0.01)

    controller.stop()

    assert "RUNNING" in received["status"]
    assert "STOPPED" in received["status"]
    assert len(received["stats"]) >= 3
    assert len(received["activity"]) >= 1
