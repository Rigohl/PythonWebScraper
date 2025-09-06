import os
import sys
import tempfile

# Ensure local experimental src is importable when running tests
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from qa.brain_adapter import BrainAdapter


def test_enqueue_and_list(tmp_path):
    db = tmp_path / "sugg.db"
    adapter = BrainAdapter(
        db_path=str(db), settings_path=str(tmp_path / "settings.yaml")
    )
    payload = {"foo": "bar"}
    prov = {"q": "test"}
    sid = adapter.enqueue_suggestion("test_type", payload, prov)
    assert isinstance(sid, int)
    items = adapter.list_suggestions()
    assert any(i["id"] == sid for i in items)


def test_commit_forbidden_by_default(tmp_path):
    db = tmp_path / "sugg2.db"
    adapter = BrainAdapter(
        db_path=str(db), settings_path=str(tmp_path / "settings.yaml")
    )
    payload = {"foo": "bar"}
    prov = {"q": "test"}
    sid = adapter.enqueue_suggestion("test_type", payload, prov)
    try:
        adapter.commit_suggestion(sid)
        committed = True
    except PermissionError:
        committed = False
    assert not committed


def test_pii_sanitization_on_enqueue(tmp_path):
    db = tmp_path / "sugg3.db"
    adapter = BrainAdapter(
        db_path=str(db), settings_path=str(tmp_path / "settings.yaml")
    )
    payload = {"contact": "Juan <juan@example.com> telefono: +34 600 123 456"}
    prov = {"q": "test pii"}
    sid = adapter.enqueue_suggestion("pii_test", payload, prov)
    items = adapter.list_suggestions()
    item = next(i for i in items if i["id"] == sid)
    # payload stored should not contain raw email or phone
    stored_payload = item["payload"]
    assert "REDACTED_EMAIL" in str(stored_payload) or "REDACTED_PHONE" in str(
        stored_payload
    )
