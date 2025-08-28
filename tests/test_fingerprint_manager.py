import unittest
from unittest.mock import Mock, patch
from src.fingerprint_manager import FingerprintManager, COMMON_VIEWPORTS

class TestFingerprintManager(unittest.TestCase):

    def setUp(self):
        self.mock_user_agent_manager = Mock()
        self.mock_user_agent_manager.get_user_agent.return_value = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.manager = FingerprintManager(self.mock_user_agent_manager)

    def test_init_with_invalid_user_agent_manager(self):
        with self.assertRaises(ValueError):
            FingerprintManager(None)

    def test_init_with_empty_viewports(self):
        with self.assertRaises(ValueError):
            FingerprintManager(self.mock_user_agent_manager, viewports=[])

    def test_get_platform_from_ua_windows(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.assertEqual(self.manager._get_platform_from_ua(ua), "Win32")

    def test_get_platform_from_ua_mac(self):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.assertEqual(self.manager._get_platform_from_ua(ua), "MacIntel")

    def test_get_platform_from_ua_linux(self):
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.assertEqual(self.manager._get_platform_from_ua(ua), "Linux x86_64")

    def test_get_platform_from_ua_iphone(self):
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        self.assertEqual(self.manager._get_platform_from_ua(ua), "iPhone")

    def test_get_platform_from_ua_android(self):
        ua = "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        self.assertEqual(self.manager._get_platform_from_ua(ua), "Linux armv8l")

    def test_get_fingerprint_structure(self):
        fingerprint = self.manager.get_fingerprint()
        self.assertIn("user_agent", fingerprint)
        self.assertIn("viewport", fingerprint)
        self.assertIn("js_overrides", fingerprint)
        self.assertIsInstance(fingerprint["viewport"], dict)
        self.assertIsInstance(fingerprint["js_overrides"], dict)

    def test_get_fingerprint_user_agent_source(self):
        fingerprint = self.manager.get_fingerprint()
        self.mock_user_agent_manager.get_user_agent.assert_called_once()
        self.assertEqual(fingerprint["user_agent"], self.mock_user_agent_manager.get_user_agent.return_value)

    def test_get_fingerprint_viewport_selection(self):
        with patch('random.choice', return_value=COMMON_VIEWPORTS[0]) as mock_choice:
            fingerprint = self.manager.get_fingerprint()
            mock_choice.assert_called_once_with(COMMON_VIEWPORTS)
            self.assertEqual(fingerprint["viewport"], COMMON_VIEWPORTS[0])

    def test_get_fingerprint_js_overrides_content(self):
        fingerprint = self.manager.get_fingerprint()
        js_overrides = fingerprint["js_overrides"]
        self.assertIn("navigator.webdriver", js_overrides)
        self.assertIn("navigator.languages", js_overrides)
        self.assertIn("navigator.platform", js_overrides)
        self.assertIn("navigator.plugins.length", js_overrides)
        self.assertIn("screen.colorDepth", js_overrides)
        self.assertIn("navigator.hardwareConcurrency", js_overrides)
        self.assertIn("navigator.deviceMemory", js_overrides)
        self.assertEqual(js_overrides["navigator.webdriver"], False)
        self.assertIn(self.manager._get_platform_from_ua(fingerprint["user_agent"]), js_overrides["navigator.platform"])

if __name__ == '__main__':
    unittest.main()
