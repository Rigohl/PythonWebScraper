"""Safe Brain adapter: read-only operations and a suggestion queue (SQLite).

By default suggestions are enqueued and NOT committed to any real brain. A
feature-flag in settings.yaml controls whether commit is allowed.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


class BrainAdapter:
    def __init__(self, db_path: str | None = None, settings_path: str | None = None):
        # base directory for experimental artifacts (allow overrides via args)
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = (
                Path(__file__).resolve().parent.parent.parent
                / "experimental"
                / "qa"
                / "suggestions.db"
            )
        if settings_path:
            self.settings_path = Path(settings_path)
        else:
            self.settings_path = (
                Path(__file__).resolve().parent.parent.parent
                / "experimental"
                / "qa"
                / "settings.yaml"
            )
        self._ensure_db()

    def _ensure_db(self):
        p = self.db_path
        p.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(p))
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                payload TEXT,
                provenance TEXT,
                status TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def _load_settings(self) -> dict[str, Any]:
        p = Path(self.settings_path)
        if not p.exists():
            return {"commit_enabled": False}
        try:
            return yaml.safe_load(p.read_text(encoding="utf8")) or {
                "commit_enabled": False
            }
        except Exception:
            return {"commit_enabled": False}

    def enqueue_suggestion(
        self, s_type: str, payload: dict[str, Any], provenance: dict[str, Any]
    ) -> int:
        # Sanitize payload for PII before enqueueing
        try:
            from qa.pii import sanitize_payload
        except Exception:
            # fallback: no sanitization
            sanitized_payload = payload
            sanitization = {"emails": 0, "phones": 0, "cards": 0}
        else:
            sanitized_payload, sanitization = sanitize_payload(payload)
        # attach sanitization summary to provenance
        prov = dict(provenance)
        prov["sanitization"] = sanitization

        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        # use timezone-aware UTC timestamp to avoid DeprecationWarning
        now = datetime.now(timezone.utc).isoformat()
        cur.execute(
            "INSERT INTO suggestions (type, payload, provenance, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                s_type,
                json.dumps(sanitized_payload, ensure_ascii=False),
                json.dumps(prov, ensure_ascii=False),
                "pending",
                now,
            ),
        )
        sid = cur.lastrowid
        conn.commit()
        conn.close()
        return sid

    def accept_suggestion(self, suggestion_id: int) -> dict[str, Any]:
        """Mark a suggestion as accepted (but not necessarily committed to an external brain).

        This provides a safe intermediary status when auto-accept is enabled but
        `commit_enabled` is False in settings.yaml.
        """
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT payload FROM suggestions WHERE id = ?", (suggestion_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise KeyError("Suggestion not found")
        payload = json.loads(row[0])
        cur.execute(
            "UPDATE suggestions SET status = ? WHERE id = ?",
            ("accepted", suggestion_id),
        )
        conn.commit()
        conn.close()
        return {"id": suggestion_id, "payload": payload}

    def list_suggestions(self, status: str | None = None) -> list[dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        if status:
            cur.execute(
                "SELECT id, type, payload, provenance, status, created_at FROM suggestions WHERE status = ?",
                (status,),
            )
        else:
            cur.execute(
                "SELECT id, type, payload, provenance, status, created_at FROM suggestions"
            )
        rows = cur.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append(
                {
                    "id": r[0],
                    "type": r[1],
                    "payload": json.loads(r[2]),
                    "provenance": json.loads(r[3]),
                    "status": r[4],
                    "created_at": r[5],
                }
            )
        return out

    def commit_suggestion(self, suggestion_id: int) -> dict[str, Any]:
        settings = self._load_settings()
        if not settings.get("commit_enabled", False):
            raise PermissionError(
                "Commit disabled by configuration (commit_enabled=false)"
            )
        # In safe mode we do not implement real commits. Placeholder for future.
        # For now, mark suggestion as committed in DB and return the payload.
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT payload FROM suggestions WHERE id = ?", (suggestion_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise KeyError("Suggestion not found")
        payload = json.loads(row[0])
        cur.execute(
            "UPDATE suggestions SET status = ? WHERE id = ?",
            ("committed", suggestion_id),
        )
        conn.commit()
        conn.close()
        return {"id": suggestion_id, "payload": payload}

    def reject_suggestion(self, suggestion_id: int) -> None:
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("SELECT id FROM suggestions WHERE id = ?", (suggestion_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise KeyError("Suggestion not found")
        cur.execute(
            "UPDATE suggestions SET status = ? WHERE id = ?",
            ("rejected", suggestion_id),
        )
        conn.commit()
        conn.close()
