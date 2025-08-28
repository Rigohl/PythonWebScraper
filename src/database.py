import dataset
from src.models.results import ScrapeResult
import os
import json
from datetime import datetime, timezone

import csv
import logging

logger = logging.getLogger(__name__)
class DatabaseManager:
    """Gestiona la comunicación con la base de datos SQLite."""

    def __init__(self, db_path: str | None = None, db_connection=None):
        """
        Inicializa y se conecta a la base de datos.
        Si se proporciona `db_connection`, se utiliza. De lo contrario,
        se crea una nueva conexión usando `db_path`.
        """
        if db_connection:
            self.db = db_connection
        elif db_path:
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.db = dataset.connect(f'sqlite:///{db_path}')
        else:
            raise ValueError("Se debe proporcionar 'db_path' o 'db_connection'.")
        self.table = self.db['pages']
        self.apis_table = self.db['discovered_apis']
        self.cookies_table = self.db['cookies']
        self.llm_schemas_table = self.db['llm_extraction_schemas'] # Added for LLM extraction schemas

    def save_discovered_api(self, page_url: str, api_url: str, payload_hash: str):
        """Guarda una API descubierta en la base de datos."""
        data = {
            "page_url": page_url,
            "api_url": api_url,
            "payload_hash": payload_hash,
            "timestamp": datetime.now(timezone.utc)
        }
        # Usar una clave compuesta para evitar duplicados exactos
        self.apis_table.upsert(data, ['page_url', 'api_url', 'payload_hash'])
        logger.info(f"API descubierta en {page_url}: {api_url}")

    def save_cookies(self, domain: str, cookies_json: str):
        """Guarda las cookies para un dominio específico."""
        data = {
            "domain": domain,
            "cookies": cookies_json,
            "timestamp": datetime.now(timezone.utc)
        }
        self.cookies_table.upsert(data, ['domain'])
        logger.debug(f"Cookies guardadas para el dominio: {domain}")

    def load_cookies(self, domain: str) -> str | None:
        """Carga las cookies para un dominio específico."""
        row = self.cookies_table.find_one(domain=domain)
        if row:
            return row['cookies']
        return None

    def save_llm_extraction_schema(self, domain: str, schema_json: str):
        """Guarda un esquema de extracción LLM para un dominio específico."""
        data = {
            "domain": domain,
            "schema": schema_json,
            "timestamp": datetime.now(timezone.utc)
        }
        self.llm_schemas_table.upsert(data, ['domain'])
        logger.debug(f"Esquema LLM guardado para el dominio: {domain}")

    def load_llm_extraction_schema(self, domain: str) -> str | None:
        """Carga un esquema de extracción LLM para un dominio específico."""
        row = self.llm_schemas_table.find_one(domain=domain)
        if row:
            return row['schema']
        return None

    def save_result(self, result: ScrapeResult):
        """
        Guarda un ScrapeResult en la base de datos.
        Usa la URL como clave única para insertar o actualizar.
        """
        # C.3: Gestión de Duplicados por Contenido
        # Si el resultado tiene un hash de contenido, comprobar si ya existe.
        if result.content_hash:
            existing = self.table.find_one(content_hash=result.content_hash)
            # Si existe y no es la misma URL (para evitar marcar como duplicado en un re-scrapeo de la misma página)
            if existing and existing['url'] != result.url:
                logger.info(f"Contenido duplicado detectado para {result.url}. Original: {existing['url']}. Marcando como DUPLICATE.")
                result.status = "DUPLICATE"

        data = result.model_dump(mode='json')

        # Serializa la lista de enlaces a un string JSON
        if 'links' in data and data['links'] is not None:
            data['links'] = json.dumps(data['links'])

        # Serializa los nuevos campos complejos a JSON
        if 'extracted_data' in data and data['extracted_data'] is not None:
            data['extracted_data'] = json.dumps(data['extracted_data'])
        if 'healing_events' in data and data['healing_events'] is not None:
            data['healing_events'] = json.dumps(data['healing_events'])

        self.table.upsert(data, ['url'])
        logger.debug(f"Resultado para {result.url} guardado en la base de datos.")

    def get_result_by_url(self, url: str) -> dict | None:
        """Recupera un resultado por su URL y deserializa los enlaces."""
        row = self.table.find_one(url=url)
        return self._deserialize_row(row) if row else None

    def export_to_csv(self, file_path: str):
        """Exporta todos los resultados con estado 'SUCCESS' a un archivo CSV."""
        # Asegurarse de que el directorio de exportación existe
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

        # find() devuelve un iterador, que procesaremos uno a uno para no cargar todo en memoria.
        results_iterator = self.table.find(status='SUCCESS')
        first_result = next(results_iterator, None)

        if not first_result:
            logger.warning("No hay datos con estado 'SUCCESS' para exportar. No se creará ningún archivo.")
            return

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Procesar el primer resultado para obtener las cabeceras
            processed_first = self._process_csv_row(first_result)
            fieldnames = processed_first.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(processed_first)

            # Procesar el resto de los resultados del iterador
            count = 1
            for row in results_iterator:
                processed_row = self._process_csv_row(row)
                # Asegurarse de que todas las filas tengan las mismas claves que la cabecera
                writer.writerow({k: processed_row.get(k) for k in fieldnames})
                count += 1

        logger.info(f"{count} registros con estado 'SUCCESS' exportados a {file_path}")

    def _process_csv_row(self, row: dict) -> dict:
        """Función helper para procesar una única fila para la exportación CSV."""
        # Esta función puede expandirse para manejar la deserialización de 'links', etc.
        if 'extracted_data' in row and row.get('extracted_data'):
            # Aplanar datos extraídos para CSV
            try:
                extracted = json.loads(row['extracted_data'])
                for field, data in extracted.items():
                    row[f"extracted_{field}"] = data.get('value')
            except (json.JSONDecodeError, TypeError):
                pass # Ignorar si no se puede parsear
        if 'extracted_data' in row:
            del row['extracted_data']
        return row

    def _deserialize_row(self, row: dict) -> dict:
        """Helper para deserializar campos JSON de una fila de la base de datos."""
        if not row:
            return row

        # Deserializa el string JSON de enlaces de vuelta a una lista
        if 'links' in row and row['links'] is not None:
            try:
                row['links'] = json.loads(row['links'])
            except (json.JSONDecodeError, TypeError):
                row['links'] = []

        # Deserializar los campos complejos
        for field in ['extracted_data', 'healing_events']:
            if field in row and row[field] is not None:
                try:
                    row[field] = json.loads(row[field])
                except (json.JSONDecodeError, TypeError):
                    row[field] = None if field == 'extracted_data' else []
        return row

    def list_results(self) -> list[dict]:
        """Devuelve una lista de todos los resultados en la base de datos."""
        all_rows = self.table.all()
        return [self._deserialize_row(row) for row in all_rows]

    def search_results(self, query: str) -> list[dict]:
        """Busca resultados que coincidan con la query en el título o contenido."""
        like_query = f'%{query}%'
        # Buscar en múltiples columnas usando _or
        results_iterator = self.table.find(_or=[
            {'title': {'like': like_query}},
            {'content_text': {'like': like_query}}
        ])
        return [self._deserialize_row(row) for row in results_iterator]

    def export_to_json(self, file_path: str):
        """Exporta todos los resultados a un archivo JSON."""
        export_dir = os.path.dirname(file_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

        results = self.list_results()
        if not results:
            logger.warning("No hay datos para exportar a JSON. No se creará ningún archivo.")
            return

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logger.info(f"{len(results)} registros exportados a {file_path}")
