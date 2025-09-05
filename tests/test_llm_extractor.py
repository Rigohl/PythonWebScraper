import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel, Field

from src.intelligence.llm_extractor import LLMExtractor
from tests.fixtures_adapters import mock_llm_adapter


class MockProduct(BaseModel):
    name: str = Field(description="The name of the product")
    price: float = Field(description="The price of the product")


@pytest.fixture
def llm_extractor():
    """Fixture para el LLMExtractor con una API key de prueba."""
    with patch('src.intelligence.llm_extractor.settings.LLM_API_KEY', 'test-key'):
        extractor = LLMExtractor()
    return extractor


@pytest.mark.asyncio
async def test_llm_extraction_logic(mock_llm_adapter):
    """
    Prueba que el extractor de LLM funciona correctamente con adaptadores.
    """
    from src.llm_extractor import LLMExtractor

    # Configurar el adaptador para retornar datos mockeados
    mock_product = MockProduct(name="Test Product", price=99.99)
    mock_llm_adapter.mock_responses["extract_data"] = mock_product

    # Crear el extractor con el adaptador
    llm_extractor = LLMExtractor(adapter=mock_llm_adapter)

    # HTML de ejemplo
    sample_html = "<html><body><h1>Test Product</h1><p>Price: $99.99</p></body></html>"

    # Llamar al método de extracción
    result = await llm_extractor.extract(sample_html, MockProduct)

    # Verificar que el resultado es correcto
    assert isinstance(result, MockProduct)
    assert result.name == "Test Product"
    assert result.price == 99.99

    # Verificar que el adaptador fue llamado
    assert mock_llm_adapter.call_count > 0
