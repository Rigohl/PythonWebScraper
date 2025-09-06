def test_help_overlay_toggle():
    """Test that help overlay toggles visibility without exceptions."""
    import types

    from src.tui.app import ScraperTUIApp

    app = ScraperTUIApp(log_file_path=None)
    # Mockea query_one para devolver un HelpOverlay falso
    app.query_one = lambda *a, **kw: types.SimpleNamespace(toggle=lambda: None)
    try:
        app.action_help()
    except (AssertionError, RuntimeError) as e:
        assert False, f"action_help raised exception: {e}"
