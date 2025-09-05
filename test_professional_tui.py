import pytest

from src.intelligence.intent_recognizer import IntentRecognizer, IntentType


@pytest.fixture
def recognizer():
    return IntentRecognizer()


def test_edit_intent_recognition():
    # Test casos de edición en español e inglés
    test_cases = [
        (
            "Cambia 'timeout: 30' por 'timeout: 60' en config.json",
            IntentType.EDIT,
            {
                "action": "replace",
                "old_content": "timeout: 30",
                "new_content": "timeout: 60",
                "file": "config.json",
            },
        ),
        ("Edit the file config.json", IntentType.EDIT, {"file": "config.json"}),
    ]

    for text, expected_type, expected_params in test_cases:
        intent = IntentRecognizer.recognize(text)
        assert intent.type == expected_type
        for key, value in expected_params.items():
            assert intent.parameters.get(key) == value
        assert intent.confidence > 0.5


def test_terminal_intent_recognition():
    # Test casos de terminal en español e inglés
    test_cases = [
        ("Ejecuta 'dir' en el terminal", IntentType.TERMINAL, {"command": "dir"}),
        ("Run 'ls -la' in terminal", IntentType.TERMINAL, {"command": "ls -la"}),
    ]

    for text, expected_type, expected_params in test_cases:
        intent = IntentRecognizer.recognize(text)
        assert intent.type == expected_type
        for key, value in expected_params.items():
            assert intent.parameters.get(key) == value
        assert intent.confidence > 0.5


def test_search_intent_recognition():
    # Test casos de búsqueda
    test_cases = [
        (
            'Busca productos en la categoría "electronics"',
            IntentType.SEARCH,
            {"category": "electronics"},
        ),
        (
            'Search for "laptop" in category "computers"',
            IntentType.SEARCH,
            {"category": "computers"},
        ),
    ]

    for text, expected_type, expected_params in test_cases:
        intent = IntentRecognizer.recognize(text)
        assert intent.type == expected_type
        for key, value in expected_params.items():
            assert intent.parameters.get(key) == value


def test_crawl_intent_recognition():
    # Test casos de crawling
    test_cases = [
        (
            "Crawl the website 'https://example.com' with depth=2",
            IntentType.CRAWL,
            {"urls": ["https://example.com"], "depth": 2},
        ),
        (
            "Analiza el sitio https://test.com",
            IntentType.CRAWL,
            {"urls": ["https://test.com"]},
        ),
    ]

    for text, expected_type, expected_params in test_cases:
        intent = IntentRecognizer.recognize(text)
        assert intent.type == expected_type
        for key, value in expected_params.items():
            assert intent.parameters.get(key) == value


def test_snapshot_intent_recognition():
    # Test casos de snapshot
    test_cases = [
        (
            'Guarda un snapshot como "backup-2025"',
            IntentType.SNAPSHOT,
            {"name": "backup-2025"},
        ),
        (
            'Save snapshot as "checkpoint-1"',
            IntentType.SNAPSHOT,
            {"name": "checkpoint-1"},
        ),
    ]

    for text, expected_type, expected_params in test_cases:
        intent = IntentRecognizer.recognize(text)
        assert intent.type == expected_type
        for key, value in expected_params.items():
            assert intent.parameters.get(key) == value


def test_unknown_intent():
    # Test texto sin intención reconocible
    text = "Este es un texto sin intención específica"
    intent = IntentRecognizer.recognize(text)
    assert intent.type == IntentType.UNKNOWN
    assert intent.confidence == 0.0
    assert not intent.parameters


def test_invalid_inputs():
    # Test entradas inválidas
    invalid_inputs = ["", None, "   ", "\n\t"]
    for text in invalid_inputs:
        intent = IntentRecognizer.recognize(text)
        assert intent.type == IntentType.UNKNOWN
        assert intent.confidence == 0.0
        assert not intent.parameters
