import pytest
import dataset
import os
import shutil
import tempfile
import csv
import json
from datetime import datetime, timezone

from src.models.results import ScrapeResult
from src.database import DatabaseManager

@pytest.fixture
def db_manager():
    """Configura una base de datos en memoria para cada prueba."""
    db_connection = dataset.connect('sqlite:///:memory:')
    manager = DatabaseManager(db_connection=db_connection)
    yield manager

@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para archivos de prueba y lo limpia después."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)

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

def test_init_creates_directory(temp_dir):
    """Prueba que el constructor puede ser instanciado con una base de datos en memoria."""
    db_path = os.path.join(temp_dir, "test.db")
    manager = DatabaseManager(db_path=db_path)
    assert isinstance(manager, DatabaseManager)
    assert os.path.exists(os.path.dirname(db_path))

def test_export_to_csv(db_manager, temp_dir):
    """Prueba que la exportación a CSV funciona y contiene los datos correctos."""
    result1 = ScrapeResult(status="SUCCESS", url="http://a.com", title="A", content_text="Content A", links=["http://b.com"])
    result2 = ScrapeResult(status="SUCCESS", url="http://b.com", title="B", content_text="Content B", links=[])
    result3 = ScrapeResult(status="LOW_QUALITY", url="http://c.com", title="C")
    db_manager.save_result(result1)
    db_manager.save_result(result2)
    db_manager.save_result(result3)

    test_csv_path = os.path.join(temp_dir, "export.csv")
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

def test_export_to_csv_no_data(db_manager, temp_dir):
    """Prueba que la exportación no crea un archivo si no hay datos 'SUCCESS'."""
    result = ScrapeResult(status="FAILED", url="http://c.com", title="C")
    db_manager.save_result(result)

    test_csv_path = os.path.join(temp_dir, "no_data_export.csv")
    db_manager.export_to_csv(test_csv_path)

    assert not os.path.exists(test_csv_path)

def test_save_and_get_complex_data(db_manager):
    """Prueba que los campos complejos como extracted_data y healing_events se serializan y deserializan."""
    complex_result = ScrapeResult(
        status="SUCCESS",
        url="http://complex.com",
        title="Complex Data",
        content_text="Some content",
        links=[],
        extracted_data={"price": {"value": "19.99", "selector": ".price"}},
        healing_events=[{"field": "price", "old": ".old-price", "new": ".price"}]
    )
    db_manager.save_result(complex_result)
    retrieved = db_manager.get_result_by_url("http://complex.com")

    assert retrieved is not None
    assert retrieved['extracted_data'] == {"price": {"value": "19.99", "selector": ".price"}}
    assert retrieved['healing_events'] == [{"field": "price", "old": ".old-price", "new": ".price"}]

def test_duplicate_content_handling(db_manager):
    """Prueba que un resultado con un content_hash existente se marca como DUPLICATE."""
    result1 = ScrapeResult(
        status="SUCCESS",
        url="http://original.com",
        title="Original",
        content_text="Unique content.",
        content_hash="hash123"
    )
    db_manager.save_result(result1)

    result2 = ScrapeResult(
        status="SUCCESS",
        url="http://duplicate.com",
        title="Duplicate",
        content_text="Also unique content.",
        content_hash="hash123"
    )
    db_manager.save_result(result2)

    retrieved_duplicate = db_manager.get_result_by_url("http://duplicate.com")
    assert retrieved_duplicate['status'] == "DUPLICATE"

    result3 = ScrapeResult(
        status="SUCCESS",
        url="http://original.com",
        title="Original Updated",
        content_text="Updated unique content.",
        content_hash="hash123"
    )
    db_manager.save_result(result3)
    retrieved_original = db_manager.get_result_by_url("http://original.com")
    assert retrieved_original['status'] == "SUCCESS"
    assert retrieved_original['title'] == "Original Updated"

def test_process_csv_row_with_extracted_data(db_manager):
    """Prueba que _process_csv_row aplana correctamente los datos extraídos."""
    row = {
        'id': 1,
        'url': 'http://a.com',
        'title': 'A',
        'extracted_data': '{"price": {"value": "25.50"}, "name": {"value": "Product A"}}'
    }
    processed_row = db_manager._process_csv_row(row)

    assert 'extracted_data' not in processed_row
    assert processed_row['extracted_price'] == "25.50"
    assert processed_row['extracted_name'] == "Product A"

def test_save_discovered_api(db_manager):
    db_manager.save_discovered_api("http://page.com", "http://api.com/data", "hash1")
    apis = list(db_manager.apis_table.all())
    assert len(apis) == 1
    assert apis[0]['page_url'] == "http://page.com"

def test_save_and_load_cookies(db_manager):
    db_manager.save_cookies("example.com", "{\"cookie1\":\"value1\"}")
    cookies = db_manager.load_cookies("example.com")
    assert cookies == "{\"cookie1\":\"value1\"}"

def test_save_and_load_llm_extraction_schema(db_manager):
    db_manager.save_llm_extraction_schema("example.com", "{\"schema\":\"data\"}")
    schema = db_manager.load_llm_extraction_schema("example.com")
    assert schema == "{\"schema\":\"data\"}"

def test_list_results(db_manager):
    db_manager.save_result(ScrapeResult(status="SUCCESS", url="http://1.com"))
    db_manager.save_result(ScrapeResult(status="FAILED", url="http://2.com"))
    results = db_manager.list_results()
    assert len(results) == 2
    success_results = db_manager.list_results(status_filter="SUCCESS")
    assert len(success_results) == 1

def test_search_results(db_manager):
    db_manager.save_result(ScrapeResult(status="SUCCESS", url="http://test.com/page", title="Test Page"))
    db_manager.save_result(ScrapeResult(status="SUCCESS", url="http://another.com/doc", title="Another Document"))
    search_results = db_manager.search_results("test")
    assert len(search_results) == 1
    assert search_results[0]['url'] == "http://test.com/page"

def test_export_to_json(db_manager, temp_dir):
    db_manager.save_result(ScrapeResult(status="SUCCESS", url="http://json1.com"))
    db_manager.save_result(ScrapeResult(status="FAILED", url="http://json2.com"))
    file_path = os.path.join(temp_dir, "export.json")
    db_manager.export_to_json(file_path)
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 1 # Only SUCCESS status is exported by default
    assert data[0]['url'] == "http://json1.com"

    db_manager.export_to_json(file_path, status_filter=None) # Export all
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 2