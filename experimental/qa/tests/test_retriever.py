import os
import sys

# Ensure experimental src is importable when running tests
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from qa.indexer import SimpleIndexer
from qa.retriever import SimpleRetriever


def test_index_and_retrieve_basic():
    docs = [
        {"id": "d1", "text": "Python scraping with requests and BeautifulSoup"},
        {
            "id": "d2",
            "text": "Playwright for browser automation and scraping dynamic pages",
        },
    ]
    idx = SimpleIndexer()
    idx.index_from_list(docs)
    ret = SimpleRetriever(idx)
    results = ret.retrieve("browser scraping", top_k=2)
    # Should return at least one result and include d2
    ids = [r[0] for r in results]
    assert "d2" in ids
