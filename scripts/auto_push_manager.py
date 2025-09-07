# filepath: c:\Users\DELL\Desktop\PythonWebScraper\scripts\auto_push_manager.py
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COUNTER_FILE = REPO_ROOT / ".auto_push_counter"
PROTECTED = {"main", "master", "develop"}
# Be very explicit: default to immediate automatic pushes for this workspace
# (threshold=1) and enable AUTO_PUSH by default. The repo hooks and protected
# branch checks still prevent pushes to protected branches.
DEFAULT_THRESHOLD = int(os.getenv("AUTO_PUSH_THRESHOLD", "1"))
# Default to enabled so automation runs without manual flags; still honor env var
# if user wants to disable it by setting AUTO_PUSH_ENABLE=0.
AUTO_PUSH_ENABLE = os.getenv("AUTO_PUSH_ENABLE", "1") in ("1", "true", "True")
# Only consider these prefixes for auto-push counting and pre-commit checks.
ALLOWED_PREFIXES = (
    "src/",
    "tests/",
    "experimental/",
    "scripts/",
    "experimental/qa/",
)


def run(cmd, cwd=None, capture=False):
    if capture:
        return subprocess.check_output(cmd, cwd=cwd or REPO_ROOT, text=True).strip()
    subprocess.check_call(cmd, cwd=cwd or REPO_ROOT)


def get_branch():
    try:
        return run(["git", "symbolic-ref", "--short", "HEAD"], capture=True)
    except Exception:
        return run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)


def files_in_last_commit():
    try:
        out = run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], capture=True)
        return [p for p in out.splitlines() if p]
    except Exception:
        out = run(["git", "diff", "--name-only", "--cached"], capture=True)
        return [p for p in out.splitlines() if p]


def read_counter():
    try:
        return int(COUNTER_FILE.read_text())
    except Exception:
        return 0


def write_counter(v):
    COUNTER_FILE.write_text(str(int(v)))


def push_changes(branch, dry_run):
    if dry_run:
        print(f"[DRY] Would push branch {branch} to origin")
        return
    print(f"Pushing branch {branch} to origin...")
    run(["git", "push", "-u", "origin", branch])
    print("Push complete.")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--enable", action="store_true")
    p.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    args = p.parse_args(argv)

    dry_run = args.dry_run
    enable_push = args.enable or AUTO_PUSH_ENABLE

    branch = get_branch()
    if branch in PROTECTED:
        print(f"[SKIP] Branch '{branch}' protegido.")
        return 0

    files = files_in_last_commit()
    # Normalize paths to forward slashes and filter to allowed prefixes to avoid
    # processing backups, generated artifacts or unrelated files.
    norm_files = [p.replace("\\", "/") for p in files if p]
    affected = [
        p for p in norm_files if any(p.startswith(pref) for pref in ALLOWED_PREFIXES)
    ]
    delta = len(affected)
    print(f"Archivos en último commit (relevantes): {delta}")
    counter = read_counter()
    counter += delta
    print(f"Contador acumulado: {counter} (umbral={args.threshold})")

    if counter >= args.threshold:
        print("Umbral alcanzado. Ejecutando checks...")
        try:
            if not affected:
                print(
                    "No hay archivos relevantes para ejecutar pre-commit; abortando push automático."
                )
                write_counter(counter)
                return 0
            print("Ejecutando pre-commit en archivos afectados...")
            run(["pre-commit", "run", "--files", *affected])
        except subprocess.CalledProcessError:
            print("[ERROR] pre-commit falló. Abortando push.")
            write_counter(counter)
            return 2
        try:
            print("Ejecutando pytest (experimental tests)...")
            run([sys.executable, "-m", "pytest", "-q", "experimental/qa/tests"])
        except subprocess.CalledProcessError:
            print("[ERROR] Tests fallaron. Abortando push.")
            write_counter(counter)
            return 3
        if enable_push:
            push_changes(branch, dry_run=dry_run)
            write_counter(0)
            return 0
        else:
            print(
                "[INFO] Push automático deshabilitado. Usa --enable o AUTO_PUSH_ENABLE=1"
            )
            write_counter(0)
            return 0
    else:
        write_counter(counter)
        print("No se alcanzó el umbral. Guardado contador.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
