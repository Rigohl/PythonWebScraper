"""
Entry point for the improved Web Scraper PRO.

This module provides a command‑line interface for launching the crawler
programmatically or via a Textual TUI. It closely follows the original
project's structure while applying the following improvements:

* robots.txt checks are disabled by default. Pass ``--respect-robots`` to
  enable them.
* Logging configuration has been centralised in ``setup_logging`` and
  respects the TUI's own logging handler when running the GUI.
* Exporting results to CSV or JSON is supported via dedicated flags.

Note that ``run_crawler`` is not implemented in this minimal stub. In a full
deployment it would orchestrate the creation of ``ScrapingOrchestrator`` and
drive Playwright's lifecycle.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from typing import Optional

from .db.manager import DatabaseManager
from .settings import settings


def setup_logging(log_file_path: Optional[str] = None, tui_handler: Optional[logging.Handler] = None) -> None:
    """Configure the root logger.

    When running in the TUI, a custom handler is passed in which takes
    precedence over the default console handler.
    """
    handlers: list[logging.Handler] = []
    if tui_handler is None:
        handlers.append(logging.StreamHandler())
    else:
        handlers.append(tui_handler)
    if log_file_path:
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file_path, mode="w"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logging.getLogger("playwright").setLevel(logging.WARNING)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Web Scraper PRO - Un crawler y archivador web inteligente."
    )
    parser.add_argument(
        "-db", "--db-path", type=str, default=settings.DB_PATH, help=f"Ruta al archivo de la base de datos (default: {settings.DB_PATH})",
    )
    parser.add_argument(
        "--log-file", type=str, default=settings.TUI_LOG_PATH, help=f"Ruta al archivo de log (default: {settings.TUI_LOG_PATH})",
    )
    parser.add_argument(
        "--tui", action="store_true", help="Ejecuta la aplicación en modo de Interfaz de Usuario Textual (TUI).",
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--crawl", nargs="+", metavar="URL", help="Una o más URLs de inicio para el crawling.",
    )
    action_group.add_argument(
        "--export-csv", metavar="FILE_PATH", help="Exporta los datos de la BD a un archivo CSV y sale.",
    )
    action_group.add_argument(
        "--export-json", metavar="FILE_PATH", help="Exporta los datos de la BD a un archivo JSON y sale.",
    )
    parser.add_argument(
        "-c", "--concurrency", type=int, default=settings.CONCURRENCY, help=f"Número de trabajadores concurrentes (default: {settings.CONCURRENCY})",
    )
    # Robots: disable by default. --respect-robots toggles to true
    parser.add_argument(
        "--respect-robots", action="store_true", default=False, help="Respeta las reglas de robots.txt. Por defecto se ignoran.",
    )
    parser.add_argument(
        "--use-rl", action="store_true", help="Activa el agente de Aprendizaje por Refuerzo para optimización dinámica.",
    )
    args = parser.parse_args()
    setup_logging(log_file_path=args.log_file)

    if args.tui:
        # Import lazily to avoid pulling Textual when running CLI
        from .tui.app import ScraperTUIApp
        app = ScraperTUIApp(log_file_path=args.log_file)
        await app.run_async()
        return

    # If no high‑level action is provided, print help and exit
    if not args.crawl and not args.export_csv and not args.export_json:
        parser.print_help()
        logging.warning("Ninguna acción especificada (p.ej. --crawl, --export-csv, --export-json). Saliendo.")
        return

    # Exports take precedence over crawling
    db_manager = DatabaseManager(db_path=args.db_path)
    if args.export_csv:
        logging.info("Exportando datos a %s…", args.export_csv)
        db_manager.export_to_csv(args.export_csv)
        return
    if args.export_json:
        logging.info("Exportando datos a %s…", args.export_json)
        db_manager.export_to_json(args.export_json)
        return

    # Launch crawler via run_crawler stub
    if args.crawl:
        # Importing here to avoid heavy imports when not crawling
        from .runner import run_crawler  # type: ignore
        await run_crawler(
            start_urls=args.crawl,
            db_path=args.db_path,
            concurrency=args.concurrency,
            respect_robots_txt=args.respect_robots,
            use_rl=args.use_rl,
        )


if __name__ == "__main__":
    asyncio.run(main())
