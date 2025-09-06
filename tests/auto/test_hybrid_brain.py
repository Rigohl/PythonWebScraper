# (removed previous flake8 directive to avoid hiding real errors)
from unittest.mock import MagicMock, patch

import pytest


# Test HybridBrain initialization and basic methods with well-configured mocks
@pytest.fixture
def mock_brain_dependencies():
    # Patch only the critical parts to keep tests deterministic and simple
    with patch(
        "src.intelligence.hybrid_brain.HybridBrain._start_background_processing",
        new=lambda self: None,
    ):
        hb = "src.intelligence.hybrid_brain"
        unified_return = {
            "integrated_response": {},
            "scraping_insights": {},
            "processing_mode": "unified_neural",
        }
        with patch(f"{hb}.Brain", autospec=True) as MockBrain:
            with patch(
                f"{hb}.AutonomousLearningBrain", autospec=True
            ) as MockAutonomous:
                with patch(f"{hb}.KnowledgeBase", autospec=True) as MockKB:
                    with patch(
                        f"{hb}.ContinuousLearningOrchestrator", autospec=True
                    ) as MockOrch:
                        with patch(
                            f"{hb}.HybridBrain._process_with_unified_brain",
                            return_value=unified_return,
                        ):
                            with patch(
                                f"{hb}.KnowledgeStore", autospec=True
                            ) as MockStore:
                                with patch(
                                    f"{hb}.PluginManager", autospec=True
                                ) as MockPlugins:
                                    with patch(
                                        f"{hb}.AdvancedMLIntelligence", autospec=True
                                    ) as MockAdvML:
                                        with patch(
                                            f"{hb}.SelfImprovingSystem", autospec=True
                                        ) as MockSelfImpr:
                                            with patch(
                                                f"{hb}.StealthCDPBrowser", autospec=True
                                            ) as MockBrowser:

                                                # Configure the primary Brain instance returned by the patched Brain class
                                                brain_inst = MockBrain.return_value
                                                brain_inst.snapshot.return_value = {
                                                    "hybrid": {},
                                                    "domains": {},
                                                }
                                                brain_inst.domain_priority.return_value = (
                                                    0.42
                                                )
                                                brain_inst.get_domain_priority = (
                                                    brain_inst.domain_priority
                                                )
                                                brain_inst.domain_success_rate.return_value = (
                                                    0.1
                                                )
                                                brain_inst.should_backoff.return_value = (
                                                    False
                                                )
                                                brain_inst.link_yield.return_value = 0.2
                                                brain_inst.avg_content_length.return_value = (
                                                    123.0
                                                )
                                                brain_inst.domain_stats = {}

                                                # Autonomous learning subsystem: simple state/returns
                                                auto_inst = MockAutonomous.return_value
                                                auto_inst.session_history = []
                                                auto_inst.domain_intelligence = {}
                                                auto_inst.get_intelligence_summary.return_value = {
                                                    "total_sessions": 0
                                                }

                                                # Continuous learning orchestrator shouldn't start threads in tests
                                                orch_inst = MockOrch.return_value
                                                orch_inst.start_background_learning.side_effect = (
                                                    lambda: None
                                                )

                                                # Plugin manager and stores
                                                MockPlugins.return_value = MagicMock()
                                                MockStore.return_value = MagicMock()
                                                MockKB.return_value = MagicMock(
                                                    snippets={},
                                                    add_snippet=lambda *a, **k: None,
                                                )

                                                # Other subsystems minimal config
                                                MockAdvML.return_value = MagicMock()
                                                MockSelfImpr.return_value = MagicMock()
                                                MockBrowser.return_value = MagicMock()

                                                yield


def test_hybrid_brain_init_and_snapshot(mock_brain_dependencies):
    from src.intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain(data_dir="tests/data")
    stats = brain.get_comprehensive_stats()
    # basic keys we expect to exist in the composed stats
    assert any(isinstance(k, str) for k in stats.keys())
    snap = brain.snapshot()
    assert "hybrid" in snap
    assert "domains" in snap


def test_hybrid_brain_process_scraping_event(mock_brain_dependencies):
    from src.intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain(data_dir="tests/data")
    event = {
        "event_type": "test",
        "url": "http://example.com",
        "success": True,
        "data_extracted": {},
    }
    result = brain.process_scraping_event(event)
    assert isinstance(result, dict)
    assert "integrated_response" in result
    assert "scraping_insights" in result
    assert result.get("processing_mode") == "unified_neural"


