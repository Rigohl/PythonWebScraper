#!/usr/bin/env python3
"""
Script para generar métricas del proceso de scraping.
Calcula estadísticas sobre rendimiento, calidad y cobertura.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.db.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_metrics(db_path: str = 'data/scraper.db', output_file: str = None):
    """
    Genera métricas del scraping y las guarda en un archivo JSON.
    """
    try:
        db = DatabaseManager(db_path)

        # Métricas básicas
        total_results = db.table.count()
        successful_results = db.table.count(status='SUCCESS')
        failed_results = db.table.count(status='ERROR')
        duplicate_results = db.table.count(status='DUPLICATE')

        # Métricas de rendimiento
        results = list(db.table.all())
        total_duration = 0
        content_lengths = []
        domains = defaultdict(int)

        for result in results:
            if result.get('crawl_duration'):
                total_duration += result.get('crawl_duration', 0)

            if result.get('content_text'):
                content_lengths.append(len(result.get('content_text', '')))

            # Contar por dominio
            from urllib.parse import urlparse
            domain = urlparse(result.get('url', '')).netloc
            domains[domain] += 1

        avg_duration = total_duration / len(results) if results else 0
        avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0

        # Métricas de calidad
        quality_score = successful_results / total_results if total_results > 0 else 0

        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_results': total_results,
            'successful_results': successful_results,
            'failed_results': failed_results,
            'duplicate_results': duplicate_results,
            'success_rate': quality_score,
            'average_crawl_duration': avg_duration,
            'average_content_length': avg_content_length,
            'domains_covered': dict(domains),
            'total_domains': len(domains)
        }

        logger.info("Métricas generadas:")
        logger.info(f"  Total de resultados: {total_results}")
        logger.info(f"  Tasa de éxito: {quality_score:.2%}")
        logger.info(f"  Duración promedio: {avg_duration:.2f}s")
        logger.info(f"  Longitud promedio de contenido: {avg_content_length:.0f} caracteres")
        logger.info(f"  Dominios cubiertos: {len(domains)}")

        if output_file:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, default=str)
            logger.info(f"Métricas guardadas en {output_file}")

        return metrics

    except Exception as e:
        logger.error(f"Error generando métricas: {e}")
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generar métricas del scraping')
    parser.add_argument('--db-path', default='data/scraper.db', help='Ruta a la base de datos')
    parser.add_argument('--output', help='Archivo de salida para métricas JSON')

    args = parser.parse_args()
    metrics = generate_metrics(args.db_path, args.output)

    if metrics:
        sys.exit(0)
    else:
        sys.exit(1)
