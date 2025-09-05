"""
Fixtures mejorados para testing con adaptadores.

Este módulo contiene fixtures actualizados que usan los nuevos adaptadores
para mejor aislamiento y testing determinístico.
"""

import pytest
from unittest.mock import Mock
from pydantic import BaseModel, Field

from src.adapters.browser_adapter import MockBrowserAdapter
from src.adapters.llm_adapter import MockLLMAdapter
from src.database import DatabaseManager


@pytest.fixture
def mock_browser_adapter():
    """Fixture que proporciona un adaptador de navegador mock."""
    return MockBrowserAdapter(
        mock_content="<html><head><title>Test Title</title></head><body><h1>Test Title</h1><p>Test content</p></body></html>",
        mock_url="http://test.com"
    )


@pytest.fixture
def mock_llm_adapter():
    """Fixture que proporciona un adaptador LLM mock."""
    return MockLLMAdapter(mock_responses={
        "clean_text": "Test content cleaned by LLM",
        "summarize": "Test summary",
        "extract_data": None  # Will use default empty model
    })


@pytest.fixture
def mock_db_manager():
    """Fixture que proporciona un DatabaseManager mock mejorado."""
    mock_db = Mock(spec=DatabaseManager)
    mock_db.save_discovered_api = Mock()
    mock_db.load_cookies = Mock(return_value=None)
    mock_db.save_cookies = Mock()
    mock_db.save_result = Mock()
    return mock_db


class MockProduct(BaseModel):
    """Modelo mock para tests de extracción estructurada."""
    name: str = Field(default="", description="The name of the product")
    price: float = Field(default=0.0, description="The price of the product")


@pytest.fixture
def mock_product_schema():
    """Fixture que proporciona un esquema de producto mock."""
    return MockProduct
