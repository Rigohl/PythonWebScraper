"""
Simple metrics collector used by tests and GUI.
Collects per-URL stats and writes summary to data/brain_state.json so the "brain" can access it.
"""

import json
import os
from typing import Any


class MetricsCollector:
    def __init__(self, storage_path: str = "data/brain_state.json"):
        self.storage_path = storage_path
        self.metrics = {"total": 0, "success": 0, "errors": 0, "last_results": []}

    def record(self, result: dict[str, Any]):
        self.metrics["total"] += 1
        if result.get("status") == 200:
            self.metrics["success"] += 1
        else:
            self.metrics["errors"] += 1

        self.metrics["last_results"].append(result)
        # keep only last 50
        self.metrics["last_results"] = self.metrics["last_results"][-50:]
        self._persist()

    def _persist(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.metrics, f, indent=2)
        except Exception:
            pass

    def snapshot(self) -> dict[str, Any]:
        return self.metrics.copy()
