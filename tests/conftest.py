"""
pytest configuration file for shared fixtures.

This file defines fixtures that can be used across multiple test files,
promoting code reuse and simplifying test setup.
"""

import os
import shutil
import tempfile
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    """A request handler that doesn't log to the console."""
    def log_message(self, format, *args):
        pass


def run_server(server):
    """Function to run the server in a thread."""
    server.serve_forever()


@pytest.fixture(scope="session")
def http_server():
    """
    A session-scoped fixture that starts a local HTTP server in a separate
    thread to serve test HTML files.
    """
    test_dir = tempfile.mkdtemp()
    server_port = 8089

    # Create dummy HTML files
    index_html = '<html><head><title>Index</title></head><body><a href="/page1.html">Page 1</a></body></html>'
    page1_html = '<html><head><title>Page 1</title></head><body><a href="/page2.html">Page 2</a></body></html>'
    page2_html = '<html><head><title>Page 2</title></head><body>End.</body></html>'

    with open(os.path.join(test_dir, "index.html"), "w") as f: f.write(index_html)
    with open(os.path.join(test_dir, "page1.html"), "w") as f: f.write(page1_html)
    with open(os.path.join(test_dir, "page2.html"), "w") as f: f.write(page2_html)

    handler = lambda *args, **kwargs: QuietHTTPRequestHandler(*args, directory=test_dir, **kwargs)
    httpd = HTTPServer(("localhost", server_port), handler)
    server_thread = threading.Thread(target=run_server, args=(httpd,))
    server_thread.daemon = True
    server_thread.start()

    yield f"http://localhost:{server_port}"

    httpd.shutdown()
    httpd.server_close()
    server_thread.join()
    shutil.rmtree(test_dir)
