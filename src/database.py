import dataset
from src.models.results import ScrapeResult
import os
import json

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

    def save_result(self, result: ScrapeResult):
        """
        Guarda un ScrapeResult en la base de datos.
        Usa la URL como clave única para insertar o actualizar.
        """
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

        # Deserializa el string JSON de enlaces de vuelta a una lista
        if row and 'links' in row and row['links'] is not None:
            try:
                row['links'] = json.loads(row['links'])
            except (json.JSONDecodeError, TypeError):
                # Si hay un error o no es un string, devuelve una lista vacía
                row['links'] = []

        # Deserializar los nuevos campos
        if row and 'extracted_data' in row and row['extracted_data'] is not None:
            try:
                row['extracted_data'] = json.loads(row['extracted_data'])
            except (json.JSONDecodeError, TypeError):
                row['extracted_data'] = None
        if row and 'healing_events' in row and row['healing_events'] is not None:
            try:
                row['healing_events'] = json.loads(row['healing_events'])
            except (json.JSONDecodeError, TypeError):
                row['healing_events'] = []
        return row

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
