import unittest
from src.proxy_manager import ProxyManager
from datetime import datetime, timedelta
import time

class TestProxyManager(unittest.TestCase):

    def setUp(self):
        self.proxies = ["http://proxy1.com", "http://proxy2.com", "http://proxy3.com"]
        self.manager = ProxyManager(self.proxies)

    def test_initialization(self):
        """Prueba que el gestor de proxies se puede instanciar y los proxies se cargan correctamente."""
        self.assertIsInstance(self.manager, ProxyManager)
        self.assertEqual(len(self.manager.available_proxies), len(self.proxies))
        self.assertEqual(len(self.manager.in_use_proxies), 0)
        self.assertEqual(len(self.manager.blocked_proxies), 0)

    def test_get_proxy(self):
        """Prueba que se puede obtener un proxy y se mueve a 'in_use'."""
        retrieved_proxies = set()
        for _ in range(len(self.proxies)):
            p = self.manager.get_proxy()
            if p:
                retrieved_proxies.add(p)
        self.assertEqual(len(retrieved_proxies), len(self.proxies))
        self.assertEqual(len(self.manager.available_proxies), 0)
        self.assertEqual(len(self.manager.in_use_proxies), len(self.proxies))
        self.assertIsNone(self.manager.get_proxy()) # No more proxies available

    def test_clean_blocked_proxies(self):
        """Prueba que los proxies bloqueados expiran y vuelven a estar disponibles."""
        proxy_to_block = self.manager.get_proxy()
        self.manager.block_proxy(proxy_to_block, block_duration_seconds=1)

        self.assertIn(proxy_to_block, self.manager.blocked_proxies)
        self.assertNotIn(proxy_to_block, self.manager.available_proxies)

        # Wait for the block duration to pass
        time.sleep(1.1)

        # Explicitly call _clean_blocked_proxies
        self.manager._clean_blocked_proxies()

        self.assertNotIn(proxy_to_block, self.manager.blocked_proxies)
        self.assertIn(proxy_to_block, self.manager.available_proxies) # Should be available again

if __name__ == '__main__':
    unittest.main()