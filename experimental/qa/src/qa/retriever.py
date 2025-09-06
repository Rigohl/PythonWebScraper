"""Simple BM25-like retriever using the SimpleIndexer above."""

import math
from typing import Dict, List, Tuple

from .indexer import SimpleIndexer


class SimpleRetriever:
    def __init__(self, indexer: SimpleIndexer, k1: float = 1.5, b: float = 0.75):
        self.indexer = indexer
        self.k1 = k1
        self.b = b

    @staticmethod
    def tokenize(text: str):
        return [t.lower() for t in text.split() if t.strip()]

    def avg_doc_len(self):
        if not self.indexer.doc_len:
            return 0
        return sum(self.indexer.doc_len.values()) / len(self.indexer.doc_len)

    def score(self, q_terms: List[str], doc_id: str, avgdl: float):
        score = 0.0
        tf_doc = self.indexer.doc_term_freq.get(doc_id, {})
        dl = self.indexer.doc_len.get(doc_id, 0)
        for term in q_terms:
            if term not in tf_doc:
                continue
            idf = self.indexer.idf(term)
            tf = tf_doc[term]
            denom = tf + self.k1 * (1 - self.b + self.b * dl / avgdl)
            score += idf * (tf * (self.k1 + 1)) / (denom + 1e-9)
        return score

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        q_terms = self.tokenize(query)
        candidates = set()
        for t in q_terms:
            candidates.update(self.indexer.inverted.get(t, set()))
        avgdl = self.avg_doc_len() or 1.0
        scored = []
        for doc_id in candidates:
            s = self.score(q_terms, doc_id, avgdl)
            scored.append((doc_id, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
