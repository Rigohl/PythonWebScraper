"""
Web scraper minimal placeholder used by GUI/tests
Supports queuing multiple URLs and executing a single one at a time via SequentialProcessor
"""

import time
from collections.abc import Callable
from typing import Any


def scrape_url(url: str, timeout: float = 1.0) -> dict[str, Any]:
    """Simulate scraping a URL. Returns a result dict.

    This is intentionally lightweight for tests: sleeps briefly and returns
    synthetic content and status.
    """
    # simulate network / processing
    time.sleep(timeout)
    return {
        "url": url,
        "status": 200,
        "content_length": len(url) * 10,
        "timestamp": time.time(),
    }


def scrape_batch(
    urls: list[str], on_result: Callable[[dict[str, Any]], None] | None = None
):
    """Scrape a list of URLs sequentially, calling on_result for each result."""
    results = []
    for u in urls:
        r = scrape_url(u)
        results.append(r)
        if on_result:
            try:
                on_result(r)
            except Exception:
                pass
    return results
