import pytest
import time
from datetime import datetime, timedelta
from src.managers.user_agent_manager import UserAgentManager

@pytest.fixture
def user_agent_manager():
    user_agents = ["Agent1", "Agent2", "Agent3"]
    return UserAgentManager(user_agents)

def test_user_agent_manager_init_empty_list():
    with pytest.raises(ValueError, match="La lista de User-Agents no puede estar vacía."):
        UserAgentManager([])

def test_get_user_agent_rotation(user_agent_manager):
    """Test that User-Agents rotate correctly in a cycle."""
    agents = [user_agent_manager.get_user_agent() for _ in range(3)]
    assert len(set(agents)) == 3  # All agents should be unique in first cycle
    assert user_agent_manager.get_user_agent() == agents[0] # Should loop back

def test_block_user_agent(user_agent_manager):
    """Test that a User-Agent can be blocked and is not used until released or expired."""
    initial_ua = user_agent_manager.get_user_agent()
    user_agent_manager.block_user_agent(initial_ua, duration_seconds=0.1)

    # The blocked UA should not be returned immediately
    next_ua = user_agent_manager.get_user_agent()
    assert next_ua != initial_ua
    assert initial_ua not in user_agent_manager.available_user_agents
    assert initial_ua in user_agent_manager.blocked_user_agents

    # After duration, it should be available again
    time.sleep(0.15)
    user_agent_manager._clean_blocked_user_agents() # Manually clean for test
    assert initial_ua in user_agent_manager.available_user_agents
    assert initial_ua not in user_agent_manager.blocked_user_agents

def test_release_user_agent(user_agent_manager):
    """Test that a blocked User-Agent can be released manually."""
    ua_to_block = user_agent_manager.get_user_agent()
    user_agent_manager.block_user_agent(ua_to_block, duration_seconds=10)

    assert ua_to_block not in user_agent_manager.available_user_agents
    user_agent_manager.release_user_agent(ua_to_block)
    assert ua_to_block in user_agent_manager.available_user_agents
    assert ua_to_block not in user_agent_manager.blocked_user_agents

def test_get_user_agent_all_blocked(user_agent_manager):
    """Test that if all UAs are blocked, it still returns one from the original list."""
    all_uas = list(user_agent_manager.user_agents)
    for ua in all_uas:
        user_agent_manager.block_user_agent(ua, duration_seconds=0.1)

    # All are blocked, so it should return one from the original list
    returned_ua = user_agent_manager.get_user_agent()
    assert returned_ua in all_uas
    # It should still be in blocked_user_agents as its time hasn't passed
    assert returned_ua in user_agent_manager.blocked_user_agents

    time.sleep(0.15)
    user_agent_manager._clean_blocked_user_agents()
    returned_ua = user_agent_manager.get_user_agent()
    assert returned_ua in all_uas
    assert returned_ua not in user_agent_manager.blocked_user_agents

def test_block_non_existent_user_agent(user_agent_manager):
    """Test that blocking a non-existent UA does not raise an error."""
    user_agent_manager.block_user_agent("NonExistentAgent", duration_seconds=1)
    # No assertion needed, just ensuring it doesn't crash

def test_release_non_existent_user_agent(user_agent_manager):
    """Test that releasing a non-existent UA does not raise an error."""
    user_agent_manager.release_user_agent("NonExistentAgent")
    # No assertion needed, just ensuring it doesn't crash
