"""A tiny vector store: the same job pgvector, Chroma or OpenSearch do, in ~40 lines.

It keeps a matrix of vectors plus the records they came from, and answers
"which records are closest in meaning to this query?"
"""
import numpy as np

from embeddings import embed


class VectorStore:
    def __init__(self):
        self.records: list[dict] = []
        self.vectors: np.ndarray | None = None

    def add(self, records: list[dict], text_key: str = "text") -> None:
        new_vectors = embed([r[text_key] for r in records])
        self.records.extend(records)
        self.vectors = new_vectors if self.vectors is None else np.vstack([self.vectors, new_vectors])

    def search(self, query: str, k: int = 5, allowed: set | None = None) -> list[tuple[float, dict]]:
        """Top-k records by meaning. `allowed` limits the search to some record ids
        (we pass the ids that passed the SPATIAL filter -- location first, then meaning)."""
        if self.vectors is None:
            return []
        scores = self.vectors @ embed([query])[0]
        order = np.argsort(-scores)
        results = []
        for i in order:
            rec = self.records[i]
            if allowed is not None and rec["id"] not in allowed:
                continue
            results.append((round(float(scores[i]), 3), rec))
            if len(results) == k:
                break
        return results
