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
- SQLite database at data/brain.db for structured data
- JSON config at data/brain_config.json for settings
- Thread-safe with automatic migrations

Thread Safety:
- Uses BrainPersistence layer for safe concurrent access
"""

from __future__ import annotations

import logging
import os
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import the new persistence layer
from .brain_persistence import BrainPersistence

# Default file paths for persistence
BRAIN_DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "brain.db")
BRAIN_CONFIG_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "brain_config.json"
)
BRAIN_STATE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "brain_state.json"
)
# Ensure BRAIN_STATE_FILE is always available
try:
    BRAIN_STATE_FILE
except NameError:
    BRAIN_STATE_FILE = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "brain_state.json"
    )


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
    def __init__(
        self,
        db_path: str = BRAIN_DB_FILE,
        config_path: str = BRAIN_CONFIG_FILE,
        state_file: Optional[str] = None,
        max_recent: int = 500,
        **kwargs,
    ) -> None:
        # Backwards compatibility: allow callers to pass `state_file` keyword (used by HybridBrain/tests)
        self.state_file = state_file or BRAIN_STATE_FILE
        self.persistence = BrainPersistence(db_path, config_path)
        self.max_recent = max_recent
        self.recent_events: Deque[ExperienceEvent] = deque(maxlen=max_recent)
        self.domain_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "visits": 0,
                "success": 0,
                "errors": 0,
                "duplicates": 0,
                "total_new_links": 0,
                "total_content_length": 0,
                "extractions": 0,
                "response_time_sum": 0.0,
            }
        )
        self.error_type_freq: Dict[str, int] = defaultdict(int)
        self._dirty = False
        self._load_state()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load_state(self) -> None:
        """Load brain state from persistence layer."""
        try:
            # Load recent events from SQLite
            recent_events_data = self.persistence.load_recent_events(self.max_recent)
            for event_data in recent_events_data:
                self.recent_events.append(ExperienceEvent(**event_data))

            # Load domain stats from SQLite
            self.domain_stats.update(self.persistence.load_domain_stats())

            # Load error frequencies from SQLite
            self.error_type_freq.update(self.persistence.load_error_frequencies())

            logger.info(
                "Brain state loaded: %d recent events, %d domains",
                len(self.recent_events),
                len(self.domain_stats),
            )
        except Exception as e:
            logger.warning(f"Could not load brain state: {e}")

    def _persist_state(self) -> None:
        """Persist brain state using the persistence layer."""
        if not self._dirty:
            return
        try:
            # Persist recent events
            for event in self.recent_events:
                self.persistence.save_event(asdict(event))

            # Persist domain stats
            for domain, stats in self.domain_stats.items():
                self.persistence.update_domain_stats(domain, stats)

            # Persist error frequencies
            for error_type, freq in self.error_type_freq.items():
                self.persistence.update_error_frequency(error_type, freq)

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
        """Flush pending changes to persistence layer."""
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
        return self.domain_success_rate(domain) * 0.6 + self.link_yield(domain) * 0.4

    def should_backoff(
        self, domain: str, error_threshold: float = 0.5, min_visits: int = 5
    ) -> bool:
        s = self.domain_stats.get(domain)
        if not s or s["visits"] < min_visits:
            return False
        return self.domain_error_rate(domain) >= error_threshold

    def top_domains(self, limit: int = 5) -> List[str]:
        scored = [(self.domain_priority(d), d) for d in self.domain_stats.keys()]
        scored.sort(reverse=True)
        return [d for _, d in scored[:limit]]

    def recent_error_spike(
        self, domain: str, window: int = 20, spike_ratio: float = 0.6
    ) -> bool:
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
            "total_events": len(self.recent_events),
        }


__all__ = ["Brain", "ExperienceEvent"]
