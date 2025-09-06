"""Lightweight TUI for reviewing suggestions.

Provides non-interactive helpers useful for tests and a simple interactive
console loop (no external dependencies) to review, reject or attempt to commit
suggestions. Commits are only allowed when `experimental/qa/settings.yaml` has
`commit_enabled: true`.
"""

import json
from pathlib import Path
from typing import Any, Optional

from qa.brain_adapter import BrainAdapter


def list_suggestions(
    adapter: Optional[BrainAdapter] = None, status: Optional[str] = None
):
    adapter = adapter or BrainAdapter()
    return adapter.list_suggestions(status=status)


def review_suggestion(
    adapter: Optional[BrainAdapter], suggestion_id: int, approve: bool = False
) -> dict:
    adapter = adapter or BrainAdapter()
    if not isinstance(suggestion_id, int):
        raise TypeError("suggestion_id must be int")
    if approve:
        # attempt commit (may raise PermissionError if commits disabled)
        res = adapter.commit_suggestion(suggestion_id)
        return {"action": "committed", "result": res}
    else:
        # mark as rejected
        adapter.reject_suggestion(suggestion_id)
        return {"action": "rejected", "id": suggestion_id}


def interactive_loop():
    adapter = BrainAdapter()
    print("Suggestion review TUI (type 'q' to quit)")
    while True:
        items = adapter.list_suggestions()
        if not items:
            print("No suggestions found.")
        else:
            for i in items:
                print(
                    f"{i['id']}: {i['type']} status={i['status']} created={i['created_at']}"
                )
        cmd = input("command (id approve/reject/refresh/q): ").strip()
        if cmd == "q":
            break
        if cmd == "refresh":
            continue
        parts = cmd.split()
        if len(parts) >= 2:
            try:
                sid = int(parts[0])
            except Exception:
                print("Invalid id")
                continue
            action = parts[1]
            if action == "approve":
                try:
                    res = adapter.commit_suggestion(sid)
                    print(f"Committed suggestion {sid}: {res}")
                except Exception as e:
                    print(f"Commit failed: {e}")
            elif action == "reject":
                adapter.reject_suggestion(sid)
                print(f"Rejected {sid}")
            else:
                print("Unknown action")
        else:
            print("Unknown command")


if __name__ == "__main__":
    interactive_loop()
