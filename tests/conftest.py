"""
Minimal conftest: expose fixtures defined in tests/fixtures_adapters.py
so pytest can discover them by name.
"""

import pytest

from .fixtures_adapters import *  # noqa: F401,F403


@pytest.fixture
def http_server():
    """Start a minimal local HTTP server and return its base URL."""
    import socket
    import threading
    import time
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class TestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ["/", "/index.html"]:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
				<!DOCTYPE html>
				<html>
				<head><title>Test Site</title></head>
				<body>
					<h1>Test Site</h1>
					<a href="/page1.html">Page 1</a>
					<a href="/page2.html">Page 2</a>
				</body>
				</html>
				""")
            elif self.path == "/page1.html":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
				<!DOCTYPE html>
				<html>
				<head><title>Page 1</title></head>
				<body>
					<h1>Page 1</h1>
					<p>This is page 1 content.</p>
				</body>
				</html>
				""")
            elif self.path == "/page2.html":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
				<!DOCTYPE html>
				<html>
				<head><title>Page 2</title></head>
				<body>
					<h1>Page 2</h1>
					<p>This is page 2 content.</p>
				</body>
				</html>
				""")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Page not found")

        def log_message(self, format, *args):
            # Suppress server logs
            pass

    # Find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    server = HTTPServer(("localhost", port), TestHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(0.05)

    base_url = f"http://localhost:{port}"

    try:
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=1.0)
