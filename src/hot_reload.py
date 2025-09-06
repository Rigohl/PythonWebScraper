"""Hot reloading functionality for scraper modules."""

import importlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class ScraperReloader(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.last_reload: Dict[str, float] = {}
        self.debounce_seconds = 1.0  # Prevent multiple reloads for the same file

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return

        if not event.src_path.endswith(".py"):
            return

        # Convert to module path
        file_path = os.path.abspath(event.src_path)
        if not any(p in file_path for p in ["src/scrapers", "src\\scrapers"]):
            return

        # Debounce check
        current_time = time.time()
        if (
            file_path in self.last_reload
            and current_time - self.last_reload[file_path] < self.debounce_seconds
        ):
            return

        self.last_reload[file_path] = current_time
        self.callback(file_path)


class HotReloader:
    def __init__(self, scrapers_dir: str):
        self.scrapers_dir = Path(scrapers_dir)
        self.observer: Optional[Observer] = None
        self._running = False

    def start(self, callback: Callable[[str], None]):
        """Start watching for changes in scraper modules."""
        if self._running:
            return

        self._running = True
        self.observer = Observer()
        handler = ScraperReloader(callback)
        self.observer.schedule(handler, str(self.scrapers_dir), recursive=True)
        self.observer.start()
        logger.info(f"Hot reloader watching directory: {self.scrapers_dir}")

    def stop(self):
        """Stop watching for changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self._running = False


def reload_module(module_path: str) -> bool:
    """
    Reload a Python module by its file path.
    Returns True if reload was successful.
    """
    try:
        # Convert file path to module name
        module_path = os.path.abspath(module_path)
        src_index = module_path.find("src")
        if src_index == -1:
            logger.warning(f"Not a src module: {module_path}")
            return False

        # Convert to proper module path
        module_name = module_path[src_index:].replace(os.sep, ".").replace(".py", "")

        # Force reload all related modules
        for name in list(sys.modules.keys()):
            if name.startswith(module_name):
                del sys.modules[name]

        # Import and reload
        try:
            module = importlib.import_module(module_name)
            importlib.reload(module)
            logger.info(f"Successfully reloaded module: {module_name}")
            return True
        except ImportError:
            logger.warning(f"Could not import module: {module_name}")
            return False

    except Exception as e:
        logger.error(f"Error reloading module {module_path}: {e}")
        return False
