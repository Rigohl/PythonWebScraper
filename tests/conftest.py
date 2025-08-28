import pytest
import os
from unittest.mock import AsyncMock, Mock, patch
from src.database import DatabaseManager
from src.llm_extractor import LLMExtractor
from src.settings import settings

@pytest.fixture
def html_file():
    path = os.path.join(os.path.dirname(__file__), 'test_page.html')
    return path

@pytest.fixture
def mock_page():
    """Mock de playwright.async_api.Page."""
    mock = AsyncMock()
    mock.context = AsyncMock() # Mock the context attribute
    mock.context.cookies.return_value = [] # Default empty cookies
    yield mock

@pytest.fixture
def mock_db_manager():
    """Mock de src.database.DatabaseManager."""
    mock = Mock(spec=DatabaseManager)
    mock.load_cookies.return_value = None # Default no stored cookies
    yield mock

@pytest.fixture
def mock_llm_extractor():
    """Mock de src.llm_extractor.LLMExtractor."""
    mock = AsyncMock(spec=LLMExtractor)
    mock.clean_text_content.side_effect = lambda x: x # Default: return original text
    mock.extract_structured_data.return_value = None
    mock.summarize_content.side_effect = lambda x, y: x # Default: return original text
    yield mock

@pytest.fixture(autouse=True)
def mock_settings_min_content_length():
    with patch('src.settings.settings.MIN_CONTENT_LENGTH', 10) as mock_len:
        yield mock_len

@pytest.fixture(autouse=True)
def mock_settings_forbidden_phrases():
    with patch('src.settings.settings.FORBIDDEN_PHRASES', ["acceso denegado", "error"]) as mock_phrases:
        yield mock_phrases

@pytest.fixture(autouse=True)
def mock_settings_retryable_status_codes():
    with patch('src.settings.settings.RETRYABLE_STATUS_CODES', [429, 500]) as mock_codes:
        yield mock_codes

@pytest.fixture(autouse=True)
def mock_imagehash_phash():
    with patch('imagehash.phash') as mock:
        mock.return_value = "mock_visual_hash"
        yield mock

@pytest.fixture(autouse=True)
def mock_pil_image_open():
    with patch('PIL.Image.open') as mock:
        yield mock
