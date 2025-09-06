"""Fingerprint management utilities for the scraper.

This module provides :class:`FingerprintManager` which composes a
:class:`UserAgentManager` with viewport and JS overrides to construct a
realistic browser fingerprint. The manager is safe for concurrent use.
"""

from __future__ import annotations

import random
import threading
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

from .user_agent_manager import UserAgentManager

# Common screen resolutions (copy to avoid accidental mutation elsewhere)
DEFAULT_VIEWPORTS: List[Dict[str, int]] = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]


@dataclass(frozen=True)
class Fingerprint:
    """A constructed browser fingerprint.

    Attributes:
        user_agent: User-Agent string.
        viewport: Mapping with ``width`` and ``height`` keys.
        js_overrides: Mapping of JS properties to inject.
    """

    user_agent: str
    viewport: Dict[str, int]
    js_overrides: Dict[str, Any]


class FingerprintManager:
    """Generate realistic fingerprints using a :class:`UserAgentManager`.

    The class accepts an optional sequence of viewports and an optional
    random generator for deterministic testing.
    """

    def __init__(
        self,
        user_agent_manager: UserAgentManager,
        viewports: Sequence[Dict[str, int]] | None = None,
        rand: random.Random | None = None,
    ) -> None:
        if user_agent_manager is None:
            raise ValueError("Se debe proporcionar un UserAgentManager.")

        self.user_agent_manager = user_agent_manager
        self.viewports: List[Dict[str, int]] = (
            list(viewports) if viewports is not None else list(DEFAULT_VIEWPORTS)
        )
        if not self.viewports:
            raise ValueError("La lista de viewports no puede estar vacía.")

        self._random = rand if rand is not None else random.Random()
        self._lock = threading.Lock()

    def set_viewports(self, viewports: Iterable[Dict[str, int]]) -> None:
        """Replace the internal viewport list with a copy of ``viewports``."""
        vp_list = list(viewports)
        if not vp_list:
            raise ValueError("La lista de viewports no puede estar vacía.")
        with self._lock:
            self.viewports = vp_list

    def _platform_from_ua(self, user_agent: str) -> str:
        """Infer a plausible ``navigator.platform`` from the User-Agent string."""
        ua_lower = (user_agent or "").lower()
        if "windows" in ua_lower:
            return "Win32"
        if "macintosh" in ua_lower or "mac os" in ua_lower:
            return "MacIntel"
        if "android" in ua_lower:
            return "Linux armv8l"
        if "linux" in ua_lower:
            return "Linux x86_64"
        if "iphone" in ua_lower or "ipad" in ua_lower:
            return "iPhone"
        return "Win32"

    def get_fingerprint(self) -> Fingerprint:
        """Construct and return a new Fingerprint.

        This method acquires a lock to ensure consistent selection of
        viewport and the call to the underlying :meth:`UserAgentManager`.
        """
        with self._lock:
            user_agent = self.user_agent_manager.get_user_agent()
            viewport = self._random.choice(self.viewports)
            platform = self._platform_from_ua(user_agent)

            js_overrides: Dict[str, Any] = {
                "navigator.webdriver": False,
                "navigator.languages": "['en-US', 'en']",
                "navigator.platform": f'"{platform}"',
                "navigator.plugins.length": 0,
                "screen.colorDepth": 24,
                "navigator.hardwareConcurrency": self._random.choice([4, 8, 16]),
                "navigator.deviceMemory": self._random.choice([4, 8]),
            }

            return Fingerprint(
                user_agent=user_agent, viewport=viewport, js_overrides=js_overrides
            )
