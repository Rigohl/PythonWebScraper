"""Unit tests for the refactored DatabaseManager."""

import os
import json
import tempfile
import shutil
import unittest

import dataset

from src.database import DatabaseManager
from src.models.results import ScrapeResult


class TestDatabaseManager(unittest.TestCase):
    def setUp(self) -> None:
        # Create an in‑memory database for each test
        self.db_connection = dataset.connect('sqlite:///:memory:')
        self.db_manager = DatabaseManager(db_connection=self.db_connection)
        # Temporary directory for exports
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir)

    def test_save_and_retrieve_result(self):
        result = ScrapeResult(status="SUCCESS", url="http://example.com", title="Title", content_text="text", links=["http://link"])
        self.db_manager.save_result(result)
        retrieved = self.db_manager.get_result_by_url("http://example.com")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], "Title")
        self.assertEqual(retrieved['links'], ["http://link"])

    def test_duplicate_detection(self):
        original = ScrapeResult(status="SUCCESS", url="http://a.com", title="Orig", content_hash="hash")
        duplicate = ScrapeResult(status="SUCCESS", url="http://b.com", title="Dup", content_hash="hash")
        self.db_manager.save_result(original)
        self.db_manager.save_result(duplicate)
        retrieved = self.db_manager.get_result_by_url("http://b.com")
        self.assertEqual(retrieved['status'], "DUPLICATE")

    def test_export_to_csv_and_json(self):
        r1 = ScrapeResult(status="SUCCESS", url="http://x.com", title="X", content_text="content", links=["http://y.com"])
        r2 = ScrapeResult(status="SUCCESS", url="http://y.com", title="Y", content_text="content")
        self.db_manager.save_result(r1)
        self.db_manager.save_result(r2)
        csv_path = os.path.join(self.tmpdir, "out.csv")
        json_path = os.path.join(self.tmpdir, "out.json")
        self.db_manager.export_to_csv(csv_path)
        self.db_manager.export_to_json(json_path)
        # Verify CSV
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, encoding='utf-8') as f:
            rows = f.read().splitlines()
        # header + 2 rows
        self.assertTrue(len(rows) >= 3)
        # Verify JSON
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)

    def test_list_and_search_results(self):
        r1 = ScrapeResult(status="SUCCESS", url="http://p.com", title="Python article")
        r2 = ScrapeResult(status="SUCCESS", url="http://j.com", title="Java guide")
        r3 = ScrapeResult(status="FAILED", url="http://fail.com", title="Fail")
        self.db_manager.save_result(r1)
        self.db_manager.save_result(r2)
        self.db_manager.save_result(r3)
        all_results = self.db_manager.list_results()
        self.assertEqual(len(all_results), 3)
        py_results = self.db_manager.search_results("Python")
        self.assertEqual(len(py_results), 1)
        self.assertEqual(py_results[0]['title'], "Python article")


if __name__ == '__main__':
    unittest.main()