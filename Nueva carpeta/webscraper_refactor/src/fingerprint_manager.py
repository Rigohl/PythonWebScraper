"""
Fingerprint management utilities for the scraper.

This module defines a ``FingerprintManager`` class responsible for generating
browser fingerprints that combine a user‑agent, screen resolution and a
handful of JavaScript navigator overrides.  The goal of the manager is to
rotate through a pool of User‑Agents while also randomising viewport sizes
and JS properties to make the underlying browser instance appear more like
a human-operated browser.

The original implementation bundled all logic in a single function.  This
rewrite introduces a small ``Fingerprint`` dataclass to represent the
generated fingerprint and allows injection of a custom random generator for
testability.  It also performs additional validation on constructor
arguments and exposes a method to update the viewport list at runtime.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

from src.user_agent_manager import UserAgentManager

# A predefined set of common screen resolutions.  These values are taken from
# public browser statistics and can be extended or replaced by consumers.
DEFAULT_VIEWPORTS: list[dict[str, int]] = [
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]


@dataclass(frozen=True)
class Fingerprint:
    """Represents a fully constructed browser fingerprint.

    Attributes:
        user_agent: The User‑Agent string to present.
        viewport: A mapping with ``width`` and ``height`` keys representing
            the viewport dimensions.
        js_overrides: A mapping of JavaScript property overrides to inject
            into the page context.
    """

    user_agent: str
    viewport: Dict[str, int]
    js_overrides: Dict[str, Any]


class FingerprintManager:
    """Generates realistic browser fingerprints for web scraping.

    ``FingerprintManager`` collaborates with a :class:`UserAgentManager` to
    rotate through a collection of User‑Agents.  It randomly selects one
    viewport from a supplied sequence, derives an appropriate platform string
    from the User‑Agent and constructs a set of JavaScript navigator
    overrides.  Consumers may supply their own random number generator via
    the ``rand`` argument for deterministic testing.
    """

    def __init__(self,
                 user_agent_manager: UserAgentManager,
                 viewports: Sequence[Dict[str, int]] | None = None,
                 rand: random.Random | None = None) -> None:
        if user_agent_manager is None:
            raise ValueError("Se debe proporcionar un UserAgentManager.")
        self.user_agent_manager = user_agent_manager

        # Use a copy of the default list to avoid accidental mutation.
        self.viewports: list[Dict[str, int]] = list(viewports) if viewports else list(DEFAULT_VIEWPORTS)
        if not self.viewports:
            raise ValueError("La lista de viewports no puede estar vacía.")

        # Allow dependency injection of a random generator for testability.
        self._random = rand if rand is not None else random.Random()

    def set_viewports(self, viewports: Iterable[Dict[str, int]]) -> None:
        """Replace the list of available viewports.

        This method validates that at least one viewport is provided and
        replaces the internal viewport list.  A copy of the provided
        sequence is stored to avoid external mutation.
        """
        vp_list = list(viewports)
        if not vp_list:
            raise ValueError("La lista de viewports no puede estar vacía.")
        self.viewports = vp_list

    def _platform_from_ua(self, user_agent: str) -> str:
        """Infer the ``navigator.platform`` value from a User‑Agent string."""
        ua_lower = user_agent.lower()
        if "windows" in ua_lower:
            return "Win32"
        if "macintosh" in ua_lower or "mac os" in ua_lower:
            return "MacIntel"
        if "linux" in ua_lower:
            return "Linux x86_64"
        if "iphone" in ua_lower or "ipad" in ua_lower:
            return "iPhone"
        if "android" in ua_lower:
            return "Linux armv8l"
        return "Win32"

    def get_fingerprint(self) -> Fingerprint:
        """Return a new :class:`Fingerprint` with randomised values.

        The method obtains the next available User‑Agent from the underlying
        :class:`UserAgentManager`, selects a viewport at random using the
        injected random generator and constructs a set of JavaScript
        overrides that make the browser appear less like an automated tool.

        Returns:
            Fingerprint: a dataclass instance containing the chosen
                User‑Agent, viewport and JS overrides.
        """
        user_agent = self.user_agent_manager.get_user_agent()
        viewport = self._random.choice(self.viewports)
        platform = self._platform_from_ua(user_agent)

        js_overrides = {
            "navigator.webdriver": False,
            # Provide languages as a Python list literal for injection.
            "navigator.languages": "['en-US', 'en']",
            "navigator.platform": f"'{platform}'",
            "navigator.plugins.length": 0,
            "screen.colorDepth": 24,
            "navigator.hardwareConcurrency": self._random.choice([4, 8, 16]),
            "navigator.deviceMemory": self._random.choice([4, 8]),
        }

        return Fingerprint(user_agent=user_agent, viewport=viewport, js_overrides=js_overrides)