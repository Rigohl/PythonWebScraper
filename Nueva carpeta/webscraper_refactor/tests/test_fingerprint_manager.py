"""Unit tests for the refactored FingerprintManager."""

import unittest
from types import SimpleNamespace

from src.user_agent_manager import UserAgentManager
from src.fingerprint_manager import FingerprintManager, Fingerprint


class DummyRandom:
    """Deterministic random number generator for testing."""
    def __init__(self):
        self.choice_calls = []
    def choice(self, seq):
        # Always return the first element and record the call
        self.choice_calls.append(seq)
        return seq[0]


class TestFingerprintManager(unittest.TestCase):
    def setUp(self) -> None:
        self.ua_manager = UserAgentManager(["AgentA", "AgentB"])

    def test_get_fingerprint_structure(self):
        fm = FingerprintManager(self.ua_manager)
        fp = fm.get_fingerprint()
        self.assertIsInstance(fp, Fingerprint)
        self.assertIn("width", fp.viewport)
        self.assertIn("height", fp.viewport)
        self.assertIsInstance(fp.user_agent, str)
        self.assertIsInstance(fp.js_overrides, dict)

    def test_custom_random_and_viewport(self):
        dummy_rand = DummyRandom()
        custom_viewports = [{"width": 800, "height": 600}, {"width": 1024, "height": 768}]
        fm = FingerprintManager(self.ua_manager, viewports=custom_viewports, rand=dummy_rand)
        fp1 = fm.get_fingerprint()
        self.assertEqual(fp1.viewport, custom_viewports[0])
        # Change viewports and ensure update takes effect
        fm.set_viewports([{"width": 1280, "height": 720}])
        fp2 = fm.get_fingerprint()
        self.assertEqual(fp2.viewport, {"width": 1280, "height": 720})

    def test_set_viewports_validation(self):
        fm = FingerprintManager(self.ua_manager)
        with self.assertRaises(ValueError):
            fm.set_viewports([])


if __name__ == "__main__":
    unittest.main()