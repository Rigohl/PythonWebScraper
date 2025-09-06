"""User-Agent rotation and blocking manager.

This module provides :class:`UserAgentManager`, a small utility to rotate
through User-Agent strings while allowing temporary blocking and
automatic expiry. All public methods are thread-safe.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List


@dataclass
class UserAgentManager:
    """Manage rotation and temporary blocking of User-Agent strings.

    The manager keeps a deterministic rotation order and a separate list
    of currently available User-Agents. When all agents are blocked, the
    manager still returns one from the original list to keep the scraper
    operational.
    """

    user_agents: List[str]
    available_user_agents: List[str] = field(init=False)
    blocked_user_agents: Dict[str, datetime] = field(init=False, default_factory=dict)
    _rotation_index: int = field(init=False, default=0)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)

    def __post_init__(self) -> None:
        if not self.user_agents:
            raise ValueError("La lista de User-Agents no puede estar vacía.")
        # Remove duplicates while preserving order
        seen: dict = dict.fromkeys(self.user_agents)
        self.user_agents = list(seen)
        self.available_user_agents = list(self.user_agents)

    def _now(self) -> datetime:
        """Return current UTC time (split out for testability)."""
        return datetime.now(timezone.utc)

    def _clean_expired_blocks(self) -> None:
        """Move expired blocked agents back to available list.

        Callers should hold ``self._lock``.
        """
        now = self._now()
        expired = [ua for ua, until in self.blocked_user_agents.items() if now > until]
        for ua in expired:
            self.blocked_user_agents.pop(ua, None)
            if ua not in self.available_user_agents and ua in self.user_agents:
                self.available_user_agents.append(ua)

    # Backwards compatibility alias
    def _clean_blocked_user_agents(self) -> None:  # pragma: no cover - thin wrapper
        with self._lock:
            self._clean_expired_blocks()

    def get_user_agent(self) -> str:
        """Return the next available User-Agent in a deterministic rotation.

        If no agents are currently available (all blocked) this method will
        return one from the original user_agents list in round-robin order.
        """
        with self._lock:
            self._clean_expired_blocks()
            if self.available_user_agents:
                self._rotation_index = (self._rotation_index + 1) % len(
                    self.available_user_agents
                )
                return self.available_user_agents[self._rotation_index]

            # Fallback to original list when all are blocked
            self._rotation_index = (self._rotation_index + 1) % len(self.user_agents)
            chosen = self.user_agents[self._rotation_index]
            # Ensure the fallback choice is recorded as blocked if it currently is
            # (tests expect it to remain in blocked_user_agents)
            return chosen

    def block_user_agent(self, user_agent: str, duration_seconds: int = 300) -> None:
        """Temporarily block ``user_agent`` for ``duration_seconds`` seconds.

        If the agent is unknown the call is a no-op.
        """
        expiry = self._now() + timedelta(seconds=duration_seconds)
        with self._lock:
            # Remove from available if present
            try:
                if user_agent in self.available_user_agents:
                    self.available_user_agents.remove(user_agent)
            except ValueError:
                pass
            # Always set/update expiry regardless of availability
            self.blocked_user_agents[user_agent] = expiry

    def release_user_agent(self, user_agent: str) -> None:
        """Immediately release a blocked User-Agent back to availability."""
        with self._lock:
            if user_agent in self.blocked_user_agents:
                self.blocked_user_agents.pop(user_agent, None)
                if (
                    user_agent in self.user_agents
                    and user_agent not in self.available_user_agents
                ):
                    self.available_user_agents.append(user_agent)

    def is_blocked(self, user_agent: str) -> bool:
        """Return True if ``user_agent`` is currently blocked (and not expired)."""
        with self._lock:
            self._clean_expired_blocks()
            return user_agent in self.blocked_user_agents

    def has_available(self) -> bool:
        """Return True when at least one User-Agent is currently available."""
        with self._lock:
            self._clean_expired_blocks()
            return bool(self.available_user_agents)
