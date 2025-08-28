import pytest
from datetime import datetime, timedelta
import time

from src.proxy_manager import ProxyManager

@pytest.fixture
def proxy_manager():
    proxies = ["http://proxy1.com", "http://proxy2.com", "http://proxy3.com"]
    return ProxyManager(proxies)

def test_initialization(proxy_manager):
    assert isinstance(proxy_manager, ProxyManager)
    assert len(proxy_manager.available_proxies) == 3
    assert len(proxy_manager.in_use_proxies) == 0
    assert len(proxy_manager.blocked_proxies) == 0

def test_initialization_empty_proxies():
    manager = ProxyManager([])
    assert len(manager.available_proxies) == 0
    assert manager.get_proxy() is None

def test_get_proxy(proxy_manager):
    retrieved_proxies = set()
    for _ in range(3):
        p = proxy_manager.get_proxy()
        assert p is not None
        retrieved_proxies.add(p)
    assert len(retrieved_proxies) == 3
    assert len(proxy_manager.available_proxies) == 0
    assert len(proxy_manager.in_use_proxies) == 3
    assert proxy_manager.get_proxy() is None # No more proxies available

def test_clean_blocked_proxies(proxy_manager):
    proxy_to_block = proxy_manager.get_proxy()
    proxy_manager.block_proxy(proxy_to_block, block_duration_seconds=0.1)

    assert proxy_to_block in proxy_manager.blocked_proxies
    assert proxy_to_block not in proxy_manager.available_proxies

    time.sleep(0.15)
    proxy_manager._clean_blocked_proxies()

    assert proxy_to_block not in proxy_manager.blocked_proxies
    assert proxy_to_block in proxy_manager.available_proxies

def test_block_proxy_from_available(proxy_manager):
    proxy = proxy_manager.get_proxy()
    proxy_manager.return_proxy(proxy) # Make it available again
    
    proxy_manager.block_proxy(proxy, block_duration_seconds=1)
    assert proxy not in proxy_manager.available_proxies
    assert proxy not in proxy_manager.in_use_proxies
    assert proxy in proxy_manager.blocked_proxies

def test_block_proxy_from_in_use(proxy_manager):
    proxy = proxy_manager.get_proxy()
    proxy_manager.block_proxy(proxy, block_duration_seconds=1)
    assert proxy not in proxy_manager.available_proxies
    assert proxy not in proxy_manager.in_use_proxies
    assert proxy in proxy_manager.blocked_proxies

def test_return_proxy(proxy_manager):
    proxy = proxy_manager.get_proxy()
    proxy_manager.return_proxy(proxy)
    assert proxy in proxy_manager.available_proxies
    assert proxy not in proxy_manager.in_use_proxies

def test_block_non_existent_proxy(proxy_manager):
    # Should not raise an error
    proxy_manager.block_proxy("http://nonexistent.com", block_duration_seconds=1)
    assert "http://nonexistent.com" not in proxy_manager.blocked_proxies # Should not add it if not in original list

def test_return_non_existent_proxy(proxy_manager):
    # Should not raise an error
    proxy_manager.return_proxy("http://nonexistent.com")
    assert "http://nonexistent.com" not in proxy_manager.available_proxies
