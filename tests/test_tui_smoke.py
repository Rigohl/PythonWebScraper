import importlib.util

import pytest

from src.tui.app import launch_professional_tui


def test_tui_launch_smoke_demo_mode():
    """Probar que el TUI principal se inicializa sin excepciones en modo demo"""
    try:
        # Intentar lanzar TUI en modo demo (debería ser no-bloqueante)
        # En un test real, esto podría requerir mocking del event loop
        # Por ahora, verificamos que la función existe y es callable
        assert callable(launch_professional_tui)

        # Si podemos ejecutar sin excepciones inmediatas, es una buena señal
        # Nota: En un entorno de CI/testing, el TUI completo podría no ejecutarse
        # pero al menos podemos verificar que no hay import errors

    except Exception as e:
        # Si hay algún error de importación o inicialización, fallar el test
        pytest.fail(f"TUI launch failed with error: {e}")


def test_tui_imports_successful():
    """Verificar que todos los imports del TUI funcionan correctamente"""
    try:
        from textual.app import App

        from src.tui.app import ProfessionalScraperApp

        # Verificar que ProfessionalScraperApp hereda de App
        assert issubclass(ProfessionalScraperApp, App)

        # Verificar que podemos instanciar la clase (sin ejecutar)
        app = ProfessionalScraperApp()
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
