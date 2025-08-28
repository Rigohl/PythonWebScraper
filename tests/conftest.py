import pytest
import os

@pytest.fixture
def html_file():
    path = os.path.join(os.path.dirname(__file__), 'test_page.html')
    return path