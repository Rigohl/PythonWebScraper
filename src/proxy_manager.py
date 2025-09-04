from __future__ import annotations

import random
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set


class ProxyManager:
    """Manage a pool of proxies with thread-safety and expiry handling.

    The manager keeps track of available, in-use and temporarily blocked
    proxies. All public methods are protected by an internal
    :class:`threading.Lock` to ensure safe access from multiple threads.
    """

    def __init__(self, proxies: Optional[List[str]] = None) -> None:
        """Initialize the manager.

        Args:
            proxies: Optional list of proxy strings to seed the pool.
        """
        self.proxies: List[str] = list(proxies or [])
        self.available_proxies: Set[str] = set(self.proxies)
        self.in_use_proxies: Set[str] = set()
        # Mapping of proxy -> UTC datetime when block expires
        self.blocked_proxies: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    def _now(self) -> datetime:
        """Return current UTC time. Separated for testability."""
        return datetime.now(timezone.utc)

    def _clean_blocked_proxies(self) -> None:
        """Remove expired entries from :attr:`blocked_proxies`.

        This method does not take the external lock; callers should hold
        ``self._lock`` when invoking it.
        """
        now = self._now()
        for proxy, expiry in list(self.blocked_proxies.items()):
            if now > expiry:
                self.blocked_proxies.pop(proxy, None)
                # Only return to available if it's known and not already in use
                if proxy in self.proxies and proxy not in self.in_use_proxies:
                    self.available_proxies.add(proxy)

    def get_proxy(self) -> Optional[str]:
        """Acquire an available proxy and mark it as in-use.

        Returns ``None`` if no proxy is currently available.
        """
        with self._lock:
            self._clean_blocked_proxies()
            if not self.available_proxies:
                return None

            proxy = random.choice(tuple(self.available_proxies))
            self.available_proxies.discard(proxy)
            self.in_use_proxies.add(proxy)
            return proxy

    def block_proxy(self, proxy: str, block_duration_seconds: int = 300) -> None:
        """Temporarily block ``proxy`` for ``block_duration_seconds`` seconds.

        If ``proxy`` is unknown (not in the original seed list) the call is
        a no-op. The proxy will be removed from both available and in-use
        pools if present.
        """
        if proxy not in self.proxies:
            return

        expiry = self._now() + timedelta(seconds=block_duration_seconds)
        with self._lock:
            self.available_proxies.discard(proxy)
            self.in_use_proxies.discard(proxy)
            self.blocked_proxies[proxy] = expiry

    def return_proxy(self, proxy: str) -> None:
        """Return a proxy to the available pool if it was in use.

        If the proxy is not part of the original seed list this is a no-op.
        """
        if proxy not in self.proxies:
            return

        with self._lock:
            if proxy in self.in_use_proxies:
                self.in_use_proxies.discard(proxy)
                # Only add to available if not currently blocked
                if proxy not in self.blocked_proxies:
                    self.available_proxies.add(proxy)
