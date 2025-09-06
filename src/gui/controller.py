import asyncio
import logging
import os
import sys
import threading
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

# Changed from relative to absolute import for better compatibility with tests
# Add the src directory to the path if it's not already there
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import the runner function with proper absolute import
from src.runner import run_crawler

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    start_urls: List[str] = field(default_factory=list)
    db_path: str = "data/scraper_database.db"
    concurrency: int = 5
    respect_robots: bool = True
    use_rl: bool = False
    hot_reload: bool = False


class ScraperController(QObject):
    # Signals for GUI updates
    status_changed = pyqtSignal(str)
    stats_update = pyqtSignal(dict)
    brain_activity = pyqtSignal(float)

    def __init__(self, runner: Optional[Callable[..., object]] = None):
        """Create a new controller.

        Parameters
        ----------
        runner:
            Optional async callable matching the signature of `run_crawler`.
            If None the real `run_crawler` from `src.runner` will be used. This
            allows injecting a dummy runner in tests.
        """
        super().__init__()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        self._config = ScraperConfig()
        # Runner injection for testability
        self._runner = runner or run_crawler

    def is_running(self) -> bool:
        return self._running

    def start(self, config: ScraperConfig):
        if self._running:
            return
        self._config = config
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        self._thread.start()
        self._running = True
        self.status_changed.emit("RUNNING")

    def stop(self):
        if not self._running:
            return
        self._stop_event.set()
        # Cancel tasks gracefully via loop call_soon_threadsafe
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._running = False
        # Emit STOPPED and wait shortly for the background thread to finish so
        # that tests observing the signal can receive it reliably.
        self.status_changed.emit("STOPPED")
        try:
            if self._thread and self._thread.is_alive():
                # join with a small timeout to avoid blocking long-running runs
                self._thread.join(timeout=0.5)
        except Exception:
            pass

    def _thread_main(self):
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._run())
        except Exception as e:
            logger.error(f"Scraper thread crashed: {e}")
        finally:
            if self._loop and self._loop.is_running():
                self._loop.stop()
            self._loop = None
            self._running = False
            self.status_changed.emit("STOPPED")

    async def _run(self):
        if not self._config.start_urls:
            logger.warning("No start URLs provided - idle mode")
            return

        async def stats_callback(stats: dict):
            self.stats_update.emit(stats)
            # Derive a numeric brain activity metric if available
            activity = 0.0
            if "brain" in stats:
                b = stats["brain"]
                activity = float(b.get("events_last_minute", 0)) / 50.0
            self.brain_activity.emit(min(1.0, activity))

        await self._runner(
            start_urls=self._config.start_urls,
            db_path=self._config.db_path,
            concurrency=self._config.concurrency,
            respect_robots_txt=self._config.respect_robots,
            use_rl=self._config.use_rl,
            hot_reload=self._config.hot_reload,
            stats_callback=stats_callback,
        )
