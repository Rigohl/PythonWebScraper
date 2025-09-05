"""Hot reloading functionality for scraper modules."""

import asyncio
import importlib
import logging
import os
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

logger = logging.getLogger(__name__)

class ScraperReloader(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.last_reload: Dict[str, float] = {}
        self.debounce_seconds = 1.0  # Prevent multiple reloads for the same file

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return
            
        if not event.src_path.endswith('.py'):
            return

        # Convert to module path
        file_path = os.path.abspath(event.src_path)
        if not any(p in file_path for p in ['src/scrapers', 'src\\scrapers']):
            return

        # Debounce check
        current_time = time.time()
        if file_path in self.last_reload and \
           current_time - self.last_reload[file_path] < self.debounce_seconds:
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
        module_dir = os.path.dirname(module_path)
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        module_name = os.path.splitext(os.path.basename(module_path))[0]
        
        # Find loaded module
        loaded_module = None
        for name, module in sys.modules.items():
            if name.endswith(module_name):
                loaded_module = module
                break

        if loaded_module:
            importlib.reload(loaded_module)
            logger.info(f"Successfully reloaded module: {module_name}")
            return True
        else:
            logger.warning(f"Module not found in sys.modules: {module_name}")
            return False

    except Exception as e:
        logger.error(f"Error reloading module {module_path}: {e}")
        return False