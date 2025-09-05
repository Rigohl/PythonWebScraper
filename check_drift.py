#!/usr/bin/env python3
"""
Script para detectar drift en los datos scrapeados.
Compara resultados recientes con históricos para identificar cambios significativos.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.db.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_content_drift(db_path: str = 'data/scraper.db', days_threshold: int = 7):
    """
    Detecta drift comparando contenido reciente con histórico.
    """
    try:
        db = DatabaseManager(db_path)

        # Obtener resultados de los últimos días
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        recent_results = list(db.table.find(created_at={'$gt': cutoff_date.isoformat()}))

        logger.info(f"Analizando {len(recent_results)} resultados recientes")

        drift_detected = []

        for result in recent_results:
            url = result.get('url')
            current_content = result.get('content_text', '')

            # Buscar resultados anteriores para la misma URL
            older_results = list(db.table.find(
                url=url,
                created_at={'$lt': result.get('created_at')}
            ))

            if older_results:
                # Comparar con el más reciente anterior
                prev_result = max(older_results, key=lambda x: x.get('created_at', ''))
                prev_content = prev_result.get('content_text', '')

                # Calcular similitud simple (puede mejorarse con difflib o embeddings)
                current_hash = hashlib.md5(current_content.encode()).hexdigest()
                prev_hash = hashlib.md5(prev_content.encode()).hexdigest()

                if current_hash != prev_hash:
                    drift_detected.append({
                        'url': url,
                        'change_detected': True,
                        'current_date': result.get('created_at'),
                        'previous_date': prev_result.get('created_at')
                    })

        if drift_detected:
            logger.warning(f"Drift detectado en {len(drift_detected)} URLs:")
            for drift in drift_detected[:10]:  # Mostrar primeros 10
                logger.warning(f"  - {drift['url']} cambió el {drift['current_date']}")
        else:
            logger.info("No se detectó drift significativo.")

        return len(drift_detected)

    except Exception as e:
        logger.error(f"Error detectando drift: {e}")
        return -1

if __name__ == "__main__":
    drift_count = detect_content_drift()
    if drift_count > 0:
        logger.info(f"Se detectaron {drift_count} cambios de contenido")
    sys.exit(0 if drift_count >= 0 else 1)
