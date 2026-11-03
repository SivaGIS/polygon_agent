"""Embeddings: turn text into vectors so that similar MEANINGS end up close together.

We use model2vec (a small, fast, CPU-only model, ~30 MB). It downloads once from Hugging Face
the first time you run it, then works offline. No API key, no cost.

In production you might use Amazon Bedrock (Titan / Cohere embeddings) or Voyage AI instead --
the idea is identical: text in, vector out.
"""
import numpy as np

MODEL_NAME = "minishlab/potion-base-8M"
_model = None


def _get_model():
    global _model
    if _model is None:
        from model2vec import StaticModel
        print(f"(loading embedding model {MODEL_NAME} -- first run downloads it, ~30 MB)")
        _model = StaticModel.from_pretrained(MODEL_NAME, force_download=False)
    return _model


def embed(texts: list[str]) -> np.ndarray:
    """Return one row per text, each scaled to length 1 (so dot product = cosine similarity)."""
    vectors = np.asarray(_get_model().encode(list(texts)), dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.where(norms == 0, 1, norms)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Similarity between two unit vectors: 1 = same meaning, ~0 = unrelated."""
    return float(np.dot(a, b))
