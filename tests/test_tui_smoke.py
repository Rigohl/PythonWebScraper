import importlib.util

import pytest


def test_tui_compose_does_not_raise():
    """Smoke test: instantiating the TUI and calling compose() should not raise."""
    # Import inside test to avoid top-level import side-effects during collection
    from src.tui.app import ScraperTUIApp

    # Create a test subclass that doesn't initialize AI
    class TestScraperTUIApp(ScraperTUIApp):
        def on_mount(self) -> None:
            """Skip AI initialization."""
            pass

    app = TestScraperTUIApp(log_file_path=None)

    # For Textual apps, we need to run the app in test mode to have an active context
    async def run_compose():
        try:
            async with app.run_test() as pilot:
                widgets = list(app.compose())
                assert len(widgets) > 0
        except Exception as e:
            if "styles.css" in str(e):
                pytest.skip("styles.css not found, skipping TUI compose test")
            else:
                assert False, f"Unexpected exception: {e}"

    import asyncio

    asyncio.run(run_compose())


def test_tui_launch_smoke_demo_mode():
    """Probar que el TUI principal se inicializa sin excepciones en modo demo"""
    try:
        # Verificar que podemos importar la clase principal del TUI
        from src.tui.app import ScraperTUIApp

        # Verificar que es callable (constructor)
        assert callable(ScraperTUIApp)

        # Si podemos instanciar sin excepciones inmediatas, es una buena señal
        app = ScraperTUIApp(log_file_path=None)
        assert app is not None

    except Exception as e:
        # Si hay algún error de importación o inicialización, fallar el test
        pytest.fail(f"TUI launch failed with error: {e}")


def test_tui_imports_successful():
    """Verificar que todos los imports del TUI funcionan correctamente"""
    try:
        from src.tui.app import ScraperTUIApp

        app = ScraperTUIApp()
        assert app is not None
    except ImportError as e:
        pytest.fail(f"TUI import failed: {e}")
    except Exception as e:
        pytest.fail(f"TUI initialization failed: {e}")


def test_tui_dependencies_available():
    """Verificar que las dependencias del TUI están disponibles"""
    try:
        # Verificar dependencias usando importlib para evitar imports innecesarios
        deps = ["textual", "rich"]
        for dep in deps:
            spec = importlib.util.find_spec(dep)
            assert spec is not None, f"Dependency {dep} not available"

        # Verificar versión de textual
        import textual

        assert textual.__version__ is not None

    except ImportError as e:
        pytest.fail(f"TUI dependency missing: {e}")
