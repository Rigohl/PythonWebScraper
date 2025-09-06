#!/usr/bin/env python
"""Wrapper to call scripts/generate_metrics.py from tools/ path.
This preserves CLI and exit codes but provides the expected path used by tests.
"""
import runpy
import sys

if __name__ == "__main__":
    try:
        runpy.run_path("scripts/generate_metrics.py", run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        sys.exit(code)
    except (ImportError, FileNotFoundError, RuntimeError, OSError) as e:
        print(f"Error running generate_metrics.py: {e}", file=sys.stderr)
        # If an unexpected exception occurs, return non-zero
        sys.exit(1)
    sys.exit(0)
