"""
Tests for the command-line interface (CLI) defined in src/main.py.

These tests ensure that the application can be launched correctly from the
command line, arguments are parsed properly, and high-level actions like
crawling and exporting work as expected.
"""

import asyncio
import os
import sys
import tempfile
import csv

import dataset
import pytest

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


async def run_cli_command(*args):
    """Helper function to run the main script as a subprocess."""
    # Use the same python executable that is running pytest
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "src.main", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()


async def test_cli_help_message():
    """Verify that the --help flag works and prints usage information."""
    return_code, stdout, stderr = await run_cli_command("--help")
    assert return_code == 0
    assert "Web Scraper PRO" in stdout
    assert "usage: main.py" in stdout


async def test_cli_crawl_and_export(http_server):
    """
    Perform an end-to-end test: crawl a site via CLI and then export the
    results to CSV via another CLI command.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as db_file, \
         tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as csv_file:

        db_path = db_file.name
        csv_path = csv_file.name

        # 1. Run the crawler via CLI
        start_url = f"{http_server}/index.html"
        return_code, stdout, stderr = await run_cli_command("--crawl", start_url, "--db-path", db_path)
        assert return_code == 0, f"Crawler process failed with stderr: {stderr}"

        # 2. Verify database content
        db = dataset.connect(f"sqlite:///{db_path}")
        assert "pages" in db.tables
        assert len(db["pages"]) == 3, "Crawler should have saved 3 pages."

        # 3. Run the export command via CLI
        return_code, stdout, stderr = await run_cli_command("--export-csv", csv_path, "--db-path", db_path)
        assert return_code == 0, f"Export process failed with stderr: {stderr}"

        # 4. Verify CSV content
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 4  # 1 header + 3 data rows
