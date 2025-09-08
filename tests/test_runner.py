import pytest
import asyncio
from unittest.mock import AsyncMock, patch, Mock

from src.runner import run_crawler

# NOTA: Se parchean las clases en el módulo 'runner' donde son importadas y utilizadas.
@patch('src.runner.DatabaseManager')
@patch('src.runner.UserAgentManager')
@patch('src.runner.LLMExtractor')
@patch('src.runner.RLAgent')
@patch('src.runner.ScrapingOrchestrator')
@patch('src.runner.async_playwright')
@pytest.mark.asyncio
async def test_run_crawler_basic_execution(
    mock_async_playwright, mock_orchestrator, mock_rl_agent, mock_llm_extractor,
    mock_user_agent_manager, mock_db_manager
):
    """Prueba la ejecución básica del crawler sin RL."""
    # --- Configuración del Mock de Playwright ---
    mock_pw_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_pw_instance.chromium.launch.return_value = mock_browser
    mock_async_playwright.return_value.__aenter__.return_value = mock_pw_instance

    # --- Configuración del Mock del Orquestador ---
    mock_orchestrator_instance = AsyncMock()
    mock_orchestrator.return_value = mock_orchestrator_instance

    # --- Parámetros de la prueba ---
    start_urls = ["http://test.com"]
    db_path = "test.db"
    concurrency = 5
    respect_robots_txt = True
    use_rl = False

    # --- Ejecución ---
    await run_crawler(
        start_urls=start_urls, db_path=db_path, concurrency=concurrency,
        respect_robots_txt=respect_robots_txt, use_rl=use_rl
    )

    # --- Verificaciones ---
    # Verificar que las dependencias se inicializaron
    mock_db_manager.assert_called_once_with(db_path=db_path)
    mock_user_agent_manager.assert_called_once()
    mock_llm_extractor.assert_called_once()

    # Verificar que RLAgent NO fue inicializado
    mock_rl_agent.assert_not_called()

    # Verificar que el orquestador fue inicializado con los argumentos correctos
    mock_orchestrator.assert_called_once()
    _, kwargs = mock_orchestrator.call_args
    assert kwargs['start_urls'] == start_urls
    assert kwargs['db_manager'] is mock_db_manager.return_value
    assert kwargs['rl_agent'] is None  # rl_agent debe ser None
    assert kwargs['concurrency'] == concurrency
    assert kwargs['respect_robots_txt'] is respect_robots_txt

    # Verificar que el navegador fue lanzado y cerrado
    mock_pw_instance.chromium.launch.assert_called_once_with(headless=True)
    mock_browser.close.assert_called_once()

    # Verificar que el orquestador se ejecutó
    mock_orchestrator_instance.run.assert_called_once_with(mock_browser)


@patch('src.runner.DatabaseManager')
@patch('src.runner.UserAgentManager')
@patch('src.runner.LLMExtractor')
@patch('src.runner.RLAgent')
@patch('src.runner.ScrapingOrchestrator')
@patch('src.runner.async_playwright')
@pytest.mark.asyncio
async def test_run_crawler_with_rl(
    mock_async_playwright, mock_orchestrator, mock_rl_agent, mock_llm_extractor,
    mock_user_agent_manager, mock_db_manager
):
    """Prueba que el crawler inicializa y utiliza el agente de RL cuando se le indica."""
    # --- Configuración ---
    mock_pw_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_pw_instance.chromium.launch.return_value = mock_browser
    mock_async_playwright.return_value.__aenter__.return_value = mock_pw_instance

    # --- Configuración del Mock del Orquestador ---
    mock_orchestrator_instance = AsyncMock()
    mock_orchestrator.return_value = mock_orchestrator_instance

    # --- Ejecución ---
    await run_crawler(
        start_urls=["http://test.com"], db_path="test.db", concurrency=5,
        respect_robots_txt=True, use_rl=True
    )

    # --- Verificaciones ---
    # Verificar que RLAgent FUE inicializado con los parámetros correctos
    mock_rl_agent.assert_called_once()
    _, rl_kwargs = mock_rl_agent.call_args
    assert rl_kwargs['domain'] == 'test.com'
    assert rl_kwargs['training_mode'] is True

    # Verificar que el orquestador recibió la instancia del agente
    mock_orchestrator.assert_called_once()
    _, orch_kwargs = mock_orchestrator.call_args
    assert orch_kwargs['rl_agent'] is mock_rl_agent.return_value

    # Verificar que el modelo de RL se guardó al final
    mock_rl_agent.return_value.save_model.assert_called_once()
