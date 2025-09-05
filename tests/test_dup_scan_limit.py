import re
from unittest.mock import patch, MagicMock

import pytest

from src.database import DatabaseManager
from src.models.results import ScrapeResult


def make_result(url: str, content: str) -> ScrapeResult:
        return ScrapeResult(
                url=url,
                status="SUCCESS",
                title=f"Title {url}",
                content_text=content,
                content_hash="hash_" + re.sub(r"\W+", "", content)[:10],
                metadata={},
                domain="example.com",
        )


def test_dup_scan_limit_sql_path(monkeypatch):
        mock_settings = MagicMock()
        mock_settings.DUP_SCAN_LIMIT = 42
        mock_settings.DUPLICATE_SIMILARITY_THRESHOLD = 0.6
        monkeypatch.setattr("src.database.settings", mock_settings)

        dbm = DatabaseManager(db_path=":memory:")

        # Patch db.query to capture SQL
        captured_sql = {}

        class DummyResultIter(list):
                pass

        def fake_query(arg):  # arg is a SQLAlchemy text object or str
                captured_sql["sql"] = str(arg)
                return DummyResultIter([])

        monkeypatch.setattr(dbm, "db", MagicMock())
        dbm.db.query = fake_query  # type: ignore
        dbm.table = MagicMock()
        dbm.table.limit.return_value = []

        r = make_result("https://example.com/a", "Sample content one")
        norm_hash = dbm._compute_normalized_hash(r)
        assert norm_hash
        dbm._check_fuzzy_duplicates(r, norm_hash)

        assert "LIMIT 42" in captured_sql["sql"], f"Expected LIMIT 42 in SQL: {captured_sql['sql']}"


def test_dup_scan_limit_dataset_fallback(monkeypatch):
        mock_settings = MagicMock()
        mock_settings.DUP_SCAN_LIMIT = 17
        mock_settings.DUPLICATE_SIMILARITY_THRESHOLD = 0.6
        monkeypatch.setattr("src.database.settings", mock_settings)

        dbm = DatabaseManager(db_path=":memory:")

        # Force query path to raise so fallback is used
        def boom(*a, **kw):
                raise Exception("no sqlalchemy")

        monkeypatch.setattr(dbm, "db", MagicMock(query=boom))
        mock_table = MagicMock()
        mock_table.limit.return_value = []
        dbm.table = mock_table

        r = make_result("https://example.com/b", "Another sample content two")
        norm_hash = dbm._compute_normalized_hash(r)
        assert norm_hash
        dbm._check_fuzzy_duplicates(r, norm_hash)

        mock_table.limit.assert_called_with(17)


@pytest.mark.asyncio
async def test_dup_scan_limit_effect_on_detection(monkeypatch):
        mock_settings = MagicMock()
        mock_settings.DUP_SCAN_LIMIT = 2
        mock_settings.DUPLICATE_SIMILARITY_THRESHOLD = 0.6
        monkeypatch.setattr("src.database.settings", mock_settings)

        dbm = DatabaseManager(db_path=":memory:")

        content1 = "Unique phrase alpha beta gamma for testing duplicates."  # base
        content2 = "Unique phrase alpha beta gamma for testing duplicates variant."  # very similar
        content3 = "Completely different unrelated text chunk."  # different
        content4 = "Unique phrase alpha beta gamma for testing duplicates variant again."  # similar to 1 & 2

        r3 = make_result("https://example.com/3", content3)
        dbm.save_result(r3)
        r2 = make_result("https://example.com/2", content2)
        dbm.save_result(r2)
        r1 = make_result("https://example.com/1", content1)
        dbm.save_result(r1)

        # Now add r4 similar to r1 & r2, but scan limit=2 means it should only scan the two most recent
        r4 = make_result("https://example.com/4", content4)
        dbm.save_result(r4)

        # r1 queda fuera de la ventana (limit=2) pero r2 sigue dentro y es similar, por lo que se marca DUPLICATE
        assert r4.status == "DUPLICATE"

        # Increase limit so older entry considered
        mock_settings.DUP_SCAN_LIMIT = 10
        r5 = make_result("https://example.com/5", content4)
        dbm.save_result(r5)
        assert r5.status == "DUPLICATE"
