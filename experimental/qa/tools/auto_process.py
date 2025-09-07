"""Automation helper for experimental/qa.

Usage (dry-run): python -m experimental.qa.tools.auto_process --dry
To actually perform auto-accept or git commit enable the flags in settings.yaml
or pass --auto-accept / --auto-commit-git on the CLI. This script is intentionally
conservative and will not override pre-commit hooks automatically.
"""

import argparse
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
SETTINGS = ROOT / "settings.yaml"


def load_settings() -> dict[str, Any]:
    if not SETTINGS.exists():
        return {"commit_enabled": False, "auto_accept": False, "auto_commit_git": False}
    return yaml.safe_load(SETTINGS.read_text(encoding="utf8")) or {}


def run_precommit_on_files(files: list[str]) -> bool:
    """Run pre-commit only against the provided files. Returns True on success."""
    cmd = ["pre-commit", "run", "--files", *files]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd)
    return res.returncode == 0


def git_add_and_commit(files: list[str], message: str) -> bool:
    try:
        subprocess.check_call(["git", "add", *files])
        subprocess.check_call(["git", "commit", "-m", message])
        subprocess.check_call(["git", "push", "-u", "origin", "HEAD"])
        return True
    except subprocess.CalledProcessError as e:
        print("Git operation failed:", e)
        return False


def main(argv: list[str] | None = None) -> int:
    p = load_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto-accept", action="store_true")
    parser.add_argument("--auto-commit-git", action="store_true")
    parser.add_argument(
        "--dry", action="store_true", help="Do not change DB or git; just show actions"
    )
    args = parser.parse_args(argv)

    auto_accept = args.auto_accept or p.get("auto_accept", False)
    auto_commit = args.auto_commit_git or p.get("auto_commit_git", False)

    qa_dir = ROOT / "src" / "qa"
    db = ROOT / "suggestions.db"

    # Discover pending suggestions
    import sqlite3

    if not db.exists():
        print("No suggestions DB found at", db)
        return 0
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute(
        "SELECT id, type, payload, provenance, status FROM suggestions WHERE status = 'pending'"
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No pending suggestions found.")
        return 0

    ids = [str(r[0]) for r in rows]
    print(f"Found {len(rows)} pending suggestions: {', '.join(ids)}")

    if auto_accept:
        print("Auto-accept enabled; marking suggestions as accepted.")
        if not args.dry:
            from experimental.qa.src.qa.brain_adapter import BrainAdapter

            adapter = BrainAdapter()
            for r in rows:
                sid = r[0]
                adapter.accept_suggestion(sid)
            print("Marked as accepted:", ",".join(ids))
        else:
            print("Dry run: would accept:", ",".join(ids))

    if auto_commit:
        # Only commit experimental files by default
        files_to_commit = [
            "experimental/qa/README.md",
            "experimental/qa/requirements-qa.txt",
            "experimental/qa/settings.yaml",
            "experimental/qa/cli.py",
            "experimental/qa/tui.py",
            # add src and tests recursively
        ]
        # expand src and tests
        for pth in (Path("experimental/qa/src"), Path("experimental/qa/tests")):
            if pth.exists():
                for f in pth.rglob("*"):
                    if f.is_file():
                        files_to_commit.append(str(f.as_posix()).replace("\\", "/"))

        print("Files considered for commit:")
        for f in files_to_commit:
            print(" - ", f)

        if args.dry:
            print("Dry run: would run pre-commit on these files and commit if clean.")
            return 0

        ok = run_precommit_on_files(files_to_commit)
        if not ok:
            print("Pre-commit checks failed; aborting commit.")
            return 2

        ok = git_add_and_commit(
            files_to_commit, "feat(experimental/qa): add experimental QA scaffold"
        )
        if not ok:
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
