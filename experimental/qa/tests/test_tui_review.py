import json
import sys
import tempfile
from pathlib import Path

# ensure local experimental src is importable (experimental/qa/src)
HERE = Path(__file__).resolve().parents[1]
SRC = HERE / "src"
# add experimental src (qa package) and the experimental folder (for tui.py)
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

from qa.brain_adapter import BrainAdapter

from tui import review_suggestion


def test_review_reject_and_commit_blocked(tmp_path):
    db = tmp_path / "suggestions.db"
    settings = tmp_path / "settings.yaml"
    settings.write_text("commit_enabled: false\n")

    adapter = BrainAdapter(db_path=db, settings_path=settings)

    # enqueue a suggestion
    payload = {"action": "update", "field": "title", "value": "New"}
    provenance = {"source": "test"}
    sid = adapter.enqueue_suggestion("test_type", payload, provenance)

    # reject it via the tui helper
    review_suggestion(adapter, sid, approve=False)

    # now list and check status
    items = adapter.list_suggestions()
    assert any(it["id"] == sid and it["status"] == "rejected" for it in items)

    # approving should raise PermissionError because commit_enabled is false
    try:
        review_suggestion(adapter, sid, approve=True)
    except PermissionError:
        # expected
        pass
    else:
        raise AssertionError(
            "Expected PermissionError when trying to commit with commit_enabled=false"
        )
