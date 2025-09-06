#!/usr/bin/env python
"""Wrapper to call scripts/check_drift.py from tools/ path."""
import runpy
import sys

if __name__ == "__main__":
    try:
        runpy.run_path("scripts/check_drift.py", run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        sys.exit(code)
    except (ImportError, FileNotFoundError, RuntimeError, OSError) as e:
        print(f"Error running check_drift.py: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
