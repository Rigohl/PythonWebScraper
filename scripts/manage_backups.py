#!/usr/bin/env python3
"""
Backup management utility script.
This script handles automatic backups of critical data files and databases.
"""

import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("logs/backup.log")],
    )
    return logging.getLogger(__name__)


def create_backup_name(base_name: str) -> str:
    """Create a backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}"


def backup_database(src_path: Path, backup_dir: Path, logger: logging.Logger) -> bool:
    """
    Create a backup of a SQLite database
    Returns True if backup was successful
    """
    try:
        if not src_path.exists():
            logger.error(f"Database file not found: {src_path}")
            return False

        # Create backup directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Connect to source database
        src_conn = sqlite3.connect(src_path)

        # Create backup filename
        backup_path = backup_dir / f"{create_backup_name(src_path.stem)}.db"

        # Create backup using SQLite backup API
        dst_conn = sqlite3.connect(backup_path)
        with dst_conn:
            src_conn.backup(dst_conn)

        src_conn.close()
        dst_conn.close()

        logger.info(f"Successfully backed up database {src_path.name} to {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to backup database {src_path}: {str(e)}")
        return False


def backup_json_file(src_path: Path, backup_dir: Path, logger: logging.Logger) -> bool:
    """
    Create a backup of a JSON file
    Returns True if backup was successful
    """
    try:
        if not src_path.exists():
            logger.error(f"JSON file not found: {src_path}")
            return False

        # Create backup directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create backup path
        backup_path = backup_dir / f"{create_backup_name(src_path.stem)}.json"

        # Copy file
        shutil.copy2(src_path, backup_path)

        logger.info(f"Successfully backed up {src_path.name} to {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to backup file {src_path}: {str(e)}")
        return False


def cleanup_old_backups(backup_dir: Path, max_backups: int, logger: logging.Logger):
    """Remove old backups keeping only the specified number of recent ones"""
    try:
        # Group backups by base name
        backups = {}
        for file in backup_dir.glob("*"):
            base_name = "_".join(file.stem.split("_")[:-2])  # Remove timestamp
            if base_name not in backups:
                backups[base_name] = []
            backups[base_name].append(file)

        # Sort and cleanup each group
        for base_name, files in backups.items():
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove excess backups
            for old_backup in files[max_backups:]:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup}")

    except Exception as e:
        logger.error(f"Failed to cleanup old backups: {str(e)}")


def main():
    """Main function"""
    logger = setup_logging()

    # Setup paths
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    backup_dir = root_dir / "backups" / "files"

    logger.info("Starting backup process...")

    # Critical files to backup
    files_to_backup = [
        data_dir / "brain_knowledge.db",
        data_dir / "scraper_database.db",
        data_dir / "brain_state.json",
        data_dir / "knowledge_base.json",
    ]

    backup_count = 0
    for file_path in files_to_backup:
        if not file_path.exists():
            logger.warning(f"File not found, skipping: {file_path}")
            continue

        if file_path.suffix == ".db":
            if backup_database(file_path, backup_dir, logger):
                backup_count += 1
        elif file_path.suffix == ".json":
            if backup_json_file(file_path, backup_dir, logger):
                backup_count += 1

    # Cleanup old backups
    cleanup_old_backups(backup_dir, max_backups=5, logger=logger)

    logger.info(
        f"Backup process completed. {backup_count} files backed up successfully."
    )


if __name__ == "__main__":
    main()
