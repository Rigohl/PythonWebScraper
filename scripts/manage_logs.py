#!/usr/bin/env python3
"""
Log management utility script.
This script handles log file rotation and cleanup to prevent logs from consuming too much disk space.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path


def archive_old_logs(logs_dir: Path, days_to_keep: int = 30):
    """Archive logs older than the specified number of days"""
    archive_dir = logs_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    for log_file in logs_dir.glob("*.log.*"):
        # Skip if file is in archive
        if "archive" in str(log_file):
            continue

        stats = log_file.stat()
        last_modified = datetime.fromtimestamp(stats.st_mtime)

        if last_modified < cutoff_date:
            # Create year/month subdirectories in archive
            year_month = last_modified.strftime("%Y/%m")
            archive_subdir = archive_dir / year_month
            archive_subdir.mkdir(parents=True, exist_ok=True)

            # Move file to archive
            shutil.move(str(log_file), str(archive_subdir / log_file.name))


def cleanup_archives(logs_dir: Path, months_to_keep: int = 6):
    """Remove archived logs older than the specified number of months"""
    archive_dir = logs_dir / "archive"
    if not archive_dir.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=30 * months_to_keep)

    for year_dir in archive_dir.glob("*"):
        if not year_dir.is_dir():
            continue

        for month_dir in year_dir.glob("*"):
            if not month_dir.is_dir():
                continue

            dir_date = datetime.strptime(f"{year_dir.name}/{month_dir.name}", "%Y/%m")
            if dir_date < cutoff_date:
                shutil.rmtree(month_dir)

        # Remove year directory if empty
        if not any(year_dir.iterdir()):
            year_dir.rmdir()


def main():
    """Main function"""
    logs_dir = Path(__file__).parent.parent / "logs"

    if not logs_dir.exists():
        print(f"No logs directory found at {logs_dir}")
        return

    print("Starting log management...")

    # Archive old logs
    archive_old_logs(logs_dir)
    print("Archived old logs")

    # Clean up old archives
    cleanup_archives(logs_dir)
    print("Cleaned up old archives")

    print("Log management completed successfully")


if __name__ == "__main__":
    main()
