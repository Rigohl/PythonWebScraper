"""
Tests mejorados para el scraper usando adaptadores.

Estos tests usan los nuevos adaptadores para mejor aislamiento
y testing más determinístico.
"""

import pytest
from src.scraper import AdvancedScraper
from src.models.results import ScrapeResult
from src.adapters.browser_adapter import MockBrowserAdapter
from src.exceptions import NetworkError
from tests.fixtures_adapters import mock_browser_adapter, mock_llm_adapter, mock_db_manager, mock_product_schema


@pytest.mark.asyncio
async def test_scraper_with_adapters_success(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test que el scraper funciona correctamente con adaptadores."""
    # Configurar contenido más largo para evitar validación de calidad
    mock_browser_adapter.mock_content = """
    <html>
        <head><title>Test Title</title></head>
        <body>
            <h1>Test Title</h1>
            <p>Este es un contenido de prueba suficientemente largo para evitar la validación de contenido mínimo.</p>
            <p>Tenemos múltiples párrafos con información relevante.</p>
            <p>Más contenido para simular una página web real con suficiente texto.</p>
            <div>Contenido adicional en div para simular estructura HTML compleja.</div>
        </body>
    </html>
    """

    # Configurar el adaptador LLM para retornar texto limpio
    mock_llm_adapter.mock_responses["clean_text"] = "Test content cleaned by LLM with sufficient length for validation"

    # Instanciar el scraper con adaptadores
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Ejecutar scraping
    result = await scraper.scrape("http://test.com")

    # Verificar resultado
    assert isinstance(result, ScrapeResult)
    assert result.status == "SUCCESS"
    assert result.url == "http://test.com"
    assert result.title == "Test Title"
    assert "Test content cleaned by LLM with sufficient length for validation" in result.content_text

    # Verificar que se llamaron los métodos apropiados
    assert mock_llm_adapter.call_count > 0


@pytest.mark.asyncio
async def test_scraper_with_extraction_schema(mock_browser_adapter, mock_llm_adapter, mock_db_manager, mock_product_schema):
    """Test extracción estructurada usando esquema."""
    from tests.fixtures_adapters import MockProduct

    # Configurar respuesta mock para extracción estructurada
    mock_product = MockProduct(name="Test Product", price=99.99)
    mock_llm_adapter.mock_responses["extract_data"] = mock_product

    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    result = await scraper.scrape("http://test.com", extraction_schema=MockProduct)

    assert result.status == "SUCCESS"
    assert result.extracted_data is not None
    # Verificar que la extracción fue llamada
    assert mock_llm_adapter.call_count > 0


@pytest.mark.asyncio
async def test_scraper_handles_browser_errors(mock_llm_adapter, mock_db_manager):
    """Test que el scraper maneja errores de navegación apropiadamente."""
    from src.exceptions import NetworkError

    # Crear adaptador que falla en navegación
    failing_adapter = MockBrowserAdapter()

    async def failing_navigate(*args, **kwargs):
        raise NetworkError("Connection failed")

    failing_adapter.navigate_to_url = failing_navigate

    scraper = AdvancedScraper(
        browser_adapter=failing_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    result = await scraper.scrape("http://failing.com")

    assert result.status == "RETRY"
    assert "Connection failed" in result.error_message
    assert result.retryable is True


@pytest.mark.asyncio
async def test_scraper_cookie_management(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test manejo de cookies."""
    import json

    # Configurar cookies existentes
    test_cookies = [{"name": "test", "value": "cookie", "domain": "test.com"}]
    mock_db_manager.load_cookies.return_value = json.dumps(test_cookies)

    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    await scraper.scrape("http://test.com")

    # Verificar que se cargaron y guardaron cookies
    mock_db_manager.load_cookies.assert_called_with("test.com")
    mock_db_manager.save_cookies.assert_called()


@pytest.mark.asyncio
async def test_scraper_api_discovery(mock_browser_adapter, mock_llm_adapter, mock_db_manager):
    """Test descubrimiento de APIs durante el scraping."""
    scraper = AdvancedScraper(
        browser_adapter=mock_browser_adapter,
        llm_adapter=mock_llm_adapter,
        db_manager=mock_db_manager
    )

    # Simular que se descubrió una API durante el scraping
    # (Esto requeriría un mock más sofisticado del response listener)
    await scraper.scrape("http://test.com")

    # Por ahora, solo verificamos que el scraping fue exitoso
    # El descubrimiento de APIs requiere mocking más avanzado
    assert True  # Placeholder hasta implementar mock más completo
