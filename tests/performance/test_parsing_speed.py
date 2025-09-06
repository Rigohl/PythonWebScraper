import time
from pathlib import Path

from bs4 import BeautifulSoup

from src.scrapers.example.parser import ExampleParser


def load_fixture_html() -> str:
    # Use local sample file if available; fallback to bundled test HTML
    candidates = [
        Path("data/toscrape_com_book.html"),
        Path("data") / "toscrape_com_book.html",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8", errors="ignore")
    # Minimal HTML fallback
    return """
    <html><head><title>Example</title><meta name='description' content='Sample desc'></head>
    <body><h1>Sample Title</h1><p>Body text</p></body></html>
    """


def test_example_parser_speed_smoke():
    html = load_fixture_html()
    soup = BeautifulSoup(html, "html.parser")
    parser = ExampleParser()

    # Warm-up
    parser.parse(soup)

    start = time.perf_counter()
    for _ in range(200):
        data = parser.parse(soup)
        assert isinstance(data, dict)
    elapsed = time.perf_counter() - start

    # Soft threshold to catch severe regressions but avoid flakiness
    assert elapsed < 1.5, f"Parsing loop too slow: {elapsed:.3f}s"
