from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._model = SentenceTransformer(settings.embedding_model)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


class FallbackEmbeddingService:
    """Deterministic fallback if model loading fails (development helper)."""

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = abs(hash(text)) % (2**32)
            rng = np.random.default_rng(seed)
            vec = rng.standard_normal(settings.embedding_dim)
            vec = vec / np.linalg.norm(vec)
            vectors.append(vec.astype(float).tolist())
        return vectors


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService | FallbackEmbeddingService:
    try:
        return EmbeddingService()
    except Exception:
        return FallbackEmbeddingService()
