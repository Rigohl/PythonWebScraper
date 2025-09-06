import json
import sys
from pathlib import Path

# ensure local experimental src is importable
HERE = Path(__file__).resolve().parents[1]
SRC = HERE / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

from qa.brain_adapter import BrainAdapter

from tui import review_suggestion


def test_review_approve_commits_when_enabled(tmp_path):
    db = tmp_path / "suggestions.db"
    settings = tmp_path / "settings.yaml"
    settings.write_text("commit_enabled: true\n")

    adapter = BrainAdapter(db_path=db, settings_path=settings)

    # enqueue a suggestion
    payload = {"action": "update", "field": "title", "value": "New"}
    provenance = {"source": "test"}
    sid = adapter.enqueue_suggestion("test_type", payload, provenance)

    # approve via tui helper (should commit and return payload)
    res = review_suggestion(adapter, sid, approve=True)
    assert res.get("action") == "committed"
    assert res.get("result") and res["result"]["id"] == sid

    # check DB status
    items = adapter.list_suggestions()
    assert any(it["id"] == sid and it["status"] == "committed" for it in items)
