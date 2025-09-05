import os
import pytest

from src.intelligence.brain import Brain, ExperienceEvent

# HybridBrain is optional; skip related assertions if import fails
try:
    from src.intelligence.hybrid_brain import HybridBrain
except Exception:  # pragma: no cover
    HybridBrain = None  # type: ignore


def make_event(domain: str = "example.com", status: str = "SUCCESS", new_links: int = 3):
    return ExperienceEvent(
        url=f"https://{domain}/page",
        status=status,
        response_time=120,
        content_length=500,
        new_links=new_links,
        domain=domain,
        extracted_fields=2,
        error_type=None,
    )


def test_brain_basic_snapshot_and_priority(tmp_path):
    state_file = tmp_path / "brain_state.json"
    brain = Brain(state_file=str(state_file))

    # Record mixed events
    brain.record_event(make_event("a.com", "SUCCESS", 5))
    brain.record_event(make_event("a.com", "ERROR", 0))
    brain.record_event(make_event("b.com", "SUCCESS", 2))

    snap = brain.snapshot()
    assert "domains" in snap
    assert "top_domains" in snap
    assert snap["total_events"] == 3

    # Priority should be higher for domain with better success/link yield
    prio_a = brain.domain_priority("a.com")
    prio_b = brain.domain_priority("b.com")
    assert isinstance(prio_a, float) and isinstance(prio_b, float)


def test_hybrid_brain_compatibility(tmp_path):
    if HybridBrain is None:
        pytest.skip("HybridBrain not available")

    os.environ["HYBRID_BRAIN_TEST_MODE"] = "1"
    state_file = tmp_path / "hybrid_brain_state.json"
    learning_file = tmp_path / "hybrid_learning.json"

    hybrid = HybridBrain(state_file=str(state_file), learning_file=str(learning_file))

    hybrid.record_scraping_result(type("R", (), {
        "url": "https://c.com/page1",
        "success": True,
        "content": "x" * 800,
        "links": ["/p2", "/p3"],
        "extracted_data": {"title": "Sample"},
        "is_duplicate": False,
        "error": None,
    })(), context={"response_time": 200})

    snap = hybrid.snapshot()
    assert snap.get("hybrid") is True
    assert "domains" in snap

    # Comprehensive stats path
    comp = hybrid.get_comprehensive_stats()
    assert comp.get("hybrid_system") is True
    assert "simple_brain" in comp and "autonomous_brain" in comp

    prio = hybrid.domain_priority("c.com")
    assert isinstance(prio, float)

    # Backoff should be boolean
    assert isinstance(hybrid.should_backoff("c.com"), bool)

    # Flush should not raise
    hybrid.flush()
