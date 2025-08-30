import pytest
from unittest.mock import Mock
from src.fingerprint_manager import FingerprintManager, DEFAULT_VIEWPORTS, Fingerprint

@pytest.fixture
def mock_user_agent_manager():
    mock = Mock()
    mock.get_user_agent.return_value = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    return mock

@pytest.fixture
def fingerprint_manager(mock_user_agent_manager):
    return FingerprintManager(mock_user_agent_manager)

def test_init_with_invalid_user_agent_manager():
    with pytest.raises(ValueError, match="A UserAgentManager must be provided."):
        FingerprintManager(None)

def test_init_with_empty_viewports(mock_user_agent_manager):
    with pytest.raises(ValueError, match="The viewports list cannot be empty."):
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
def test_platform_from_ua(fingerprint_manager, user_agent, expected_platform):
    assert fingerprint_manager._platform_from_ua(user_agent) == expected_platform

def test_get_fingerprint_structure(fingerprint_manager):
    fingerprint = fingerprint_manager.get_fingerprint()
    assert isinstance(fingerprint, Fingerprint)
    assert isinstance(fingerprint.user_agent, str)
    assert isinstance(fingerprint.viewport, dict)
    assert isinstance(fingerprint.js_overrides, dict)
    assert "width" in fingerprint.viewport
    assert "height" in fingerprint.viewport

def test_get_fingerprint_user_agent_source(fingerprint_manager, mock_user_agent_manager):
    fingerprint = fingerprint_manager.get_fingerprint()
    mock_user_agent_manager.get_user_agent.assert_called_once()
    assert fingerprint.user_agent == mock_user_agent_manager.get_user_agent.return_value

def test_get_fingerprint_viewport_selection(fingerprint_manager, monkeypatch):
    mock_choice_return_value = DEFAULT_VIEWPORTS[0]
    # The manager uses its own random instance, so we patch that one.
    monkeypatch.setattr(fingerprint_manager._random, "choice", lambda x: mock_choice_return_value)

    fingerprint = fingerprint_manager.get_fingerprint()
    assert fingerprint.viewport == mock_choice_return_value

def test_get_fingerprint_js_overrides_content(fingerprint_manager):
    fingerprint = fingerprint_manager.get_fingerprint()
    js_overrides = fingerprint.js_overrides
    assert "navigator.webdriver" in js_overrides
    assert "navigator.languages" in js_overrides
    assert "navigator.platform" in js_overrides
    assert "navigator.plugins.length" in js_overrides
    assert "screen.colorDepth" in js_overrides
    assert "navigator.hardwareConcurrency" in js_overrides
    assert "navigator.deviceMemory" in js_overrides
    assert js_overrides["navigator.webdriver"] is False
    # Check that the platform string is correctly embedded
    platform_string = fingerprint_manager._platform_from_ua(fingerprint.user_agent)
    assert platform_string in js_overrides["navigator.platform"]
