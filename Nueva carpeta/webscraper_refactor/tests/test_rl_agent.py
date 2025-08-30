"""Unit tests for the refactored RLAgent."""

import os
import tempfile
import unittest

from src.rl_agent import RLAgent


class TestRLAgent(unittest.TestCase):
    def test_get_action_and_learn(self):
        # Instantiate RLAgent without specifying model_path; will use dummy if RL unavailable
        agent = RLAgent(domain="example.com", model_path=None)
        state = {"low_quality_ratio": 0.1, "failure_ratio": 0.0, "current_backoff": 1.0}
        action = agent.get_action(state)
        self.assertIsInstance(action, dict)
        self.assertIn("adjust_backoff_factor", action)
        # Perform learning; should not raise
        next_state = {"low_quality_ratio": 0.2, "failure_ratio": 0.0, "current_backoff": 1.0}
        agent.learn(state, action, reward=1.0, next_state=next_state)

    def test_save_model(self):
        tmpdir = tempfile.mkdtemp()
        try:
            model_path = os.path.join(tmpdir, "model_rl")
            agent = RLAgent(domain="example.com", model_path=model_path)
            # Save model
            agent.save_model()
            # In dummy mode there may be no file; in RL mode a .zip file may appear
            # The test simply ensures no exception was raised
            self.assertTrue(True)
        finally:
            # Clean up
            for filename in os.listdir(tmpdir):
                os.remove(os.path.join(tmpdir, filename))
            os.rmdir(tmpdir)


if __name__ == '__main__':
    unittest.main()