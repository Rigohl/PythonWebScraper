import pytest

from src.managers.user_agent_manager import UserAgentManager


def test_user_agent_manager_init():
    """Test UserAgentManager initialization."""
    user_agents = ["Mozilla/5.0", "Chrome/90.0"]
    manager = UserAgentManager(user_agents)

    assert manager.user_agents == user_agents
    assert len(manager.available_user_agents) == 2


def test_user_agent_manager_get_random():
    """Test UserAgentManager get_user_agent method."""
    user_agents = ["Mozilla/5.0", "Chrome/90.0", "Safari/14.0"]
    manager = UserAgentManager(user_agents)

    ua = manager.get_user_agent()
    assert ua in user_agents

    ua2 = manager.get_user_agent()
    assert ua2 in user_agents
    # Should cycle through available agents
    assert ua != ua2 or len(user_agents) == 1


def test_proxy_manager_init():
    pytest.skip("ProxyManager not implemented yet")


def test_fingerprint_manager_init():
    pytest.skip("FingerprintManager not implemented yet")
