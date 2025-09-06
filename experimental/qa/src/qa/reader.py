"""Reader component: extractive reader with optional HF pipeline if installed.

If transformers is available and a model name is supplied via environment or
argument, the HF QA pipeline will be used; otherwise we fall back to returning
the best snippet from the retrieved chunks.
"""

import os
from typing import Any, Dict, List, Optional

try:
    from transformers import pipeline

    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False


class SimpleReader:
    def __init__(self, hf_model: Optional[str] = None):
        self.hf_model = hf_model
        self.hf_pipeline = None
        if hf_model and HF_AVAILABLE:
            try:
                self.hf_pipeline = pipeline(
                    "question-answering", model=hf_model, tokenizer=hf_model
                )
            except Exception:
                self.hf_pipeline = None

    def answer(
        self, question: str, chunks: List[Dict[str, Any]], top_k: int = 3
    ) -> Dict[str, Any]:
        # If HF available and pipeline ready, use it
        if self.hf_pipeline:
            # concatenate top_k chunks into context
            context = "\n\n".join([c.get("text", "") for c in chunks[:top_k]])
            try:
                out = self.hf_pipeline({"question": question, "context": context})
                return {
                    "answer": out.get("answer"),
                    "score": float(out.get("score", 0.0)),
                    "evidence": chunks[:top_k],
                }
            except Exception:
                pass
        # Fallback: return the chunk that contains most question tokens
        q_tokens = set(question.lower().split())
        best = None
        best_overlap = -1
        for c in chunks[:top_k]:
            tokens = set(c.get("text", "").lower().split())
            overlap = len(q_tokens & tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best = c
        if best is None:
            return {"answer": "", "score": 0.0, "evidence": []}
        # return snippet as answer
        snippet = best.get("text", "")[:400]
        return {"answer": snippet, "score": float(best_overlap), "evidence": [best]}
