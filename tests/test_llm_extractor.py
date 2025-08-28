import pytest
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel
from src.llm_extractor import LLMExtractor
from src.settings import settings

# Mock settings.LLM_API_KEY for initialization
@pytest.fixture(autouse=True)
def mock_settings_llm_api_key():
    with patch('src.settings.settings.LLM_API_KEY', "test_api_key"):
        yield

# Mock settings.LLM_MODEL for API calls
@pytest.fixture(autouse=True)
def mock_settings_llm_model():
    with patch('src.settings.settings.LLM_MODEL', "test_model"):
        yield

@pytest.fixture
def llm_extractor():
    return LLMExtractor()

@pytest.fixture
def mock_openai_chat_completions_create():
    with patch('openai.resources.chat.completions.Completions.create') as mock_create:
        yield mock_create

@pytest.mark.asyncio
async def test_clean_text_content_success(llm_extractor, mock_openai_chat_completions_create):
    mock_response = AsyncMock()
    mock_response.cleaned_text = "cleaned content"
    mock_openai_chat_completions_create.return_value = mock_response

    text = "<div><p>Some content</p></div>"
    cleaned_text = await llm_extractor.clean_text_content(text)

    mock_openai_chat_completions_create.assert_called_once()
    assert cleaned_text == "cleaned content"

@pytest.mark.asyncio
async def test_clean_text_content_failure(llm_extractor, mock_openai_chat_completions_create):
    mock_openai_chat_completions_create.side_effect = Exception("API Error")

    text = "<div><p>Some content</p></div>"
    cleaned_text = await llm_extractor.clean_text_content(text)

    mock_openai_chat_completions_create.assert_called_once()
    assert cleaned_text == text # Should return original text on failure

@pytest.mark.asyncio
async def test_extract_structured_data_success(llm_extractor, mock_openai_chat_completions_create):
    class Product(BaseModel):
        name: str
        price: float

    mock_response = AsyncMock(spec=Product)
    mock_response.name = "Test Product"
    mock_response.price = 99.99
    mock_openai_chat_completions_create.return_value = mock_response

    html_content = "<html>...</html>"
    extracted_data = await llm_extractor.extract_structured_data(html_content, Product)

    mock_openai_chat_completions_create.assert_called_once()
    assert isinstance(extracted_data, Product)
    assert extracted_data.name == "Test Product"
    assert extracted_data.price == 99.99

@pytest.mark.asyncio
async def test_extract_structured_data_failure(llm_extractor, mock_openai_chat_completions_create):
    class Product(BaseModel):
        name: str
        price: float

    mock_openai_chat_completions_create.side_effect = Exception("API Error")

    html_content = "<html>...</html>"
    extracted_data = await llm_extractor.extract_structured_data(html_content, Product)

    mock_openai_chat_completions_create.assert_called_once()
    assert isinstance(extracted_data, Product) # Should return empty instance on failure
    assert extracted_data.name is None
    assert extracted_data.price is None

@pytest.mark.asyncio
async def test_extract_structured_data_dynamic_schema_success(llm_extractor, mock_openai_chat_completions_create):
    class DynamicSchema(BaseModel):
        field1: str
        field2: int

    mock_response = AsyncMock(spec=DynamicSchema)
    mock_response.model_dump.return_value = {"field1": "value1", "field2": 123}
    mock_openai_chat_completions_create.return_value = mock_response

    html_content = "<html>...</html>"
    schema_dict = {"field1": (str, ...), "field2": (int, ...)}
    extracted_data = await llm_extractor.extract_structured_data_dynamic_schema(html_content, schema_dict)

    mock_openai_chat_completions_create.assert_called_once()
    assert extracted_data == {"field1": "value1", "field2": 123}

@pytest.mark.asyncio
async def test_extract_structured_data_dynamic_schema_failure(llm_extractor, mock_openai_chat_completions_create):
    mock_openai_chat_completions_create.side_effect = Exception("API Error")

    html_content = "<html>...</html>"
    schema_dict = {"field1": (str, ...), "field2": (int, ...)}
    extracted_data = await llm_extractor.extract_structured_data_dynamic_schema(html_content, schema_dict)

    mock_openai_chat_completions_create.assert_called_once()
    assert extracted_data is None # Should return None on failure

@pytest.mark.asyncio
async def test_summarize_content_success(llm_extractor, mock_openai_chat_completions_create):
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = "summarized content"
    mock_openai_chat_completions_create.return_value = mock_response

    text_content = "Long text to summarize."
    summarized_text = await llm_extractor.summarize_content(text_content)

    mock_openai_chat_completions_create.assert_called_once()
    assert summarized_text == "summarized content"

@pytest.mark.asyncio
async def test_summarize_content_failure(llm_extractor, mock_openai_chat_completions_create):
    mock_openai_chat_completions_create.side_effect = Exception("API Error")

    text_content = "Long text to summarize."
    summarized_text = await llm_extractor.summarize_content(text_content)

    mock_openai_chat_completions_create.assert_called_once()
    assert summarized_text == text_content # Should return original text on failure

def test_llm_extractor_init_no_api_key():
    with patch('src.settings.settings.LLM_API_KEY', None):
        with pytest.raises(ValueError, match="La clave de API de LLM (LLM_API_KEY) no está configurada en los ajustes."):
            LLMExtractor()