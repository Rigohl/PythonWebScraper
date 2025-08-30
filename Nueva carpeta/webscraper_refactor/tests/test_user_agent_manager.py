"""Unit tests for the refactored UserAgentManager."""

import time
import unittest

from src.user_agent_manager import UserAgentManager


class TestUserAgentManager(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = UserAgentManager(["Agent1", "Agent2", "Agent3"])

    def test_init_empty_list(self):
        with self.assertRaises(ValueError):
            UserAgentManager([])

    def test_rotation(self):
        # Collect the first cycle of user agents
        agents_seen = [self.manager.get_user_agent() for _ in range(3)]
        self.assertEqual(len(set(agents_seen)), 3)
        # The next call should loop back to the first agent in the cycle
        first_again = self.manager.get_user_agent()
        self.assertIn(first_again, agents_seen)

    def test_block_and_release(self):
        ua = self.manager.get_user_agent()
        self.manager.block_user_agent(ua, duration_seconds=0.2)
        # Blocked agent should not be available immediately
        self.assertNotIn(ua, self.manager.available_user_agents)
        # After expiration the agent should return automatically
        time.sleep(0.25)
        self.assertFalse(self.manager.is_blocked(ua))
        self.assertIn(ua, self.manager.available_user_agents)
        # Manual release should also work
        self.manager.block_user_agent(ua, duration_seconds=10)
        self.assertTrue(self.manager.is_blocked(ua))
        self.manager.release_user_agent(ua)
        self.assertFalse(self.manager.is_blocked(ua))
        self.assertIn(ua, self.manager.available_user_agents)

    def test_has_available(self):
        self.assertTrue(self.manager.has_available())
        # Block all agents
        for ua in list(self.manager.user_agents):
            self.manager.block_user_agent(ua, duration_seconds=0.1)
        # Should still report available because they are blocked but original list can still be used
        self.assertTrue(self.manager.has_available())
        # After expiry, agents become available again
        time.sleep(0.15)
        self.assertTrue(self.manager.has_available())


if __name__ == "__main__":
    unittest.main()