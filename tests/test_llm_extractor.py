import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel, Field

from src.llm_extractor import LLMExtractor


class MockProduct(BaseModel):
    name: str = Field(description="The name of the product")
    price: float = Field(description="The price of the product")


@pytest.fixture
def llm_extractor():
    """Fixture para el LLMExtractor con una API key de prueba."""
    with patch('src.llm_extractor.settings.LLM_API_KEY', 'test-key'):
        extractor = LLMExtractor()
    return extractor


@patch('instructor.patch')
def test_llm_extraction_logic(mock_instructor_patch, llm_extractor):
    """
    Prueba que el extractor de LLM construye el prompt correctamente y
    parsea la respuesta del LLM.
    """
    # 1. Configurar el mock del cliente de OpenAI
    mock_openai_client = Mock()
    # Simulamos que el cliente devuelve un objeto MockProduct cuando se le llama
    mock_openai_client.chat.completions.create.return_value = MockProduct(name="Test Product", price=99.99)
    mock_instructor_patch.return_value = mock_openai_client

    # 2. Definir un HTML de ejemplo y el esquema de extracción
    sample_html = "<html><body><h1>Test Product</h1><p>Price: $99.99</p></body></html>"
    extraction_schema = MockProduct

    # 3. Llamar al método a probar
    result = llm_extractor.extract(sample_html, extraction_schema)

    # 4. Verificar que el cliente fue llamado correctamente
    mock_openai_client.chat.completions.create.assert_called_once()
    call_args, call_kwargs = mock_openai_client.chat.completions.create.call_args
    # Verificamos que el HTML de ejemplo está en el prompt enviado al LLM
    assert sample_html in str(call_kwargs['messages'])
    # Verificamos que el resultado es una instancia correcta de MockProduct
    assert isinstance(result, MockProduct)
    assert result.name == "Test Product"
    assert result.price == 99.99
