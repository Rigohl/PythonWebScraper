#!/usr/bin/env python3
"""
Script para verificar la calidad de los datos scrapeados.
Ejecuta validaciones sobre los resultados almacenados en la base de datos.
"""

import sys
import os
from pathlib import Path

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.db.database import DatabaseManager
from src.models.results import ScrapeResult
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_quality(db_path: str = 'data/scraper.db'):
    """
    Verifica la calidad de los datos en la base de datos.
    """
    try:
        db = DatabaseManager(db_path)

        # Obtener estadísticas básicas
        total_results = db.table.count()
        successful_results = db.table.count(status='SUCCESS')
        failed_results = db.table.count(status='ERROR')

        logger.info(f"Total de resultados: {total_results}")
        logger.info(f"Resultados exitosos: {successful_results}")
        logger.info(f"Resultados fallidos: {failed_results}")

        # Verificar calidad del contenido
        results = db.table.all()
        quality_issues = []

        for result in results:
            if result.get('status') == 'SUCCESS':
                content = result.get('content_text', '')
                if len(content.strip()) < 100:
                    quality_issues.append(f"Contenido muy corto en {result.get('url')}")
                if not result.get('title'):
                    quality_issues.append(f"Título faltante en {result.get('url')}")

        if quality_issues:
            logger.warning("Problemas de calidad detectados:")
            for issue in quality_issues[:10]:  # Mostrar primeros 10
                logger.warning(f"  - {issue}")
        else:
            logger.info("No se detectaron problemas de calidad.")

        return len(quality_issues) == 0

    except Exception as e:
        logger.error(f"Error verificando calidad de datos: {e}")
        return False

if __name__ == "__main__":
    success = check_data_quality()
    sys.exit(0 if success else 1)
