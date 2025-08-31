"""Compatibility bridge for legacy import path `src.db.database`.

Re-exports `DatabaseManager` from `src.database`.
"""

from ..database import DatabaseManager  # noqa: F401

__all__ = ["DatabaseManager"]
from ..database import *  # noqa: F401,F403
