"""
Sequential processor that accepts multiple URLs and runs scraping one at a time.
It calls a MetricsCollector for each result so metrics are persisted for the "brain".
"""

from __future__ import annotations

import threading
import time

try:
    from .metrics_collector import MetricsCollector
    from .web_scraper import scrape_url
except Exception:
    # allow running as a module loaded from tests (no package context)
    import importlib.util
    import pathlib

    base = pathlib.Path(__file__).resolve().parent

    def _load(name, fname):
        spec = importlib.util.spec_from_file_location(name, str(base / fname))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # type: ignore
        return m

    _mc = _load("metrics_collector", "metrics_collector.py")
    _ws = _load("web_scraper", "web_scraper.py")
    MetricsCollector = _mc.MetricsCollector
    scrape_url = _ws.scrape_url


class SequentialProcessor:
    def __init__(self, collector: MetricsCollector | None = None):
        self.queue: list[str] = []
        self._lock = threading.Lock()
        self._running = False
        self.collector = collector or MetricsCollector()

    def enqueue(self, urls: list[str]):
        with self._lock:
            self.queue.extend(urls)

    def run_once(self):
        """Run a single item from the queue if present."""
        url = None
        with self._lock:
            if self.queue:
                url = self.queue.pop(0)

        if url is None:
            return None

        result = scrape_url(url)
        # record metrics
        try:
            self.collector.record(result)
        except Exception:
            pass

        return result

    def run(self):
        """Run continuously until the queue is empty. Non-blocking wrapper can call this in a thread."""
        if self._running:
            return
        self._running = True
        try:
            while True:
                with self._lock:
                    if not self.queue:
                        break
                self.run_once()
                # small pause to avoid tight loop
                time.sleep(0.05)
        finally:
            self._running = False

    def start_background(self) -> threading.Thread:
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t
