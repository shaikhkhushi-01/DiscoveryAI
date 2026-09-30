from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.services.embeddings.base import EmbeddingProvider


@lru_cache
def _model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


class SentenceTransformerProvider(EmbeddingProvider):
    @property
    def dimension(self) -> int:
        return settings.embedding_dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = _model().encode(texts, normalize_embeddings=True)
        return vectors.tolist()
