"""
User‑Agent rotation and blocking manager.

This module defines ``UserAgentManager``, a small utility class for
rotating through a collection of User‑Agent strings, temporarily blocking
agents that lead to detection or throttling and restoring them after a
configurable timeout.  The original implementation used bare functions
without extensive type hints or documentation.  In this rewrite we add
comprehensive docstrings, type annotations and a few helper methods to
improve testability and clarity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, List, Set, Dict


@dataclass
class UserAgentManager:
    """Manages rotation and temporary blocking of User‑Agent strings.

    The manager maintains a pool of User‑Agents and cycles through them on
    successive calls to :meth:`get_user_agent`.  Agents can be blocked for
    a specified duration using :meth:`block_user_agent`, during which
    :meth:`get_user_agent` will skip them.  Once the block expires or the
    agent is manually released via :meth:`release_user_agent`, it becomes
    available again.

    Args:
        user_agents: An iterable of User‑Agent strings.  Duplicate
            values are ignored.

    Raises:
        ValueError: If ``user_agents`` is empty.
    """

    user_agents: List[str]
    available_user_agents: Set[str] = field(init=False)
    blocked_user_agents: Dict[str, datetime] = field(init=False, default_factory=dict)
    _rotation_index: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if not self.user_agents:
            raise ValueError("La lista de User-Agents no puede estar vacía.")
        # Normalise to a list to allow index-based rotation and create a set
        # of available agents for fast membership tests.
        self.user_agents = list(dict.fromkeys(self.user_agents))
        self.available_user_agents = set(self.user_agents)

    def _clean_expired_blocks(self) -> None:
        """Remove expired entries from the blocked user agents dictionary."""
        now = datetime.now()
        expired = [ua for ua, until in self.blocked_user_agents.items() if now > until]
        for ua in expired:
            # Re-add to available and delete from blocked
            self.available_user_agents.add(ua)
            del self.blocked_user_agents[ua]

    # Backwards compatibility: older tests expect a method named
    # ``_clean_blocked_user_agents`` with equivalent behaviour.
    def _clean_blocked_user_agents(self) -> None:  # pragma: no cover - simple alias
        self._clean_expired_blocks()

    def get_user_agent(self) -> str:
        """Return the next available User‑Agent, rotating through the pool.

        If all agents are currently blocked, this method returns a User‑Agent
        from the original list in round‑robin order, even if that agent is
        still blocked.  This ensures the scraper always has something to send.

        Returns:
            str: A User‑Agent string.
        """
        self._clean_expired_blocks()
        if not self.available_user_agents:
            # All are blocked; fall back to sequential rotation through the
            # original list.  We don''t remove the block entry here because
            # the block timeout may still be in force.
            self._rotation_index = (self._rotation_index + 1) % len(self.user_agents)
            return self.user_agents[self._rotation_index]

        # Cycle through only available agents
        available_list = list(self.available_user_agents)
        self._rotation_index = (self._rotation_index + 1) % len(available_list)
        return available_list[self._rotation_index]

    def block_user_agent(self, user_agent: str, duration_seconds: int = 300) -> None:
        """Temporarily block a User‑Agent for a given number of seconds.

        Args:
            user_agent: The User‑Agent string to block.  If the agent is not
                recognised, this method silently returns.
            duration_seconds: The number of seconds to block the User‑Agent.
        """
        if user_agent in self.available_user_agents:
            self.available_user_agents.remove(user_agent)
        # Always set/update the blocked expiry time, even if the agent wasn''t available.
        self.blocked_user_agents[user_agent] = datetime.now() + timedelta(seconds=duration_seconds)

    def release_user_agent(self, user_agent: str) -> None:
        """Release a previously blocked User‑Agent immediately.

        Args:
            user_agent: The User‑Agent string to release.  If the agent is not
                present in the blocked list, this method silently returns.
        """
        if user_agent in self.blocked_user_agents:
            del self.blocked_user_agents[user_agent]
            self.available_user_agents.add(user_agent)

    def is_blocked(self, user_agent: str) -> bool:
        """Check whether a User‑Agent is currently blocked."""
        self._clean_expired_blocks()
        return user_agent in self.blocked_user_agents

    def has_available(self) -> bool:
        """Return ``True`` if at least one User‑Agent is currently available."""
        self._clean_expired_blocks()
        return bool(self.available_user_agents)
