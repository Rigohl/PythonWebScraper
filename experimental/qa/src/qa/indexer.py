"""Simple indexer: reads documents (list of dicts with id,text,title) and builds an inverted index
and stores document term frequencies. This is intentionally minimal and dependency-free.
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


class SimpleIndexer:
    def __init__(self):
        # term -> set(doc_id)
        self.inverted = defaultdict(set)
        # doc_id -> Counter(term->freq)
        self.doc_term_freq = {}
        # doc_id -> length (number of terms)
        self.doc_len = {}
        self.N = 0

    @staticmethod
    def tokenize(text: str):
        return [t.lower() for t in text.split() if t.strip()]

    def add_document(self, doc_id: str, text: str):
        tokens = self.tokenize(text)
        tf = Counter(tokens)
        self.doc_term_freq[doc_id] = tf
        self.doc_len[doc_id] = sum(tf.values())
        for term in tf:
            self.inverted[term].add(doc_id)
        self.N = len(self.doc_term_freq)

    def index_from_list(self, docs):
        for d in docs:
            self.add_document(d["id"], d.get("text", ""))

    def save(self, path: str):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf8") as f:
            json.dump(
                {
                    "inverted": {k: list(v) for k, v in self.inverted.items()},
                    "doc_term_freq": {
                        k: dict(v) for k, v in self.doc_term_freq.items()
                    },
                    "doc_len": self.doc_len,
                },
                f,
                ensure_ascii=False,
            )

    def load(self, path: str):
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf8"))
        self.inverted = defaultdict(
            set, {k: set(v) for k, v in data.get("inverted", {}).items()}
        )
        self.doc_term_freq = {
            k: Counter(v) for k, v in data.get("doc_term_freq", {}).items()
        }
        self.doc_len = {k: int(v) for k, v in data.get("doc_len", {}).items()}
        self.N = len(self.doc_term_freq)

    def idf(self, term: str):
        df = len(self.inverted.get(term, []))
        if df == 0:
            return 0.0
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1)
