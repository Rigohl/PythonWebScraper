from src.database import DatabaseManager
from src.models.results import ScrapeResult


def make_dummy_result(url: str) -> ScrapeResult:
    return ScrapeResult(
        url=url,
        status="SUCCESS",
        title="Test Page",
        content_text="Hello world",
        content_hash="abc123",
    )


def test_database_manager_save_and_load(tmp_path):
    db_file = tmp_path / "testdb.sqlite"
    db_path = str(db_file)

    manager = DatabaseManager(db_path=db_path)
    res = make_dummy_result("http://example.com/page1")
    manager.save_result(res)

    loaded = manager.get_result_by_url("http://example.com/page1")
    assert loaded is not None
    assert loaded.get("url") == "http://example.com/page1"

    # Test cookies
    manager.save_cookies("example.com", "[]")
    cookies = manager.load_cookies("example.com")
    assert cookies == "[]"

    # Test llm schema store/load
    manager.save_llm_extraction_schema("example.com", "{}")
    schema = manager.load_llm_extraction_schema("example.com")
    assert schema == "{}"


def test_database_manager_context_manager(tmp_path):
    db_file = tmp_path / "testdb2.sqlite"
    db_path = str(db_file)
    with DatabaseManager(db_path=db_path) as mgr:
        res = make_dummy_result("http://example.com/page2")
        mgr.save_result(res)
        assert mgr.get_result_by_url("http://example.com/page2") is not None

    # after exit, opening a new manager should still see the row
    mgr2 = DatabaseManager(db_path=db_path)
    assert mgr2.get_result_by_url("http://example.com/page2") is not None
