"""Compatibility bridge for legacy import path `src.managers.user_agent_manager`.

Re-exports `UserAgentManager` from the refactored top-level module
`src.user_agent_manager`.
"""

from ..user_agent_manager import UserAgentManager  # noqa: F401

__all__ = ["UserAgentManager"]
from ..user_agent_manager import *  # noqa: F401,F403
