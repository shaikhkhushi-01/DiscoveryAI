from functools import lru_cache

import torch
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.services.embeddings.base import EmbeddingProvider


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    # Keep CPU thread pools small on memory-constrained API instances.
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        # PyTorch may already have initialized its inter-op pool.
        pass
    model = SentenceTransformer(settings.embedding_model, device="cpu")
    model.eval()
    return model


class SentenceTransformerProvider(EmbeddingProvider):
    @property
    def dimension(self) -> int:
        return settings.embedding_dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        # Small batches cap temporary activation memory; indexing itself is
        # serialized by services.indexing._INDEXING_LOCK.
        vectors = _model().encode(
            texts,
            batch_size=1,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vectors.tolist()
