"""
Entry point for Web Scraper PRO with CLI and TUI interfaces.

This module provides the main command-line interface for launching the crawler
programmatically or via a Textual TUI. It supports multiple operation modes:

Features:
* Crawling mode: Scrapes websites using configurable concurrency and options
* Export mode: Exports stored data to CSV or JSON formats
* Demo mode: Runs a lightweight scraping demo using local HTML files
* TUI mode: Launches an interactive text-based user interface
* Comprehensive logging: Configurable logging with file and console output

Configuration:
* robots.txt checks are disabled by default (use --respect-robots to enable)
* Supports both online and offline modes
* Configurable database paths and concurrency settings
* Optional reinforcement learning agent integration

The module orchestrates dependency injection and manages the complete
application lifecycle from argument parsing to execution cleanup.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from typing import Optional

from .database import DatabaseManager
from .settings import settings


def setup_logging(
    log_file_path: Optional[str] = None, tui_handler: Optional[logging.Handler] = None
) -> None:
    """Configure the root logger with appropriate handlers.

    Sets up logging configuration for both console and file output. When
    running in TUI mode, uses the provided TUI handler instead of the default
    console handler to prevent output conflicts.

    Args:
        log_file_path: Optional path for log file output. Creates directories if needed.
        tui_handler: Optional custom handler for TUI mode to redirect log output.

    Note:
        Playwright logging is automatically reduced to WARNING level to minimize noise.
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
    """Handle data export operations to CSV or JSON formats.

    Args:
        args: Parsed command line arguments containing export configuration.

    Note:
        Exports are mutually exclusive - only one format can be exported at a time.
    """
    db_manager = DatabaseManager(db_path=args.db_path)
    if args.export_csv:
        logging.info("Exporting data to %s...", args.export_csv)
        db_manager.export_to_csv(args.export_csv)
    elif args.export_json:
        logging.info("Exporting data to %s...", args.export_json)
        db_manager.export_to_json(args.export_json)


async def _handle_crawl(args: argparse.Namespace) -> None:
    """Handle the crawling process with configured parameters.

    Args:
        args: Parsed command line arguments containing crawling configuration
              including URLs, concurrency settings, and behavior flags.

    Note:
        Imports run_crawler lazily to avoid heavy dependencies when not needed.
    """
    # Validate inputs
    if not args.crawl:
        raise ValueError("No URLs provided for crawling.")

    if args.concurrency <= 0:
        raise ValueError("Concurrency must be a positive integer.")

    if not args.db_path:
        raise ValueError("Database path cannot be empty.")

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
    """Main entry point for Web Scraper PRO application.

    Parses command line arguments and routes execution to appropriate handlers
    based on the selected operation mode (crawl, export, TUI, or demo).

    Operation modes:
    * --crawl: Scrapes specified URLs with full browser automation
    * --export-csv/--export-json: Exports stored data to specified format
    * --tui: Launches interactive text-based user interface
    * --demo: Runs lightweight demo using local HTML file
    * (default): Shows help if no operation specified

    Global settings are applied early to propagate throughout the application.
    """
    parser = argparse.ArgumentParser(
        description="Web Scraper PRO - Intelligent web crawler and archiver."
    )
    parser.add_argument(
        "-db",
        "--db-path",
        type=str,
        default=settings.DB_PATH,
        help=f"Path to database file (default: {settings.DB_PATH})",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=settings.TUI_LOG_PATH,
        help=f"Path to log file (default: {settings.TUI_LOG_PATH})",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Run application in Textual User Interface (TUI) mode.",
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--crawl",
        nargs="+",
        metavar="URL",
        help="One or more starting URLs for crawling.",
    )
    action_group.add_argument(
        "--export-csv",
        metavar="FILE_PATH",
        help="Export database data to CSV file and exit.",
    )
    action_group.add_argument(
        "--export-json",
        metavar="FILE_PATH",
        help="Export database data to JSON file and exit.",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=settings.CONCURRENCY,
        help=f"Number of concurrent workers (default: {settings.CONCURRENCY})",
    )
    # Robots: disable by default. --respect-robots toggles to true
    parser.add_argument(
        "--respect-robots",
        action="store_true",
        default=False,
        help="Respect robots.txt rules. Ignored by default.",
    )
    parser.add_argument(
        "--enable-ethics",
        action="store_true",
        default=settings.ETHICS_CHECKS_ENABLED,
        help="Enable ethical/compliance checks (placeholder feature).",
    )
    parser.add_argument(
        "--online",
        action="store_true",
        default=not settings.OFFLINE_MODE,
        help="Force online mode (allows remote LLM calls).",
    )
    parser.add_argument(
        "--use-rl",
        action="store_true",
        help="Enable Reinforcement Learning agent for dynamic optimization.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run lightweight demo mode processing a local HTML file without Playwright.",
    )
    args = parser.parse_args()
    setup_logging(log_file_path=args.log_file)

    # Apply early setting overrides (propagated throughout application)
    settings.ROBOTS_ENABLED = args.respect_robots
    settings.ETHICS_CHECKS_ENABLED = args.enable_ethics
    settings.OFFLINE_MODE = not args.online

    try:
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
                logging.error("Demo file not found: %s", str(demo_file))
                return

            html = demo_file.read_text(encoding="utf-8")

            # Very small, dependency-free extraction: grab title and first <p>
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logging.error(
                    "Demo mode requires 'beautifulsoup4'. Install with: pip install beautifulsoup4"
                )
                return

            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string if soup.title else "(no title)"
            first_p = soup.find("p")
            content = first_p.get_text(strip=True) if first_p else "(no content)"

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
                "Demo result:\nTitle: %s\nContent snippet: %s", title, content[:200]
            )
            # Persist if DB available; also write JSON to artifacts for visibility
            wrote_to_db = False
            try:
                db = DatabaseManager(db_path=args.db_path)
                try:
                    db.save_scrape_result(result)
                    logging.info(
                        "Demo result saved to database: %s", args.db_path
                    )
                    wrote_to_db = True
                except Exception as exc:  # pragma: no cover - best-effort
                    logging.debug("Could not save demo result to DB: %s", exc)
            except Exception:
                logging.debug(
                    "Could not initialize DatabaseManager for demo persistence."
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
                logging.info("Demo result written to: %s", str(demo_out))
            except Exception as exc:  # pragma: no cover - best-effort
                logging.debug("Could not write artifacts/demo_result.json: %s", exc)
            return

        # If no action is provided, print help and exit
        parser.print_help()
        # Mensaje traducido al español para pruebas
        logging.warning(
            "Ninguna acción especificada (p. ej., --crawl, --export-csv, --tui). Saliendo."
        )
    except ValueError as e:
        logging.error("Validation error: %s", e)
        sys.exit(1)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
