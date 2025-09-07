"""Auto push manager: count files and push when threshold reached.

Safe by default: runs pre-commit and pytest for experimental tests before pushing.
To enable real pushes either run with --enable or set AUTO_PUSH_ENABLE=1 in env.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COUNTER_FILE = REPO_ROOT / ".auto_push_counter"
PROTECTED = {"main", "master", "develop"}
DEFAULT_THRESHOLD = int(os.getenv("AUTO_PUSH_THRESHOLD", "10"))
AUTO_PUSH_ENABLE = os.getenv("AUTO_PUSH_ENABLE", "0") in ("1", "true", "True")


def run(cmd: list[str], cwd: Path | None = None, capture: bool = False):
    if capture:
        return subprocess.check_output(cmd, cwd=cwd or REPO_ROOT, text=True).strip()
    subprocess.check_call(cmd, cwd=cwd or REPO_ROOT)


def get_branch() -> str:
    try:
        return run(["git", "symbolic-ref", "--short", "HEAD"], capture=True)
    except Exception:
        return run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)


def files_in_last_commit() -> list[str]:
    try:
        out = run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], capture=True)
        return [p for p in out.splitlines() if p]
    except Exception:
        out = run(["git", "diff", "--name-only", "--cached"], capture=True)
        return [p for p in out.splitlines() if p]


def read_counter() -> int:
    try:
        return int(COUNTER_FILE.read_text())
    except Exception:
        return 0


def write_counter(v: int) -> None:
    COUNTER_FILE.write_text(str(int(v)))


def push_changes(branch: str, dry_run: bool):
    if dry_run:
        print(f"[DRY] Would push branch {branch} to origin")
        return
    print(f"Pushing branch {branch} to origin...")
    run(["git", "push", "-u", "origin", branch])
    print("Push complete.")


def main(argv: list[str] | None = None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="No push, only simulate")
    p.add_argument("--enable", action="store_true", help="Allow real push")
    p.add_argument(
        "--threshold", type=int, default=DEFAULT_THRESHOLD, help="Files threshold"
    )
    args = p.parse_args(argv)

    dry_run = args.dry_run
    enable_push = args.enable or AUTO_PUSH_ENABLE

    branch = get_branch()
    if branch in PROTECTED:
        print(f"[SKIP] Branch '{branch}' is protected. No automatic push.")
        return 0

    files = files_in_last_commit()
    delta = len(files)
    print(f"Files in last commit: {delta}")
    counter = read_counter()
    counter += delta
    print(f"Accumulated counter: {counter} (threshold={args.threshold})")

    if counter >= args.threshold:
        print("Threshold reached. Running checks...")
        try:
            # Normalize separators and restrict to tracked python files
            normalized = [f.replace("\\", "/") for f in files if f]
            # Only run pre-commit on .py files and skip backup snapshots which may be unparsable
            affected = [
                f
                for f in normalized
                if f.endswith(".py") and not f.startswith("backups/")
            ]
            if affected:
                print("Running pre-commit on affected files...")
                run(["pre-commit", "run", "--files", *affected])
        except subprocess.CalledProcessError:
            print("[ERROR] pre-commit failed. Aborting auto-push.")
            write_counter(counter)
            return 2

        try:
            print("Running pytest (experimental tests)...")
            run([sys.executable, "-m", "pytest", "-q", "experimental/qa/tests"])
        except subprocess.CalledProcessError:
            print("[ERROR] Tests failed. Aborting auto-push.")
            write_counter(counter)
            return 3

        if enable_push:
            push_changes(branch, dry_run=False)
            write_counter(0)
            return 0
        else:
            print(
                "[INFO] Auto-push disabled. Use --enable or set AUTO_PUSH_ENABLE=1 to allow pushes."
            )
            write_counter(0)
            return 0
    else:
        write_counter(counter)
        print("Threshold not reached yet. Counter saved.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
