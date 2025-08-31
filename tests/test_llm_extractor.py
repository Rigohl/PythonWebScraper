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


def test_llm_extraction_logic(llm_extractor):
    """
    Prueba que el extractor de LLM construye el prompt correctamente y
    parsea la respuesta del LLM.
    """
    # TODO: Implementar este test.
    # 1. Crear un mock del cliente de OpenAI (`instructor.patch`).
    # 2. Definir un HTML de ejemplo y un esquema de extracción (MockProduct).
    # 3. Llamar a `llm_extractor.extract()`.
    # 4. Verificar que el mock del cliente de OpenAI fue llamado con un prompt
    #    que contiene el HTML y la descripción del esquema.
    # 5. Simular una respuesta del LLM y verificar que el método `extract`
    #    devuelve una instancia correcta de MockProduct.
    pytest.skip("Test para LLMExtractor aún no implementado.")
