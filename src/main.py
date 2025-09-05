# src/main.py

import argparse
import asyncio
import logging
import sys
import os
import json

# The runner now handles logging setup, so we just import it.
from . import runner
from .database import DatabaseManager

logger = logging.getLogger(__name__)

async def main():
    """
    Main entry point for the modular web scraper.
    """
    parser = argparse.ArgumentParser(
        description="Advanced Web Scraper PRO - Sistema de scraping inteligente"
    )

    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--crawl",
        nargs="+",
        metavar="URL",
        help="One or more starting URLs for crawling.",
    )
    action_group.add_argument(
        "--tui",
        action="store_true",
        help="Launch Text User Interface (TUI) mode"
    )
    action_group.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (without Playwright)"
    )
    action_group.add_argument(
        "--export-csv",
        metavar="FILE",
        help="Export scraped data to CSV file"
    )
    action_group.add_argument(
        "--export-json",
        metavar="FILE",
        help="Export scraped data to JSON file"
    )
    action_group.add_argument(
        "--brain-snapshot",
        action="store_true",
        help="Output current (Hybrid) Brain snapshot as JSON and exit"
    )

    # Configuration arguments
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent workers (default: 5)"
    )
    parser.add_argument(
        "--db-path",
        default="data/scraper_database.db",
        help="Database file path (default: data/scraper_database.db)"
    )
    parser.add_argument(
        "--respect-robots",
        action="store_true",
        default=True,
        help="Respect robots.txt (default: True)"
    )
    parser.add_argument(
        "--use-rl",
        action="store_true",
        help="Use reinforcement learning agent"
    )

    args = parser.parse_args()

    # Handle different actions
    if args.brain_snapshot:
        await output_brain_snapshot()
    elif args.tui:
        await launch_tui()
    elif args.demo:
        await run_demo_mode()
    elif args.crawl:
        logger.info(f"Starting crawl for URLs: {args.crawl}")
        await runner.run_crawler(
            start_urls=args.crawl,
            db_path=args.db_path,
            concurrency=args.concurrency,
            respect_robots_txt=args.respect_robots,
            use_rl=args.use_rl
        )
    elif args.export_csv:
        await export_to_csv(args.export_csv, args.db_path)
    elif args.export_json:
        await export_to_json(args.export_json, args.db_path)
    else:
        logger.warning("No action specified. Use --help to see available options.")
        parser.print_help()

async def launch_tui():
    """Launch the Text User Interface"""
    try:
        # Import corrected TUI class name (was ScraperTUIApp in app.py)
        from .tui.app import ScraperTUIApp  # type: ignore
        app = ScraperTUIApp()
        await app.run_async()
    except ImportError:
        logger.error("TUI dependencies not available. Install textual: pip install textual")
        sys.exit(1)


async def output_brain_snapshot():
    """Dump current brain (hybrid if available) snapshot to stdout as JSON."""
    try:
        from .intelligence import get_intelligence_integration
        integration = get_intelligence_integration()
        brain = getattr(integration, 'brain', None)
        snapshot = {}
        if brain is not None:
            if hasattr(brain, 'get_comprehensive_stats'):
                snapshot = brain.get_comprehensive_stats()  # HybridBrain
            elif hasattr(brain, 'snapshot'):
                snapshot = brain.snapshot()  # Simple Brain
            else:
                snapshot = {"warning": "Brain object does not expose snapshot method"}
        else:
            snapshot = {"error": "No brain instance available"}
        json.dump(snapshot, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    except Exception as e:
        logger.error(f"Failed to produce brain snapshot: {e}")
        print(json.dumps({"error": str(e)}))

async def run_demo_mode():
    """Run in demo mode without Playwright"""
    logger.info("Running in demo mode...")
    demo_urls = [
        "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html"
    ]
    await runner.discover_and_run_scrapers(demo_urls)

async def export_to_csv(file_path: str, db_path: str):
    """Export scraped data to CSV (run sync export in thread)."""
    logger.info(f"Exporting data to CSV: {file_path}")
    db_manager = DatabaseManager(db_path=db_path)
    # Run blocking IO-bound export in default executor to avoid blocking event loop
    await asyncio.to_thread(db_manager.export_to_csv, file_path)
    logger.info("CSV export completed")

async def export_to_json(file_path: str, db_path: str):
    """Export scraped data to JSON (run sync export in thread)."""
    logger.info(f"Exporting data to JSON: {file_path}")
    db_manager = DatabaseManager(db_path=db_path)
    await asyncio.to_thread(db_manager.export_to_json, file_path)
    logger.info("JSON export completed")

if __name__ == "__main__":
    asyncio.run(main())
