import pytest
from unittest.mock import Mock, patch
import numpy as np
import os

from src.intelligence.rl_agent import RLAgent, ScrapingEnv

# Fixtures for mocking dependencies
@pytest.fixture
def mock_ppo_load():
    with patch('stable_baselines3.PPO.load') as mock:
        yield mock

@pytest.fixture
def mock_ppo_init():
    with patch('stable_baselines3.PPO.__init__', return_value=None) as mock:
        yield mock

@pytest.fixture
def mock_ppo_predict():
    with patch('stable_baselines3.PPO.predict') as mock:
        # Default prediction: no change (action 1)
        mock.return_value = (np.array([1]), None)
        yield mock

@pytest.fixture
def mock_ppo_save():
    with patch('stable_baselines3.PPO.save') as mock:
        yield mock

@pytest.fixture
def mock_os_path_exists():
    with patch('os.path.exists') as mock:
        mock.return_value = False # Default: no model exists
        yield mock

# Tests for ScrapingEnv
def test_scraping_env_init():
    env = ScrapingEnv()
    assert env.observation_space.shape == (3,)
    assert env.action_space.n == 3
    assert np.array_equal(env.current_state, np.zeros(3))

def test_scraping_env_set_state():
    env = ScrapingEnv()
    state_dict = {"low_quality_ratio": 0.1, "failure_ratio": 0.2, "current_backoff": 1.5}
    env.set_state(state_dict)
    assert np.array_equal(env.current_state, np.array([0.1, 0.2, 1.5], dtype=np.float32))

def test_scraping_env_step_reset_render_close():
    env = ScrapingEnv()
    obs, reward, terminated, truncated, info = env.step(0)
    assert np.array_equal(obs, np.zeros(3))
    assert reward == 0.0
    assert terminated is False
    assert truncated is False
    assert info == {}

    obs_reset, info_reset = env.reset()
    assert np.array_equal(obs_reset, np.zeros(3))
    assert info_reset == {}

    env.render()
    env.close()
    # No assertions needed, just ensuring they don't raise errors

# Tests for RLAgent
def test_rl_agent_init_new_model(mock_ppo_init, mock_os_path_exists):
    agent = RLAgent(domain="test.com", model_path="/tmp/model")
    mock_ppo_init.assert_called_once_with("MlpPolicy", agent.vec_env, verbose=0, device="cpu")
    assert agent.model is not None

def test_rl_agent_init_load_existing_model(mock_ppo_load, mock_os_path_exists):
    mock_os_path_exists.return_value = True
    agent = RLAgent(domain="test.com", model_path="/tmp/model")
    mock_ppo_load.assert_called_once()
    assert agent.model is not None

def test_rl_agent_get_action_decrease_backoff(mock_ppo_predict):
    mock_ppo_predict.return_value = (np.array([0]), None) # Action 0
    agent = RLAgent(domain="test.com")
    action = agent.get_action({"low_quality_ratio": 0.5, "failure_ratio": 0.5, "current_backoff": 1.0})
    assert action == {"adjust_backoff_factor": 0.8}

def test_rl_agent_get_action_no_change(mock_ppo_predict):
    mock_ppo_predict.return_value = (np.array([1]), None) # Action 1
    agent = RLAgent(domain="test.com")
    action = agent.get_action({"low_quality_ratio": 0.5, "failure_ratio": 0.5, "current_backoff": 1.0})
    assert action == {"adjust_backoff_factor": 1.0}

def test_rl_agent_get_action_increase_backoff(mock_ppo_predict):
    mock_ppo_predict.return_value = (np.array([2]), None) # Action 2
    agent = RLAgent(domain="test.com")
    action = agent.get_action({"low_quality_ratio": 0.5, "failure_ratio": 0.5, "current_backoff": 1.0})
    assert action == {"adjust_backoff_factor": 1.2}

def test_rl_agent_save_model(mock_ppo_save):
    agent = RLAgent(domain="test.com", model_path="/tmp/model")
    agent.model = Mock() # Ensure model is not None
    agent.save_model()
    agent.model.save.assert_called_once_with("/tmp/model")

def test_rl_agent_learn_calls_model_learn(mock_ppo_predict, mock_ppo_save):
    # This test confirms that agent.model.learn is called, but does NOT
    # verify the effectiveness of the RL learning due to the on-policy nature
    # of PPO and the current integration design.
    agent = RLAgent(domain="test.com", model_path="/tmp/test_model")
    agent.model = Mock() # Mock the PPO model instance
    agent.buffer_size = 1 # Set buffer size to 1 for immediate learning

    state = {"low_quality_ratio": 0.1, "failure_ratio": 0.1, "current_backoff": 1.0}
    action_taken = {"adjust_backoff_factor": 1.0}
    reward = 0.5
    next_state = {"low_quality_ratio": 0.0, "failure_ratio": 0.0, "current_backoff": 1.0}

    agent.learn(state, action_taken, reward, next_state)

    agent.model.learn.assert_called_once_with(total_timesteps=agent.buffer_size)
    # Note: save is called in finally block, so it should be called even if learn fails
    agent.model.save.assert_called_once() # save_model should be called after learn
    assert len(agent.experience_buffer) == 0 # Buffer should be cleared

# Acknowledge the limitation of RL learning effectiveness testing
# The current design of RLAgent.learn is not suitable for effective on-policy RL training.
# Comprehensive testing of RL learning would require a refactoring of the environment interaction.
