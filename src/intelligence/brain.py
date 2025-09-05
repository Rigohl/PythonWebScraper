"""Adaptive learning Brain module for the scraper.

This component provides an incremental learning layer that captures
experience from each scraping cycle and updates lightweight heuristics
(which can later guide the RL agent, prioritisation, anomaly detection
or content extraction strategies).

Design Goals:
- Non-intrusive: Safe to enable/disable without breaking core flow.
- Lightweight: Pure Python + stdlib; no heavy ML dependencies here.
- Extensible: Data persisted in JSON so future models can be trained.
- Observable: Exposes metrics and adaptive signals consumable by orchestrator.

Core Concepts:
Experience Event: {
  "url": str,
  "status": str,              # SUCCESS / DUPLICATE / ERROR / RETRY
  "response_time": float|None,
  "content_length": int|None,
  "new_links": int|None,
  "timestamp": iso8601,
  "domain": str,
  "extracted_fields": int|None,
  "error_type": str|None
}

Heuristics maintained:
- domain_success_rate
- avg_content_length_per_domain
- link_yield_score (new_links / visits)
- error_type_frequency
- rolling_response_time_ms

Derived signals:
- domain_priority(domain): boost domains with higher success_rate * link_yield
- should_backoff(domain): if error ratio exceeds threshold in short window

Persistence:
- JSON state file at data/brain_state.json (configurable)

Thread Safety:
- Orchestrator interactions are async; Brain methods kept sync & cheap.
  If future contention arises, a simple asyncio.Lock can be added.
"""
from __future__ import annotations

import json
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Iterable, List, Optional

import logging

logger = logging.getLogger(__name__)

BRAIN_STATE_FILE = "data/brain_state.json"

@dataclass
class ExperienceEvent:
    url: str
    status: str
    response_time: Optional[float] = None
    content_length: Optional[int] = None
    new_links: Optional[int] = None
    timestamp: str = datetime.now(timezone.utc).isoformat()
    domain: Optional[str] = None
    extracted_fields: Optional[int] = None
    error_type: Optional[str] = None

class Brain:
    def __init__(self, state_file: str = BRAIN_STATE_FILE, max_recent: int = 500) -> None:
        self.state_file = state_file
        self.max_recent = max_recent
        self.recent_events: Deque[ExperienceEvent] = deque(maxlen=max_recent)
        self.domain_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "visits": 0,
            "success": 0,
            "errors": 0,
            "duplicates": 0,
            "total_new_links": 0,
            "total_content_length": 0,
            "extractions": 0,
            "response_time_sum": 0.0,
        })
        self.error_type_freq: Dict[str, int] = defaultdict(int)
        self._dirty = False
        self._load_state()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load_state(self) -> None:
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for ev in data.get("recent_events", [])[-self.max_recent:]:
                self.recent_events.append(ExperienceEvent(**ev))
            self.domain_stats.update(data.get("domain_stats", {}))
            self.error_type_freq.update(data.get("error_type_freq", {}))
            logger.info("Brain state loaded: %d recent events, %d domains", len(self.recent_events), len(self.domain_stats))
        except Exception as e:
            logger.warning(f"Could not load brain state: {e}")

    def _persist_state(self) -> None:
        if not self._dirty:
            return
        try:
            os.makedirs(os.path.dirname(self.state_file) or ".", exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "recent_events": [asdict(e) for e in self.recent_events],
                    "domain_stats": self.domain_stats,
                    "error_type_freq": self.error_type_freq,
                }, f, indent=2, ensure_ascii=False)
            self._dirty = False
        except Exception as e:
            logger.warning(f"Failed persisting brain state: {e}")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------
    def record_event(self, event: ExperienceEvent) -> None:
        self.recent_events.append(event)
        domain = event.domain or self._extract_domain(event.url)
        stats = self.domain_stats[domain]
        stats["visits"] += 1
        if event.status == "SUCCESS":
            stats["success"] += 1
        elif event.status == "ERROR":
            stats["errors"] += 1
        elif event.status == "DUPLICATE":
            stats["duplicates"] += 1
        if event.new_links:
            stats["total_new_links"] += event.new_links
        if event.content_length:
            stats["total_content_length"] += event.content_length
        if event.extracted_fields:
            stats["extractions"] += event.extracted_fields
        if event.response_time:
            stats["response_time_sum"] += event.response_time
        if event.error_type:
            self.error_type_freq[event.error_type] += 1
        self._dirty = True

    def flush(self) -> None:
        self._persist_state()

    # ------------------------------------------------------------------
    # Heuristic calculations
    # ------------------------------------------------------------------
    def domain_success_rate(self, domain: str) -> float:
        s = self.domain_stats.get(domain)
        if not s:
            return 0.0
        return s["success"] / s["visits"] if s["visits"] else 0.0

    def domain_error_rate(self, domain: str) -> float:
        s = self.domain_stats.get(domain)
        if not s:
            return 0.0
        return s["errors"] / s["visits"] if s["visits"] else 0.0

    def link_yield(self, domain: str) -> float:
        s = self.domain_stats.get(domain)
        if not s or not s["visits"]:
            return 0.0
        return s["total_new_links"] / s["visits"]

    def avg_content_length(self, domain: str) -> float:
        s = self.domain_stats.get(domain)
        if not s or not s["success"]:
            return 0.0
        return s["total_content_length"] / max(1, s["success"])

    def avg_response_time(self, domain: str) -> float:
        s = self.domain_stats.get(domain)
        if not s or not s["visits"]:
            return 0.0
        return s["response_time_sum"] / s["visits"]

    def domain_priority(self, domain: str) -> float:
        # Composite scoring; tunable weights
        return (self.domain_success_rate(domain) * 0.6 + self.link_yield(domain) * 0.4)

    def should_backoff(self, domain: str, error_threshold: float = 0.5, min_visits: int = 5) -> bool:
        s = self.domain_stats.get(domain)
        if not s or s["visits"] < min_visits:
            return False
        return self.domain_error_rate(domain) >= error_threshold

    def top_domains(self, limit: int = 5) -> List[str]:
        scored = [(self.domain_priority(d), d) for d in self.domain_stats.keys()]
        scored.sort(reverse=True)
        return [d for _, d in scored[:limit]]

    def recent_error_spike(self, domain: str, window: int = 20, spike_ratio: float = 0.6) -> bool:
        # Look at last N events for that domain
        errors = 0
        total = 0
        for ev in reversed(self.recent_events):
            if total >= window:
                break
            if (ev.domain or self._extract_domain(ev.url)) == domain:
                total += 1
                if ev.status == "ERROR":
                    errors += 1
        if total < 5:
            return False
        return (errors / total) >= spike_ratio

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def _extract_domain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return ""

    # Snapshot for external reporting
    def snapshot(self) -> Dict[str, Any]:
        return {
            "domains": self.domain_stats,
            "top_domains": self.top_domains(),
            "error_type_freq": self.error_type_freq,
            "recent_events": [asdict(e) for e in list(self.recent_events)[-20:]],
            "total_events": len(self.recent_events)
        }

__all__ = ["Brain", "ExperienceEvent"]
