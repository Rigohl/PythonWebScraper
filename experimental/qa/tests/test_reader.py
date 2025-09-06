import os
import sys

# Ensure local experimental src is importable
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from qa.reader import SimpleReader


def test_reader_fallback():
    reader = SimpleReader()
    chunks = [
        {
            "id": "c1",
            "text": "Playwright permite automatizar navegadores. Es útil para páginas dinámicas.",
        },
        {
            "id": "c2",
            "text": "Python es excelente para web scraping. BeautifulSoup y requests son comunes.",
        },
    ]
    out = reader.answer("¿Qué herramienta para automatizar navegadores?", chunks)
    assert out.get("answer")
    assert len(out.get("evidence", [])) >= 1


def test_reader_hf_opt_in_env(monkeypatch):
    # If HF not available this will return fallback; ensure creating with env var does not crash
    monkeypatch.setenv("QA_HF_MODEL", "distilbert-base-cased-distilled-squad")
    reader = SimpleReader(hf_model=os.getenv("QA_HF_MODEL"))
    chunks = [
        {"id": "c1", "text": "Playwright permite automatizar navegadores."},
    ]
    out = reader.answer("automatizar navegadores", chunks)
    assert out is not None
