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

from .database import DatabaseManager
from .settings import settings


def setup_logging(
    log_file_path: Optional[str] = None, tui_handler: Optional[logging.Handler] = None
) -> None:
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


async def _handle_tui(log_file_path: str) -> None:
    """Launch the Textual User Interface."""
    # Import lazily to avoid pulling Textual when running CLI
    from .tui.app import ScraperTUIApp

    app = ScraperTUIApp(log_file_path=log_file_path)
    await app.run_async()


def _handle_export(args: argparse.Namespace) -> None:
    """Handle data export operations."""
    db_manager = DatabaseManager(db_path=args.db_path)
    if args.export_csv:
        logging.info("Exportando datos a %s…", args.export_csv)
        db_manager.export_to_csv(args.export_csv)
    elif args.export_json:
        logging.info("Exportando datos a %s…", args.export_json)
        db_manager.export_to_json(args.export_json)


async def _handle_crawl(args: argparse.Namespace) -> None:
    """Handle the crawling process."""
    # Importing here to avoid heavy imports when not crawling
    from .runner import run_crawler  # type: ignore

    await run_crawler(
        start_urls=args.crawl,
        db_path=args.db_path,
        concurrency=args.concurrency,
        respect_robots_txt=args.respect_robots,
        use_rl=args.use_rl,
    )


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Web Scraper PRO - Un crawler y archivador web inteligente."
    )
    parser.add_argument(
        "-db",
        "--db-path",
        type=str,
        default=settings.DB_PATH,
        help=f"Ruta al archivo de la base de datos (default: {settings.DB_PATH})",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=settings.TUI_LOG_PATH,
        help=f"Ruta al archivo de log (default: {settings.TUI_LOG_PATH})",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Ejecuta la aplicación en modo de Interfaz de Usuario Textual (TUI).",
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--crawl",
        nargs="+",
        metavar="URL",
        help="Una o más URLs de inicio para el crawling.",
    )
    action_group.add_argument(
        "--export-csv",
        metavar="FILE_PATH",
        help="Exporta los datos de la BD a un archivo CSV y sale.",
    )
    action_group.add_argument(
        "--export-json",
        metavar="FILE_PATH",
        help="Exporta los datos de la BD a un archivo JSON y sale.",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=settings.CONCURRENCY,
        help=f"Número de trabajadores concurrentes (default: {settings.CONCURRENCY})",
    )
    # Robots: disable by default. --respect-robots toggles to true
    parser.add_argument(
        "--respect-robots",
        action="store_true",
        default=False,
        help="Respeta las reglas de robots.txt. Por defecto se ignoran.",
    )
    parser.add_argument(
        "--enable-ethics",
        action="store_true",
        default=settings.ETHICS_CHECKS_ENABLED,
        help="Activa comprobaciones éticas/compliance (placeholder).",
    )
    parser.add_argument(
        "--online",
        action="store_true",
        default=not settings.OFFLINE_MODE,
        help="Fuerza modo online (permite llamadas a LLM remotos).",
    )
    parser.add_argument(
        "--use-rl",
        action="store_true",
        help="Activa el agente de Aprendizaje por Refuerzo para optimización dinámica.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecuta un modo demo ligero que procesa un fichero HTML local sin requerir Playwright.",
    )
    args = parser.parse_args()
    setup_logging(log_file_path=args.log_file)

    # Propagar overrides tempranos (para la TUI también)
    settings.ROBOTS_ENABLED = args.respect_robots
    settings.ETHICS_CHECKS_ENABLED = args.enable_ethics
    settings.OFFLINE_MODE = not args.online

    if args.tui:
        await _handle_tui(args.log_file)
        return

    # Exports take precedence over crawling
    if args.export_csv or args.export_json:
        _handle_export(args)
        return

    # Launch crawler
    if args.crawl:
        await _handle_crawl(args)
        return

    # Demo mode: run a simple local-html based scraping flow without Playwright
    if args.demo:
        # Minimal demo: load local HTML and run a very small extraction path
        from pathlib import Path

        from .models.results import ScrapeResult

        demo_file = Path(__file__).resolve().parents[1] / "toscrape_com_book.html"
        if not demo_file.exists():
            logging.error("Archivo demo no encontrado: %s", str(demo_file))
            return

        html = demo_file.read_text(encoding="utf-8")

        # Very small, dependency-free extraction: grab title and first <p>
        try:
            from bs4 import BeautifulSoup
        except Exception:
            logging.error(
                "Para ejecutar el modo demo es necesario 'beautifulsoup4' en el entorno. Instálalo con: pip install beautifulsoup4"
            )
            return

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "(sin título)"
        first_p = soup.find("p")
        content = first_p.get_text(strip=True) if first_p else "(sin contenido)"

        result = ScrapeResult(
            status="SUCCESS",
            url=str(demo_file),
            title=title,
            content_text=content,
            content_html=str(first_p or ""),
            links=[a.get("href") for a in soup.find_all("a", href=True)],
            visual_hash="demo",
            content_hash="demo_hash",
            http_status_code=200,
            crawl_duration=0.0,
            content_type="DEMO",
            extracted_data=None,
            healing_events=[],
        )
        logging.info(
            "Resultado demo:\nTitle: %s\nContent snippet: %s", title, content[:200]
        )
        # Persist if DB available; also write JSON to artifacts for visibility
        wrote_to_db = False
        try:
            db = DatabaseManager(db_path=args.db_path)
            try:
                db.save_scrape_result(result)
                logging.info(
                    "Resultado demo guardado en la base de datos: %s", args.db_path
                )
                wrote_to_db = True
            except Exception as exc:  # pragma: no cover - best-effort
                logging.debug("No se pudo guardar resultado demo en BD: %s", exc)
        except Exception:
            logging.debug(
                "No se pudo inicializar DatabaseManager para persistencia demo."
            )

        # Always write a JSON fallback in artifacts so the user can inspect the demo output
        try:
            import json

            artifacts_dir = Path(__file__).resolve().parents[1] / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            demo_out = artifacts_dir / "demo_result.json"
            with demo_out.open("w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "title": title,
                        "content": content,
                        "url": str(demo_file),
                        "links": [a.get("href") for a in soup.find_all("a", href=True)],
                        "saved_to_db": wrote_to_db,
                    },
                    fh,
                    ensure_ascii=False,
                    indent=2,
                )
            logging.info("Resultado demo escrito a: %s", str(demo_out))
        except Exception as exc:  # pragma: no cover - best-effort
            logging.debug("No se pudo escribir artifacts/demo_result.json: %s", exc)
        return

    # If no action is provided, print help and exit
    parser.print_help()
    logging.warning(
        "Ninguna acción especificada (p.ej. --crawl, --export-csv, --tui). Saliendo."
    )


if __name__ == "__main__":
    asyncio.run(main())
