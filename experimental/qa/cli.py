"""Simple CLI to query the experimental QA retriever and enqueue suggestions."""

import argparse
import json

# Ensure local experimental src is importable
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from qa.brain_adapter import BrainAdapter
from qa.chunker import chunk_documents
from qa.indexer import SimpleIndexer
from qa.retriever import SimpleRetriever


def load_docs(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf8"))


def build_index_from_docs(docs):
    # chunk docs then index chunks
    chunks = chunk_documents(docs, chunk_size=40, overlap=10)
    idx = SimpleIndexer()
    idx.index_from_list(chunks)
    return idx, chunks


def main():
    parser = argparse.ArgumentParser(description="QA experimental CLI")
    parser.add_argument("query", help="Consulta a realizar")
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Enqueue suggestion based on top result (no commit)",
    )
    parser.add_argument(
        "--reader",
        action="store_true",
        help="Use extractive reader to generate an answer from top chunks (safe, offline)",
    )
    args = parser.parse_args()

    q = args.query
    docs = load_docs(Path(__file__).parent / "data" / "sample_docs.json")
    idx, chunks = build_index_from_docs(docs)
    ret = SimpleRetriever(idx)
    results = ret.retrieve(q, top_k=5)
    if not results:
        print("No results found")
        return
    for doc_id, score in results:
        doc = next((d for d in chunks if d["id"] == doc_id), None)
        title = doc.get("title") if doc else ""
        snippet = (doc.get("text")[:200] + "...") if doc else ""
        print(f"{doc_id}\tscore={score:.4f}\t{title}\n    {snippet}\n")

    if args.reader:
        # use reader to generate a short answer
        from qa.reader import SimpleReader

        reader = SimpleReader()
        # pass top chunks in original order
        top_chunks = [
            next((d for d in chunks if d["id"] == did), None) for did, _ in results
        ]
        top_chunks = [c for c in top_chunks if c]
        out = reader.answer(q, top_chunks, top_k=3)
        print("\n=== Answer (reader) ===")
        print(out.get("answer"))
        print("Evidence:")
        for e in out.get("evidence", []):
            print(f" - {e.get('id')} : {e.get('text')[:140]}...")

    if args.suggest:
        # Create a suggestion using top result
        top_id, top_score = results[0]
        top_chunk = next((d for d in chunks if d["id"] == top_id), None)
        adapter = BrainAdapter()
        payload = {
            "action": "proposed_annotation",
            "source_chunk": top_chunk,
            "suggested_by": "experimental_cli",
        }
        provenance = {"query": q, "score": float(top_score)}
        sid = adapter.enqueue_suggestion("annotation", payload, provenance)
        print(f"Suggestion enqueued id={sid} (commit disabled by default)")


if __name__ == "__main__":
    main()
