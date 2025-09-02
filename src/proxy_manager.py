import random
from datetime import datetime, timedelta


class ProxyManager:
    def __init__(self, proxies=None):
        self.proxies = proxies if proxies is not None else []
        self.available_proxies = set(self.proxies)
        self.in_use_proxies = set()
        self.blocked_proxies = {}  # {proxy: block_until_timestamp}

    def _clean_blocked_proxies(self):
        """Removes expired blocked proxies from the blocked list and makes them available."""
        now = datetime.now()
        for proxy, block_until in list(self.blocked_proxies.items()):
            if now > block_until:
                self.available_proxies.add(proxy)
                del self.blocked_proxies[proxy]

    def get_proxy(self):
        """Returns an available proxy, or None if no proxies are available."""
        self._clean_blocked_proxies()
        if not self.available_proxies:
            return None

        proxy = random.choice(list(self.available_proxies))
        self.available_proxies.remove(proxy)
        self.in_use_proxies.add(proxy)
        return proxy

    def block_proxy(self, proxy, block_duration_seconds=300):
        """Blocks a proxy for a certain duration (in seconds)."""
        if proxy in self.in_use_proxies:
            self.in_use_proxies.remove(proxy)
        if proxy in self.available_proxies:
            self.available_proxies.remove(proxy)
        # Only add to blocked if it's a known proxy
        if proxy in self.proxies:
            self.blocked_proxies[proxy] = datetime.now() + timedelta(seconds=block_duration_seconds)

    def return_proxy(self, proxy):
        """Returns a proxy to the available pool."""
        if proxy in self.in_use_proxies:
            self.in_use_proxies.remove(proxy)
            self.available_proxies.add(proxy)
