"""Compatibility bridge for legacy import path `src.intelligence.rl_agent`.

Re-exports `RLAgent` from the refactored top-level module `src.rl_agent`.
Tests patching this path (e.g. for mocks) will now locate this module.
"""

from ..rl_agent import RLAgent  # noqa: F401

__all__ = ["RLAgent"]
from ..rl_agent import *  # noqa: F401,F403
