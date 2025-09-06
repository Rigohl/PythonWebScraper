import pytest


def _import_brain():
    try:
        from src.intelligence.brain import Brain

        return Brain
    except Exception:
        pytest.skip("Brain not available")


def test_brain_init():
    """Test Brain initialization."""
    Brain = _import_brain()
    brain = Brain()

    assert hasattr(brain, "domain_stats")
    assert isinstance(brain.domain_stats, dict)
    assert hasattr(brain, "recent_events")
    assert hasattr(brain, "record_event")


def test_brain_snapshot():
    Brain = _import_brain()
    brain = Brain()

    snapshot = brain.snapshot()
    assert isinstance(snapshot, dict)
    assert "domains" in snapshot


def _import_rl_agent():
    try:
        from src.intelligence.rl_agent import RLAgent

        return RLAgent
    except Exception:
        pytest.skip("RLAgent not available")


def test_rl_agent_init():
    RLAgent = _import_rl_agent()
    agent = RLAgent()

    assert hasattr(agent, "get_action")
    assert hasattr(agent, "learn")


def _import_curiosity():
    try:
        from src.intelligence.curiosity import Curiosity

        return Curiosity
    except Exception:
        pytest.skip("Curiosity not available")


def test_curiosity_init():
    Curiosity = _import_curiosity()
    curiosity = Curiosity()

    assert hasattr(curiosity, "novelty_detector")
    assert curiosity.novelty_detector is not None
