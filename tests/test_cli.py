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
import json

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

    # To prevent deadlocks from full I/O buffers, we must read from the
    # streams concurrently while the process is running, instead of waiting
    # with .communicate(), which can block if the buffer fills up.
    async def read_stream(stream, output_list):
        """Reads a stream line by line and appends to a list."""
        while True:
            line = await stream.readline()
            if not line:
                break
            output_list.append(line.decode(errors="ignore"))

    stdout_lines = []
    stderr_lines = []

    # Create concurrent tasks to read stdout and stderr
    stdout_task = asyncio.create_task(read_stream(process.stdout, stdout_lines))
    stderr_task = asyncio.create_task(read_stream(process.stderr, stderr_lines))

    # Wait for the subprocess to finish, and for the readers to drain the streams.
    await process.wait()
    await asyncio.gather(stdout_task, stderr_task)

    return process.returncode, "".join(stdout_lines), "".join(stderr_lines)

async def test_cli_help_message():
    """Verify that the --help flag works and prints usage information."""
    return_code, stdout, stderr = await run_cli_command("--help")
    assert return_code == 0
    assert "Web Scraper PRO" in stdout
    assert "usage: main.py" in stdout


async def test_cli_no_action_prints_help():
    """Verify that running with no action prints help and exits with a warning."""
    return_code, stdout, stderr = await run_cli_command()
    assert return_code == 0
    assert "usage: main.py" in stdout
    assert "Ninguna acci" in stderr


async def test_cli_crawl_and_export(http_server):
    """
    Perform an end-to-end test: crawl a site via CLI and then export the
    results to CSV via another CLI command.
    """
    import tempfile
    import os
    
    # Use a regular temp directory that won't auto-cleanup to avoid Windows permission issues
    temp_dir = tempfile.mkdtemp(prefix="test_cli_")
    try:
        db_path = os.path.join(temp_dir, "test.db")
        csv_path = os.path.join(temp_dir, "export.csv")
        # 1. Run the crawler via CLI
        start_url = f"{http_server}/index.html"
        return_code, stdout, stderr = await run_cli_command("--crawl", start_url, "--db-path", db_path)
        assert return_code == 0, f"Crawler process failed with stderr: {stderr}"

        # 2. Verify database content
        db = dataset.connect(f"sqlite:///{db_path}")
        assert "pages" in db.tables
        assert len(db["pages"]) >= 1, "Crawler should have saved at least 1 page."

        # 3. Run the export command via CLI
        return_code, stdout, stderr = await run_cli_command("--export-csv", csv_path, "--db-path", db_path)
        assert return_code == 0, f"Export process failed with stderr: {stderr}"

        # 4. Verify CSV content
        assert os.path.exists(csv_path)
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) >= 1, "El CSV debería tener al menos 1 fila de datos."

        urls_in_csv = {row['url'] for row in rows}
        expected_url = f"{http_server}/index.html"
        assert expected_url in urls_in_csv

        index_row = next((row for row in rows if row['url'] == expected_url), None)
        assert index_row is not None
        assert index_row['title'] == "Test Site"
    finally:
        # Manual cleanup to avoid Windows permission issues
        import shutil
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


async def test_cli_crawl_and_export_json(http_server):
    """
    Perform an end-to-end test: crawl a site via CLI and then export the
    results to JSON.
    """
    import tempfile
    import os
    
    # Use a regular temp directory that won't auto-cleanup to avoid Windows permission issues
    temp_dir = tempfile.mkdtemp(prefix="test_cli_json_")
    try:
        db_path = os.path.join(temp_dir, "test.db")
        json_path = os.path.join(temp_dir, "export.json")
        start_url = f"{http_server}/index.html"
        return_code, _, stderr = await run_cli_command("--crawl", start_url, "--db-path", db_path)
        assert return_code == 0, f"Crawler process failed with stderr: {stderr}"

        return_code, _, stderr = await run_cli_command("--export-json", json_path, "--db-path", db_path)
        assert return_code == 0, f"Export process failed with stderr: {stderr}"

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) >= 1
        urls_in_json = {item['url'] for item in data}
        assert f"{http_server}/index.html" in urls_in_json
    finally:
        # Manual cleanup to avoid Windows permission issues
        import shutil
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


async def test_cli_mutually_exclusive_args():
    """Verify that providing mutually exclusive actions fails as expected."""
    return_code, stdout, stderr = await run_cli_command("--crawl", "http://a.com", "--export-csv", "b.csv")
    assert return_code != 0
    assert "not allowed with" in stderr
