import pytest
from unittest.mock import Mock
from src.fingerprint_manager import FingerprintManager, COMMON_VIEWPORTS

@pytest.fixture
def mock_user_agent_manager():
    mock = Mock()
    mock.get_user_agent.return_value = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    return mock

@pytest.fixture
def fingerprint_manager(mock_user_agent_manager):
    return FingerprintManager(mock_user_agent_manager)

def test_init_with_invalid_user_agent_manager():
    with pytest.raises(ValueError, match="Se debe proporcionar un UserAgentManager."):
        FingerprintManager(None)

def test_init_with_empty_viewports(mock_user_agent_manager):
    with pytest.raises(ValueError, match="La lista de viewports no puede estar vacía."):
        FingerprintManager(mock_user_agent_manager, viewports=[])

@pytest.mark.parametrize(
    "user_agent, expected_platform",
    [
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Win32"),
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "MacIntel"),
        ("Mozilla/5.0 (X11; Linux x86_64)", "Linux x86_64"),
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)", "iPhone"),
        ("Mozilla/5.0 (Linux; Android 10)", "Linux armv8l"),
        ("Unknown UA", "Win32"), # Default case
    ],
)
def test_get_platform_from_ua(fingerprint_manager, user_agent, expected_platform):
    assert fingerprint_manager._get_platform_from_ua(user_agent) == expected_platform

def test_get_fingerprint_structure(fingerprint_manager):
    fingerprint = fingerprint_manager.get_fingerprint()
    assert "user_agent" in fingerprint
    assert "viewport" in fingerprint
    assert "js_overrides" in fingerprint
    assert isinstance(fingerprint["viewport"], dict)
    assert isinstance(fingerprint["js_overrides"], dict)

def test_get_fingerprint_user_agent_source(fingerprint_manager, mock_user_agent_manager):
    fingerprint = fingerprint_manager.get_fingerprint()
    mock_user_agent_manager.get_user_agent.assert_called_once()
    assert fingerprint["user_agent"] == mock_user_agent_manager.get_user_agent.return_value

def test_get_fingerprint_viewport_selection(fingerprint_manager, monkeypatch):
    mock_choice_return_value = COMMON_VIEWPORTS[0]
    monkeypatch.setattr("random.choice", lambda x: mock_choice_return_value)
    
    fingerprint = fingerprint_manager.get_fingerprint()
    assert fingerprint["viewport"] == mock_choice_return_value

def test_get_fingerprint_js_overrides_content(fingerprint_manager):
    fingerprint = fingerprint_manager.get_fingerprint()
    js_overrides = fingerprint["js_overrides"]
    assert "navigator.webdriver" in js_overrides
    assert "navigator.languages" in js_overrides
    assert "navigator.platform" in js_overrides
    assert "navigator.plugins.length" in js_overrides
    assert "screen.colorDepth" in js_overrides
    assert "navigator.hardwareConcurrency" in js_overrides
    assert "navigator.deviceMemory" in js_overrides
    assert js_overrides["navigator.webdriver"] is False
    # Check that the platform string is correctly embedded
    assert fingerprint_manager._get_platform_from_ua(fingerprint["user_agent"]) in js_overrides["navigator.platform"]