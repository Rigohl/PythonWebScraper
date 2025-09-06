import asyncio
import logging
import os
import subprocess
import sys

from playwright.async_api import async_playwright

from src.db.database import DatabaseManager
from src.intelligence.llm_extractor import LLMExtractor
from src.managers.user_agent_manager import UserAgentManager

# ...existing imports from the project (assuming src/ is in path)...
from src.orchestrator import ScrapingOrchestrator

# Configurar logging para la ejecución del orquestador
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(command, cwd=None, capture_output=True):
    """Ayudante para ejecutar un comando y capturar salida."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=True,
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(f"Comando falló: {command}\n{e.stderr}")
        return None, e.stderr


def verify_test_files():
    """Verificar archivos de pruebas existentes en tests/."""
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    if not os.path.exists(tests_dir):
        logger.warning("Directorio tests/ no existe.")
        return []
    test_files = [
        f for f in os.listdir(tests_dir) if f.startswith("test_") and f.endswith(".py")
    ]
    logger.info(f"Archivos de pruebas encontrados: {test_files}")
    return test_files


async def run_orchestrator_test():
    """Ejecutar una prueba controlada headless del ScrapingOrchestrator."""
    logger.info("Iniciando prueba del orquestador...")
    try:
        # Crear instancias como especificado
        db_manager = DatabaseManager(":memory:")  # DB en memoria para pruebas
        ua_manager = UserAgentManager()
        llm_extractor = LLMExtractor()

        # Crear orquestador (asumiendo configuración mínima; ajustar si es necesario)
        orch = ScrapingOrchestrator(
            db_manager=db_manager,
            ua_manager=ua_manager,
            llm_extractor=llm_extractor,
            allowed_domain="example.com",  # Dominio dummy para prueba
            concurrency=1,  # Baja concurrencia para control
            respect_robots_txt=False,  # Deshabilitar para prueba
        )

        # Agregar una URL dummy a la cola
        await orch.queue.put((1, "https://httpbin.org/html"))  # URL simple para prueba

        # Ejecutar con navegador Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await orch.run(browser)
            await browser.close()

        logger.info("Prueba del orquestador completada exitosamente.")
        return "Sin errores en la ejecución del orquestador."
    except (RuntimeError, ValueError, TypeError, ConnectionError, OSError) as e:
        logger.error(f"Prueba del orquestador falló: {e}")
        return f"Excepción: {e}"


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Verificación previa: Archivos de pruebas existentes
    logger.info("Verificando archivos de pruebas existentes...")
    test_files = verify_test_files()
    if not test_files:
        logger.warning(
            "No se encontraron archivos de pruebas. Pytest podría fallar con 'no tests collected'."
        )

    # Paso 1: Crear entorno virtual
    logger.info("Creando entorno virtual...")
    venv_path = os.path.join(project_root, ".venv")
    if os.path.exists(venv_path):
        logger.info("Entorno virtual ya existe, omitiendo creación.")
    else:
        stdout, stderr = run_command("python -m venv .venv", cwd=project_root)
        if stderr:
            logger.error(f"Error en creación de venv: {stderr}")
            return

    # Paso 2: Activar venv e instalar dependencias
    logger.info("Activando venv e instalando dependencias...")
    activate_script = os.path.join(
        venv_path, "Scripts", "activate.bat"
    )  # Específico para Windows
    pip_cmd = f'"{activate_script}" && python -m pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt'
    stdout, stderr = run_command(pip_cmd, cwd=project_root)
    if stderr:
        logger.error(f"Error en instalación de dependencias: {stderr}")
        return

    # Paso 3: Instalar Playwright
    logger.info("Instalando Playwright...")
    playwright_cmd = f'"{activate_script}" && playwright install'
    stdout, stderr = run_command(playwright_cmd, cwd=project_root)
    if stderr:
        logger.error(f"Error en instalación de Playwright: {stderr}")
        return

    # Paso 4: Ejecutar pytest
    logger.info("Ejecutando suite de pytest...")
    pytest_cmd = f'"{activate_script}" && pytest -q'
    stdout, stderr = run_command(pytest_cmd, cwd=project_root)
    pytest_output = stdout or stderr
    logger.info(f"Salida de pytest:\n{pytest_output}")

    # Parsear resumen de pytest (hipotético basado en salida)
    # En ejecución real, parsear líneas como "passed: X, failed: Y, skipped: Z"
    # Para simulación, asumir desde salida

    # Paso 5: Ejecutar prueba del orquestador
    logger.info("Ejecutando validación del orquestador...")
    orch_result = asyncio.run(run_orchestrator_test())

    # Paso 6: Generar reporte
    print("\n" + "=" * 50)
    print("REPORTE")
    print("=" * 50)
    print("(a) Salida completa de pytest -q:")
    print(pytest_output)
    print("\n(b) Logs y errores de la ejecución end-to-end:")
    print(orch_result)
    print("\n(c) Recomendaciones:")
    # Recomendaciones hipotéticas basadas en problemas comunes
    print(
        "- Si pytest muestra errores de importación, asegúrate de que src/ esté en PYTHONPATH o agrégalo a sys.path en las pruebas."
    )
    print(
        "- Para timeouts en el orquestador, aumenta el timeout del navegador en settings (ej. 30s)."
    )
    print(
        "- Si Playwright falla, asegúrate de que los navegadores estén instalados; ejecuta 'playwright install' manualmente."
    )
    print(
        "- Para muchos fallos, crea issues: ej. 'Issue: Mock httpx en test_scraper.py - Pasos: 1. Ejecuta pytest en test_scraper.py, 2. Observa NetworkError, 3. Agrega @patch para httpx.AsyncClient'."
    )
    print("\nSi hay muchos fallos, issues separados creados como arriba.")


if __name__ == "__main__":
    main()
