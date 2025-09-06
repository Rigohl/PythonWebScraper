import tempfile

from src.database import DatabaseManager


def test_database_manager_saves_and_loads_tmp_db():
    with tempfile.TemporaryDirectory() as td:
        db_path = f"{td}/test.db"
        with DatabaseManager(db_path=db_path) as manager:
            manager.save_cookies("example.com", "[]")
            assert manager.load_cookies("example.com") == "[]"