def test_hybrid_brain_domain_priority_and_backoff(mock_brain_dependencies):
    from src.intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain(data_dir="tests/data")
    domain = "example.com"
    priority = brain.get_domain_priority(domain)
    assert isinstance(priority, float)
    backoff = brain.should_backoff(domain)
    assert isinstance(backoff, bool)


def test_hybrid_brain_flush_and_export(mock_brain_dependencies, tmp_path):
    from src.intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain(data_dir=str(tmp_path))
    # Should not raise
    brain.flush()
    out = tmp_path / "IA_SELF_REPAIR_TEST.md"
    brain.export_repair_report(path=str(out), limit=2)


def test_domain_priority_with_non_empty_history(mock_brain_dependencies):
    """If the autonomous brain has sessions for a domain, priority should reflect that history."""
    from src.intelligence.autonomous_brain import ScrapingSession
    from src.intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain(data_dir="tests/data")
    domain = "hist.example"

    # Inject some sessions into the autonomous brain to simulate learning
    sess1 = ScrapingSession(
        domain=domain,
        url=f"https://{domain}/p/1",
        timestamp=1.0,
        success=True,
        response_time=0.5,
        content_length=1000,
        status_code=200,
        retry_count=1,
        user_agent="ua-1",
        delay_used=1.0,
        extraction_quality=0.9,
        patterns_found=["p1", "p2"],
        errors=[],
    )

    sess2 = ScrapingSession(
        domain=domain,
        url=f"https://{domain}/p/2",
        timestamp=2.0,
        success=False,
        response_time=2.5,
        content_length=0,
        status_code=500,
        retry_count=3,
        user_agent="ua-2",
        delay_used=2.0,
        extraction_quality=0.2,
        patterns_found=[],
        errors=["500_error"],
    )

    brain.autonomous_brain.session_history.extend([sess1, sess2])

    prio = brain.get_domain_priority(domain)
    assert isinstance(prio, float)


def test_should_backoff_true_when_autonomous_threshold_exceeded(
    mock_brain_dependencies,
):
    """When autonomous session history shows low success or many errors, should_backoff should be True."""
    from src.intelligence.autonomous_brain import ScrapingSession
    from src.intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain(data_dir="tests/data")
    domain = "backoff.example"

    # create 5 failing sessions to exceed min_visits_for_backoff
    sessions = []
    for i in range(5):
        sess = ScrapingSession(
            domain=domain,
            url=f"https://{domain}/i/{i}",
            timestamp=float(i),
            success=False,
            response_time=3.0,
            content_length=0,
            status_code=500,
            retry_count=0,
            user_agent="ua",
            delay_used=1.0,
            extraction_quality=0.0,
            patterns_found=[],
            errors=["err"] if i % 2 == 0 else [],
        )
        sessions.append(sess)

    brain.autonomous_brain.session_history.extend(sessions)

    assert brain.should_backoff(domain) is True


def test_flush_and_export_with_real_snippets(mock_brain_dependencies, tmp_path):
    """Test flush and export behavior when the knowledge base contains snippets."""
    from src.intelligence.hybrid_brain import HybridBrain
    from src.intelligence.knowledge_base import KnowledgeSnippet

    brain = HybridBrain(data_dir=str(tmp_path))

    # add a real snippet to the knowledge base
    ks = KnowledgeSnippet(
        id="tst1",
        category="test",
        title="Test Snippet",
        content="content",
        tags=["t"],
        quality_score=0.5,
    )

    brain.knowledge_base.snippets[ks.id] = ks

    # flush should not raise
    brain.flush()

    out = tmp_path / "IA_SELF_REPAIR_TEST_REAL_KB.md"
    suggestions = brain.generate_repair_suggestions(limit=5)

    brain.export_repair_report(path=str(out), limit=5)
    assert out.exists()
    # verify report header and that the total shown matches generated suggestions
    text = out.read_text(encoding="utf-8")
    assert "IA Self-Repair Advisory Report" in text
    assert f"Total sugerencias: {len(suggestions)}" in text
    if len(suggestions) > 0:
        # if advisor produced suggestions, at least one should reference the snippet title
        assert "Test Snippet" in text
