import json

from src.intelligence.brain import Brain
from src.intelligence.knowledge_base import KnowledgeBase, KnowledgeSnippet


def make_sample_snippet(sn_id: str) -> dict:
    return {
        "id": sn_id,
        "category": "test",
        "title": "Test snippet",
        "content": "Contenido de prueba",
        "tags": ["test"],
        "quality_score": 0.9,
    }


def test_knowledgebase_add_and_get(tmp_path):
    kb_path = tmp_path / "kb.json"
    kb = KnowledgeBase(persist_path=str(kb_path))

    s = make_sample_snippet("test_snippet_1")
    kb.add_snippet(s)

    got = kb.get("test_snippet_1")
    assert got is not None
    assert got["id"] == "test_snippet_1"
    assert "content" in got and got["content"] == "Contenido de prueba"


def test_brain_can_process_event_and_snapshot(tmp_path):
    # Create an isolated brain persistence files under tmp_path
    db_path = str(tmp_path / "brain.db")
    config_path = str(tmp_path / "brain_config.json")
    state_file = str(tmp_path / "brain_state.json")

    brain = Brain(db_path=db_path, config_path=config_path, state_file=state_file)

    # Process a synthetic scraping event and ensure a well-typed response
    event = {
        "url": "http://example.com/test",
        "status": "SUCCESS",
        "response_time": 0.12,
        "content_length": 1200,
        "new_links": 3,
        "domain": "example.com",
    }

    processed = brain.process_scraping_event(event)
    assert isinstance(processed, dict)
    assert "integrated_response" in processed
    assert "scraping_insights" in processed
    assert processed["processing_mode"] == "legacy_simple"

    snap = brain.snapshot()
    assert isinstance(snap, dict)
    assert "domains" in snap
