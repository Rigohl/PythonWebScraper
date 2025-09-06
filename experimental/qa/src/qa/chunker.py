"""Chunking utilities: split documents into overlapping word chunks and
preserve parent document metadata for evidence extraction.
"""

from typing import Dict, List


def chunk_documents(
    docs: List[Dict], chunk_size: int = 40, overlap: int = 10
) -> List[Dict]:
    """Split each document in docs into chunks of ~chunk_size words with overlap.

    Returns a list of chunk dicts with fields: id, text, parent_id, title
    """
    chunks = []
    for d in docs:
        doc_id = d.get("id")
        text = d.get("text", "")
        title = d.get("title", "")
        words = [w for w in text.split() if w.strip()]
        if not words:
            continue
        i = 0
        chunk_idx = 0
        while i < len(words):
            piece = words[i : i + chunk_size]
            chunk_text = " ".join(piece)
            chunk_id = f"{doc_id}::chunk:{chunk_idx}"
            chunks.append(
                {
                    "id": chunk_id,
                    "text": chunk_text,
                    "parent_id": doc_id,
                    "title": title,
                }
            )
            chunk_idx += 1
            if i + chunk_size >= len(words):
                break
            i += chunk_size - overlap
    return chunks
