import pytest
import dataset
import os
import shutil
import tempfile
import json
import csv

from src.models.results import ScrapeResult
from src.db.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Configura una base de datos en memoria para las pruebas."""
    db_connection = dataset.connect('sqlite:///:memory:')
    manager = DatabaseManager(db_connection=db_connection)
    return manager


@pytest.fixture
def temp_test_dir():
    """Crea un directorio temporal para archivos de prueba."""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    shutil.rmtree(test_dir)


def test_save_and_get_result_with_links(db_manager):
    """Prueba que un resultado con enlaces se guarda y se recupera correctamente."""
    links_list = ["http://example.com/link1", "http://example.com/link2"]
    result = ScrapeResult(
        status="SUCCESS",
        url="http://example.com",
        title="Test Title",
        content_text="This is the content.",
        links=links_list
    )
    db_manager.save_result(result)
    retrieved = db_manager.get_result_by_url("http://example.com")

    assert retrieved is not None
    assert retrieved['title'] == "Test Title"
    assert isinstance(retrieved['links'], list)
    assert retrieved['links'] == links_list


def test_upsert_logic(db_manager):
    """Prueba que upsert actualiza un registro existente."""
    result1 = ScrapeResult(status="SUCCESS", url="http://example.com", title="First Title", links=[])
    db_manager.save_result(result1)

    result2 = ScrapeResult(status="SUCCESS", url="http://example.com", title="Updated Title", links=["http://a.com"])
    db_manager.save_result(result2)

    count = len(list(db_manager.table.all()))
    assert count == 1

    retrieved = db_manager.get_result_by_url("http://example.com")
    assert retrieved['title'] == "Updated Title"
    assert retrieved['links'] == ["http://a.com"]


def test_export_to_csv(db_manager, temp_test_dir):
    """Prueba que la exportación a CSV funciona y contiene los datos correctos."""
    result1 = ScrapeResult(status="SUCCESS", url="http://a.com", title="A", content_text="Content A", links=["http://b.com"])
    result2 = ScrapeResult(status="SUCCESS", url="http://b.com", title="B", content_text="Content B", links=[])
    result3 = ScrapeResult(status="LOW_QUALITY", url="http://c.com", title="C")
    db_manager.save_result(result1)
    db_manager.save_result(result2)
    db_manager.save_result(result3)

    test_csv_path = os.path.join(temp_test_dir, "export.csv")
    db_manager.export_to_csv(test_csv_path)

    assert os.path.exists(test_csv_path)
    with open(test_csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]['url'] == 'http://a.com'
    assert rows[0]['title'] == 'A'
    assert rows[1]['url'] == 'http://b.com'
    assert rows[1]['content_text'] == 'Content B'


def test_duplicate_content_handling(db_manager):
    """Prueba que un resultado con un content_hash existente se marca como DUPLICATE."""
    result1 = ScrapeResult(status="SUCCESS", url="http://original.com", title="Original", content_text="Unique content.", content_hash="hash123")
    db_manager.save_result(result1)

    result2 = ScrapeResult(status="SUCCESS", url="http://duplicate.com", title="Duplicate", content_text="Also unique content.", content_hash="hash123")
    db_manager.save_result(result2)

    retrieved_duplicate = db_manager.get_result_by_url("http://duplicate.com")
    assert retrieved_duplicate['status'] == "DUPLICATE"


def test_list_and_search_results(db_manager):
    """Prueba que listar y buscar resultados funciona correctamente."""
    result1 = ScrapeResult(status="SUCCESS", url="http://site.com/page1", title="Articulo sobre Python", content_text="Este es un articulo sobre Python programming", links=[])
    result2 = ScrapeResult(status="SUCCESS", url="http://site.com/page2", title="Articulo sobre Java", content_text="Este es un articulo sobre Java programming", links=[])
    result3 = ScrapeResult(status="FAILED", url="http://site.com/page3", title="Articulo fallido", content_text="Este articulo fallo", links=[])
    db_manager.save_result(result1)
    db_manager.save_result(result2)
    db_manager.save_result(result3)

    all_results = db_manager.list_results()
    assert len(all_results) == 3

    search_results = db_manager.search_results(query="Python")
    assert len(search_results) == 1
    assert search_results[0]['title'] == "Articulo sobre Python"

    empty_search = db_manager.search_results(query="GoLang")
    assert len(empty_search) == 0


def test_export_to_json(db_manager, temp_test_dir):
    """Prueba que la exportación a JSON funciona y contiene los datos correctos."""
    result1 = ScrapeResult(status="SUCCESS", url="http://a.com", title="A", content_text="Content A", extracted_data={"price": 10})
    result2 = ScrapeResult(status="SUCCESS", url="http://b.com", title="B", content_text="Content B", extracted_data={"price": 20})
    db_manager.save_result(result1)
    db_manager.save_result(result2)

    test_json_path = os.path.join(temp_test_dir, "export.json")
    db_manager.export_to_json(test_json_path)

    assert os.path.exists(test_json_path)
    with open(test_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert len(data) == 2
    assert data[0]['url'] == 'http://a.com'
    assert data[1]['extracted_data'] == {'price': 20}
