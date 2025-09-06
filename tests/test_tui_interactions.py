import pytest

from src.tui.app import ScraperTUIApp


@pytest.mark.asyncio
async def test_tui_help_toggle():
    """Test that help overlay toggles without raising exceptions."""
    app = ScraperTUIApp()
    import types

    # Mockea query_one para devolver un HelpOverlay falso
    app.query_one = lambda *a, **kw: types.SimpleNamespace(toggle=lambda: None)
    try:
        app.action_help()
    except (AssertionError, RuntimeError) as e:
        assert False, f"action_help raised exception: {e}"
