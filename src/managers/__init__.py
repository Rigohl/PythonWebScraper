"""Compatibility package for legacy import path `src.managers.*`."""

from .user_agent_manager import UserAgentManager  # noqa: F401

__all__ = ["UserAgentManager"]
from ..user_agent_manager import UserAgentManager  # legacy path support
