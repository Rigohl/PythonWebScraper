# src/main.py

import argparse
import asyncio
import json
import logging
import sys
from typing import Any

# The runner now handles logging setup, so we just import it.
from . import runner
from .database import DatabaseManager

logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Main entry point for the modular web scraper.
    """
    parser = _create_argument_parser()
    args = parser.parse_args()

    # Handle different actions
    action_result = await _handle_action(args)

    if not action_result:
        # Mensaje esperado por tests: contiene 'Ninguna acci'
        logger.warning(
            "Ninguna acción especificada. Usa --help para ver opciones disponibles."
        )
        parser.print_help()


def _create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Advanced Web Scraper PRO - Sistema de scraping inteligente"
    )

    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group()
    _add_action_arguments(action_group)

    # Configuration arguments
    _add_configuration_arguments(parser)

    return parser


def _add_action_arguments(action_group: argparse._MutuallyExclusiveGroup) -> None:
    """Add action arguments to the parser

    Args:
        action_group: Mutually exclusive argument group
    """
    action_group.add_argument(
        "--crawl",
        nargs="+",
        metavar="URL",
        help="One or more starting URLs for crawling.",
    )
    action_group.add_argument(
        "--tui", action="store_true", help="Launch Text User Interface (TUI) mode"
    )
    action_group.add_argument(
        "--tui-pro",
        action="store_true",
        help="Launch Professional Dashboard TUI mode (NUEVO)",
    )
    action_group.add_argument(
        "--demo", action="store_true", help="Run in demo mode (without Playwright)"
    )
    action_group.add_argument(
        "--export-csv", metavar="FILE", help="Export scraped data to CSV file"
    )
    action_group.add_argument(
        "--export-json", metavar="FILE", help="Export scraped data to JSON file"
    )
    action_group.add_argument(
        "--export-md", metavar="FILE", help="Export scraped data to Markdown report"
    )
    action_group.add_argument(
        "--brain-snapshot",
        action="store_true",
        help="Output current (Hybrid) Brain snapshot as JSON and exit",
    )
    action_group.add_argument(
        "--query-kb", metavar="QUERY", help="Query the brain's knowledge base"
    )
    action_group.add_argument(
        "--repair-report",
        action="store_true",
        help="Generate and export the IA self-repair report",
    )


def _add_configuration_arguments(parser: argparse.ArgumentParser) -> None:
    """Add configuration arguments to the parser

    Args:
        parser: ArgumentParser instance
    """
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent workers (default: 5)",
    )
    parser.add_argument(
        "--db-path",
        default="data/scraper_database.db",
        help="Database file path (default: data/scraper_database.db)",
    )
    parser.add_argument(
        "--respect-robots",
        action="store_true",
        default=False,
        help="Respect robots.txt (default: False)",
    )
    parser.add_argument(
        "--use-rl", action="store_true", help="Use reinforcement learning agent"
    )
    parser.add_argument(
        "--hot-reload",
        action="store_true",
        help="Enable hot reloading of scraper modules",
    )


async def _handle_action(args: argparse.Namespace) -> bool:
    """Handle the parsed command line arguments

    Args:
        args: Parsed command line arguments

    Returns:
        True if an action was handled, False otherwise
    """
    if args.brain_snapshot:
        await output_brain_snapshot()
    elif args.tui:
        await launch_tui()
    elif args.tui_pro:
        await launch_professional_tui()
    elif args.demo:
        await run_demo_mode()
    elif args.crawl:
        await _handle_crawl_action(args)
    elif args.export_csv:
        await export_to_csv(args.export_csv, args.db_path)
    elif args.export_json:
        await export_to_json(args.export_json, args.db_path)
    elif args.export_md:
        await export_to_markdown(args.export_md, args.db_path)
    elif args.query_kb:
        await query_knowledge_base(args.query_kb)
    elif args.repair_report:
        await generate_repair_report()
    else:
        return False

    return True


async def _handle_crawl_action(args: argparse.Namespace) -> None:
    """Handle the crawl action with proper validation and logging

    Args:
        args: Parsed command line arguments
    """
    if not _validate_crawl_arguments(args):
        return

    logger.info("Starting crawl for URLs: %s", args.crawl)
    await runner.run_crawler(
        start_urls=args.crawl,
        db_path=args.db_path,
        concurrency=args.concurrency,
        respect_robots_txt=args.respect_robots,
        use_rl=args.use_rl,
        hot_reload=args.hot_reload,
    )


async def launch_tui() -> None:
    """Launch the Text User Interface"""
    # Check if required dependencies are available
    if not _check_tui_dependencies():
        sys.exit(1)

    # Import corrected TUI class name (was ScraperTUIApp in app.py)
    from .tui.app import ScraperTUIApp  # type: ignore

    app = ScraperTUIApp()
    await app.run_async()


async def launch_professional_tui() -> None:
    """Launch the Professional Dashboard TUI"""
    # Check if required dependencies are available
    if not _check_tui_dependencies("Professional TUI"):
        sys.exit(1)

    from .tui.professional_app import run_professional_app

    await run_professional_app()


def _check_tui_dependencies(tui_type: str = "TUI") -> bool:
    """Check if TUI dependencies are available

    Args:
        tui_type: Type of TUI being launched, used in error messages

    Returns:
        True if dependencies are available, False otherwise
    """
    try:
        # Only import textual when actually needed for the check
        __import__("textual")
        return True
    except ImportError:
        logger.error(
            "%s dependencies not available. Install textual: pip install textual",
            tui_type,
        )
        return False


async def output_brain_snapshot() -> None:
    """Dump current brain (hybrid if available) snapshot to stdout as JSON."""
    # Check if HybridBrain is available
    if not _is_module_available(".intelligence.hybrid_brain", "HybridBrain"):
        print(json.dumps({"error": "HybridBrain module not available"}))
        return

    # Import module and create brain instance
    from .intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain()

    # Get brain snapshot using the appropriate method
    snapshot = _get_brain_snapshot(brain)

    # Output the snapshot
    json.dump(snapshot, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def _is_module_available(module_path: str, class_name: str | None = None) -> bool:
    """Check if a module is available for import

    Args:
        module_path: Relative module path to import
        class_name: Optional specific class to check for

    Returns:
        True if module is available, False otherwise
    """
    try:
        module = __import__(
            module_path, globals(), locals(), [class_name] if class_name else [], 1
        )
        if class_name and not hasattr(module, class_name):
            logger.error("%s not found in %s", class_name, module_path)
            return False
        return True
    except ImportError as e:
        logger.error("%s not available: %s", module_path, e)
        return False


def _get_brain_snapshot(brain) -> dict[str, Any]:
    """Get snapshot from a brain instance using the appropriate method

    Args:
        brain: Brain instance

    Returns:
        Dictionary containing brain snapshot data
    """
    if brain is None:
        return {"error": "No brain instance available"}

    try:
        if hasattr(brain, "get_comprehensive_stats"):
            return brain.get_comprehensive_stats()
        elif hasattr(brain, "snapshot"):
            return brain.snapshot()
        else:
            return {"warning": "Brain object does not expose snapshot method"}
    except (AttributeError, RuntimeError, TypeError) as e:
        logger.error("Failed to produce brain snapshot: %s", e)
        return {"error": str(e)}


async def query_knowledge_base(query: str) -> None:
    """Queries the brain's knowledge base."""
    print(f"🧠 Consultando la Base de Conocimiento con: '{query}'")

    # Validate input
    if not query or not query.strip():
        print("\n[ERROR] La consulta no puede estar vacía.")
        return

    # Check if HybridBrain is available
    if not _is_module_available(".intelligence.hybrid_brain", "HybridBrain"):
        print(json.dumps({"error": "HybridBrain module not available"}))
        return

    # Import and initialize brain
    from .intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain()

    # Query the knowledge base
    results = _query_brain_knowledge_base(brain, query)

    # Display results
    _display_knowledge_base_results(results)


