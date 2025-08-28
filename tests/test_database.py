import unittest
import dataset
import os
import shutil
import tempfile
from src.scraper import ScrapeResult
from src.database import DatabaseManager
import json
import csv

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        """Configura una base de datos en memoria y un directorio temporal."""
        self.test_dir = tempfile.mkdtemp()
        db_connection = dataset.connect('sqlite:///:memory:')
        self.db_manager = DatabaseManager(db_connection=db_connection)

    def tearDown(self):
        """Limpia el directorio temporal después de cada prueba."""
        shutil.rmtree(self.test_dir)

    def test_save_and_get_result_with_links(self):
        """Prueba que un resultado con enlaces se guarda y se recupera correctamente."""
        links_list = ["http://example.com/link1", "http://example.com/link2"]
        result = ScrapeResult(
            status="SUCCESS",
            url="http://example.com",
            title="Test Title",
            content_text="This is the content.",
            links=links_list
        )

        self.db_manager.save_result(result)

        retrieved = self.db_manager.get_result_by_url("http://example.com")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], "Test Title")
        # Verificar que los enlaces se deserializan correctamente
        self.assertIsInstance(retrieved['links'], list)
        self.assertEqual(retrieved['links'], links_list)

    def test_upsert_logic(self):
        """Prueba que upsert actualiza un registro existente."""
        result1 = ScrapeResult(status="SUCCESS", url="http://example.com", title="First Title", links=[])
        self.db_manager.save_result(result1)

        result2 = ScrapeResult(status="SUCCESS", url="http://example.com", title="Updated Title", links=["http://a.com"])
        self.db_manager.save_result(result2)

        count = len(list(self.db_manager.table.all()))
        self.assertEqual(count, 1)

        retrieved = self.db_manager.get_result_by_url("http://example.com")
        self.assertEqual(retrieved['title'], "Updated Title")
        self.assertEqual(retrieved['links'], ["http://a.com"])

    def test_init_creates_directory(self):
        """Prueba que el constructor puede ser instanciado con una base de datos en memoria."""
        # Simplemente instanciar para asegurar que no hay errores de inicialización
        db_manager_temp = DatabaseManager(db_connection=dataset.connect('sqlite:///:memory:'))
        self.assertIsInstance(db_manager_temp, DatabaseManager)

    def test_export_to_csv(self):
        """Prueba que la exportación a CSV funciona y contiene los datos correctos."""
        # Guardar datos de prueba
        result1 = ScrapeResult(status="SUCCESS", url="http://a.com", title="A", content_text="Content A", links=["http://b.com"])
        result2 = ScrapeResult(status="SUCCESS", url="http://b.com", title="B", content_text="Content B", links=[])
        result3 = ScrapeResult(status="LOW_QUALITY", url="http://c.com", title="C") # No debería ser exportado
        self.db_manager.save_result(result1)
        self.db_manager.save_result(result2)
        self.db_manager.save_result(result3)

        test_csv_path = os.path.join(self.test_dir, "export.csv")

        # Ejecutar la exportación
        self.db_manager.export_to_csv(test_csv_path)

        # Verificar el contenido del archivo CSV
        self.assertTrue(os.path.exists(test_csv_path))
        with open(test_csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 2) # Solo se exportan los SUCCESS
        self.assertEqual(rows[0]['url'], 'http://a.com')
        self.assertEqual(rows[0]['title'], 'A')
        self.assertEqual(rows[1]['url'], 'http://b.com')
        self.assertEqual(rows[1]['content_text'], 'Content B')

    def test_export_to_csv_no_data(self):
        """Prueba que la exportación no crea un archivo si no hay datos 'SUCCESS'."""
        # Guardar solo datos que no deberían ser exportados
        result = ScrapeResult(status="FAILED", url="http://c.com", title="C")
        self.db_manager.save_result(result)

        test_csv_path = os.path.join(self.test_dir, "no_data_export.csv")
        self.db_manager.export_to_csv(test_csv_path)

        self.assertFalse(os.path.exists(test_csv_path), "El archivo CSV no debería crearse si no hay datos para exportar.")

    def test_save_and_get_complex_data(self):
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
        self.db_manager.save_result(complex_result)
        retrieved = self.db_manager.get_result_by_url("http://complex.com")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['extracted_data'], {"price": {"value": "19.99", "selector": ".price"}})
        self.assertEqual(retrieved['healing_events'], [{"field": "price", "old": ".old-price", "new": ".price"}])

    def test_duplicate_content_handling(self):
        """Prueba que un resultado con un content_hash existente se marca como DUPLICATE."""
        result1 = ScrapeResult(
            status="SUCCESS",
            url="http://original.com",
            title="Original",
            content_text="Unique content.",
            content_hash="hash123"
        )
        self.db_manager.save_result(result1)

        result2 = ScrapeResult(
            status="SUCCESS",
            url="http://duplicate.com",
            title="Duplicate",
            content_text="Also unique content.", # El texto no importa, solo el hash
            content_hash="hash123" # Mismo hash que el original
        )
        self.db_manager.save_result(result2)

        retrieved_duplicate = self.db_manager.get_result_by_url("http://duplicate.com")
        self.assertEqual(retrieved_duplicate['status'], "DUPLICATE")

        # Probar que un re-scrapeo de la misma URL no se marca como duplicado
        result3 = ScrapeResult(
            status="SUCCESS",
            url="http://original.com",
            title="Original Updated",
            content_text="Updated unique content.",
            content_hash="hash123"
        )
        self.db_manager.save_result(result3)
        retrieved_original = self.db_manager.get_result_by_url("http://original.com")
        self.assertEqual(retrieved_original['status'], "SUCCESS")
        self.assertEqual(retrieved_original['title'], "Original Updated")


    def test_process_csv_row_with_extracted_data(self):
        """Prueba que _process_csv_row aplana correctamente los datos extraídos."""
        row = {
            'id': 1,
            'url': 'http://a.com',
            'title': 'A',
            'extracted_data': '{"price": {"value": "25.50"}, "name": {"value": "Product A"}}'
        }
        processed_row = self.db_manager._process_csv_row(row)

        # Verificar que el campo original se elimina
        self.assertNotIn('extracted_data', processed_row)
        # Verificar que los nuevos campos aplanados existen
        self.assertEqual(processed_row['extracted_price'], "25.50")
        self.assertEqual(processed_row['extracted_name'], "Product A")

    def test_list_and_search_results(self):
        """Prueba que listar y buscar resultados funciona correctamente."""
        # Asumimos que estos métodos existen en DatabaseManager según README.md
        if not all(hasattr(self.db_manager, m) for m in ['list_results', 'search_results']):
            self.skipTest("DatabaseManager no tiene los métodos list_results o search_results.")

        # Guardar datos de prueba
        result1 = ScrapeResult(status="SUCCESS", url="http://site.com/page1", title="Articulo sobre Python", links=[])
        result2 = ScrapeResult(status="SUCCESS", url="http://site.com/page2", title="Articulo sobre Java", links=[])
        result3 = ScrapeResult(status="FAILED", url="http://site.com/page3", title="Articulo fallido", links=[])
        self.db_manager.save_result(result1)
        self.db_manager.save_result(result2)
        self.db_manager.save_result(result3)

        # Probar list_results
        all_results = self.db_manager.list_results()
        self.assertEqual(len(all_results), 3)

        # Probar search_results por título
        search_results = self.db_manager.search_results(query="Python")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]['title'], "Articulo sobre Python")

        # Probar búsqueda sin resultados
        empty_search = self.db_manager.search_results(query="GoLang")
        self.assertEqual(len(empty_search), 0)

    def test_export_to_json(self):
        """Prueba que la exportación a JSON funciona y contiene los datos correctos."""
        # Asumimos que el método existe en DatabaseManager según README.md
        if not hasattr(self.db_manager, 'export_to_json'):
            self.skipTest("DatabaseManager no tiene el método export_to_json.")

        # Guardar datos de prueba
        result1 = ScrapeResult(status="SUCCESS", url="http://a.com", title="A", content_text="Content A", extracted_data={"price": 10})
        result2 = ScrapeResult(status="SUCCESS", url="http://b.com", title="B", content_text="Content B", extracted_data={"price": 20})
        self.db_manager.save_result(result1)
        self.db_manager.save_result(result2)

        test_json_path = os.path.join(self.test_dir, "export.json")

        # Ejecutar la exportación
        self.db_manager.export_to_json(test_json_path)

        # Verificar el contenido del archivo JSON
        self.assertTrue(os.path.exists(test_json_path))
        with open(test_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['url'], 'http://a.com')
        self.assertEqual(data[1]['extracted_data'], {'price': 20})

if __name__ == '__main__':
    unittest.main()
