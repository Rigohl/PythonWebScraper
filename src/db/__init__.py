"""Compatibility package for legacy import path `src.db.database`.

Provides re-export of `DatabaseManager` from the refactored flat module
`src.database` so older tests/imports keep functioning.
"""

from ..database import DatabaseManager  # re-export

__all__ = ["DatabaseManager"]
from ..database import DatabaseManager  # re-export for legacy path
