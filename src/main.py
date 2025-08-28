import asyncio
import argparse
import logging
import os
from src.database import DatabaseManager
from src import config
from src.runner import run_crawler

def setup_logging(log_file_path: str | None = None, tui_handler: logging.Handler | None = None):
    """Configura el sistema de logging para todo el proyecto."""
    handlers = [logging.StreamHandler()] # Por defecto, a la consola

    if log_file_path:
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file_path, mode='w'))

    if tui_handler:
        # Si estamos en la TUI, usamos su handler en lugar del de consola
        handlers = [tui_handler]
        if log_file_path:
            handlers.append(logging.FileHandler(log_file_path, mode='w'))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
    # Silenciar logs demasiado verbosos de librerías de terceros
    logging.getLogger("playwright").setLevel(logging.WARNING)

async def main():
    """
    Punto de entrada principal que configura e inicia todos los componentes.
    Este es el "Composition Root" de la aplicación.
    """
    parser = argparse.ArgumentParser(description="Web Scraper PRO - Un crawler y archivador web inteligente.")
    parser.add_argument("-db", "--db-path", type=str, default=config.DB_PATH, help=f"Ruta al archivo de la base de datos (default: {config.DB_PATH})")
    parser.add_argument("--log-file", type=str, default=config.TUI_LOG_PATH, help=f"Ruta al archivo de log (default: {config.TUI_LOG_PATH})")
    parser.add_argument("--tui", action="store_true", help="Ejecuta la aplicación en modo de Interfaz de Usuario Textual (TUI).")

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--crawl", nargs='+', metavar="URL", help="Una o más URLs de inicio para el crawling.")
    action_group.add_argument("--export-csv", metavar="FILE_PATH", help="Exporta los datos de la BD a un archivo CSV y sale.")

    parser.add_argument("-c", "--concurrency", type=int, default=config.CONCURRENCY, help=f"Número de trabajadores concurrentes (default: {config.CONCURRENCY})")
    parser.add_argument("--no-robots", action="store_true", help="Ignora las reglas del archivo robots.txt.")
    parser.add_argument("--use-rl", action="store_true", help="Activa el agente de Aprendizaje por Refuerzo para optimización dinámica.")
    args = parser.parse_args()

    # Configurar logging antes de cualquier otra cosa
    setup_logging(log_file_path=args.log_file)

    if args.tui:
        from src.tui import ScraperTUIApp
        app = ScraperTUIApp(log_file_path=args.log_file)
        await app.run_async()
        return

    if args.export_csv:
        db_manager = DatabaseManager(db_path=args.db_path)
        logging.info(f"Exportando datos a {args.export_csv}...")
        db_manager.export_to_csv(args.export_csv)
        logging.info("Exportación completada.")
        return

    if args.crawl:
        await run_crawler(
            start_urls=args.crawl,
            db_path=args.db_path,
            concurrency=args.concurrency,
            respect_robots_txt=not args.no_robots,
            use_rl=args.use_rl
        )

if __name__ == "__main__":
    asyncio.run(main())
