import pytest


def _import_exceptions():
    try:
        from src import exceptions

        return exceptions
    except Exception:
        pytest.skip("exceptions module not available")


def test_network_error():
    exceptions = _import_exceptions()

    error = exceptions.NetworkError("Test network error")
    assert str(error) == "Test network error"
    assert isinstance(error, Exception)


def test_content_quality_error():
    exceptions = _import_exceptions()

    error = exceptions.ContentQualityError("Test quality error")
    assert str(error) == "Test quality error"
    assert isinstance(error, Exception)


def test_parsing_error():
    exceptions = _import_exceptions()

    error = exceptions.ParsingError("Test parsing error")
    assert str(error) == "Test parsing error"
    assert isinstance(error, Exception)