def _query_brain_knowledge_base(brain, query: str) -> list[dict[str, str]]:
    """Query the brain's knowledge base with error handling

    Args:
        brain: Brain instance
        query: Query string

    Returns:
        List of results or empty list on error
    """
    try:
        return brain.query_knowledge_base(query)
    except (AttributeError, RuntimeError, TypeError, ValueError) as e:
        logger.error("Error querying knowledge base: %s", e)
        print(json.dumps({"error": str(e)}))
        return []


def _display_knowledge_base_results(results) -> None:
    """Display knowledge base query results

    Args:
        results: List of result dictionaries
    """
    if not results:
        print("\n[INFO] No se encontraron resultados para tu consulta.")
        return

    print(f"\n[SUCCESS] Se encontraron {len(results)} resultados:\n")
    for res in results:
        print(f"  - ID: {res.get('id', 'N/A')}")
        print(f"    Titulo: {res.get('title', 'N/A')}")
        print(f"    Categoria: {res.get('category', 'N/A')}")
        print(f"    Tags: {', '.join(res.get('tags', []))}")
        print(f"    Contenido: {res.get('content', 'N/A')[:100]}...")
        print("-" * 20)


async def generate_repair_report() -> None:
    """Generates and exports the IA self-repair report."""
    print("🧠 Generando reporte de auto-reparacion y diagnostico...")

    # Check if HybridBrain is available
    if not _is_module_available(".intelligence.hybrid_brain", "HybridBrain"):
        print(json.dumps({"error": "HybridBrain module not available"}))
        return

    # Import and initialize brain
    from .intelligence.hybrid_brain import HybridBrain

    brain = HybridBrain()

    # Generate and export repair report
    success = _generate_brain_repair_report(brain)

    if success:
        print("\n[SUCCESS] Reporte de auto-reparacion generado en 'IA_SELF_REPAIR.md'")
    else:
        print("\n[ERROR] No se pudo generar el reporte de auto-reparacion")


