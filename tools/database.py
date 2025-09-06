#!/usr/bin/env python3
"""
Script de utilidad para interactuar con la base de datos del scraper.
Permite operaciones básicas como consultar, limpiar o exportar datos.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Añadir src al path para imports - ahora desde tools/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.db.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def query_database(db_path: str, limit: int = 10, status: str = None):
    """Consulta resultados de la base de datos."""
    try:
        db = DatabaseManager(db_path)

        if status:
            results = list(db.table.find(status=status, _limit=limit))
        else:
            results = list(db.table.all(_limit=limit))

        logger.info("Encontrados %d resultados", len(results))
        for result in results:
            print(
                json.dumps(
                    {
                        "url": result.get("url"),
                        "status": result.get("status"),
                        "title": result.get("title"),
                        "created_at": result.get("created_at"),
                    },
                    indent=2,
                    default=str,
                )
            )

    except (OSError, ValueError, KeyError) as e:
        logger.error("Error consultando base de datos: %s", e)


def clean_database(db_path: str, older_than_days: int = 30):
    """Limpia resultados antiguos de la base de datos."""
    from datetime import datetime, timedelta

    try:
        db = DatabaseManager(db_path)
        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        old_results = list(db.table.find(created_at={"$lt": cutoff_date.isoformat()}))
        logger.info("Eliminando %d resultados antiguos", len(old_results))

        for result in old_results:
            db.table.delete(id=result["id"])

        logger.info("Limpieza completada")

    except (OSError, ValueError, KeyError) as e:
        logger.error("Error limpiando base de datos: %s", e)


def export_database(db_path: str, output_file: str):
    """Exporta la base de datos a un archivo JSON."""
    try:
        db = DatabaseManager(db_path)
        results = list(db.table.all())

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("Base de datos exportada a %s", output_file)

    except (OSError, ValueError) as e:
        logger.error("Error exportando base de datos: %s", e)


def main():
    parser = argparse.ArgumentParser(
        description="Utilidad para base de datos del scraper"
    )
    parser.add_argument(
        "--db-path", default="data/scraper.db", help="Ruta a la base de datos"
    )
    parser.add_argument("--query", action="store_true", help="Consultar resultados")
    parser.add_argument("--limit", type=int, default=10, help="Límite de resultados")
    parser.add_argument("--status", help="Filtrar por status")
    parser.add_argument(
        "--clean", action="store_true", help="Limpiar resultados antiguos"
    )
    parser.add_argument(
        "--older-than", type=int, default=30, help="Días para considerar antiguos"
    )
    parser.add_argument("--export", help="Exportar a archivo JSON")

    args = parser.parse_args()

    if args.query:
        query_database(args.db_path, args.limit, args.status)
    elif args.clean:
        clean_database(args.db_path, args.older_than)
    elif args.export:
        export_database(args.db_path, args.export)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