def _generate_brain_repair_report(brain) -> bool:
    """Generate brain repair report with error handling

    Args:
        brain: Brain instance

    Returns:
        True if successful, False otherwise
    """
    try:
        brain.export_repair_report()
        return True
    except (AttributeError, RuntimeError, OSError) as e:
        logger.error("Error generating repair report: %s", e)
        print(json.dumps({"error": str(e)}))
        return False


async def run_demo_mode() -> None:
    """Run in demo mode without Playwright"""
    logger.info("Running in demo mode...")

    # Validate demo URLs
    demo_urls = [
        "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
    ]

    if not demo_urls:
        logger.error("No demo URLs configured")
        return

    await runner.discover_and_run_scrapers(demo_urls)


async def export_to_csv(file_path: str, db_path: str) -> None:
    """Export scraped data to CSV (run sync export in thread)."""
    # Validate inputs
    if not file_path or not file_path.strip():
        logger.error("File path cannot be empty")
        return

    if not db_path or not db_path.strip():
        logger.error("Database path cannot be empty")
        return

    logger.info("Exporting data to CSV: %s", file_path)

    try:
        db_manager = DatabaseManager(db_path=db_path)
        # Run blocking IO-bound export in default executor to avoid blocking event loop
        await asyncio.to_thread(db_manager.export_to_csv, file_path)
        logger.info("CSV export completed")
    except (OSError, ValueError, TypeError) as e:
        logger.error("Unexpected error during CSV export: %s", e)


async def export_to_json(file_path: str, db_path: str) -> None:
    """Export scraped data to JSON (run sync export in thread)."""
    # Validate inputs
    if not file_path or not file_path.strip():
        logger.error("File path cannot be empty")
        return

    if not db_path or not db_path.strip():
        logger.error("Database path cannot be empty")
        return

    logger.info("Exporting data to JSON: %s", file_path)

    try:
        db_manager = DatabaseManager(db_path=db_path)
        await asyncio.to_thread(db_manager.export_to_json, file_path)
        logger.info("JSON export completed")
    except (OSError, ValueError, TypeError) as e:
        logger.error("Failed to export JSON: %s", e)


async def export_to_markdown(file_path: str, db_path: str) -> None:
    """Export scraped data to a Markdown report."""
    # Validate inputs
    if not file_path or not file_path.strip():
        logger.error("File path cannot be empty")
        return

    if not db_path or not db_path.strip():
        logger.error("Database path cannot be empty")
        return

    logger.info("Exporting data to Markdown: %s", file_path)

    try:
        db_manager = DatabaseManager(db_path=db_path)
        await asyncio.to_thread(db_manager.export_to_markdown, file_path)
        logger.info("Markdown export completed")
    except (OSError, ValueError, TypeError) as e:
        logger.error("Failed to export Markdown: %s", e)


async def get_app_version() -> str:
    """Get the application version from settings."""
    from .settings import settings

    return settings.SCRAPER_VERSION


def _validate_crawl_arguments(args: argparse.Namespace) -> bool:
    """Validate crawl command arguments

    Args:
        args: Parsed command line arguments

    Returns:
        True if arguments are valid, False otherwise
    """
    if not args.crawl:
        logger.error("No URLs provided for crawling")
        return False

    for url in args.crawl:
        if not url or not url.strip():
            logger.error("Empty URL provided for crawling")
            return False

        if not url.startswith(("http://", "https://")):
            logger.error(
                "Invalid URL format: %s. Must start with http:// or https://", url
            )
            return False

    if args.concurrency < 1:
        logger.error("Concurrency must be at least 1")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(main())
