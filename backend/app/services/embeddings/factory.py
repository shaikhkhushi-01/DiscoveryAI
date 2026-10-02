from app.core.config import settings
from app.services.embeddings.base import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    """Create the configured embedding provider without loading ML runtimes at API startup.

    Sentence Transformers/PyTorch are intentionally imported only when an embedding
    operation is requested. This keeps the FastAPI process within small-container
    memory limits while preserving the existing embedding implementation.
    """
    provider = settings.embedding_provider
    if provider != "sentence-transformers":
        raise ValueError(f"Unsupported embedding provider: {provider}")

    from app.services.embeddings.sentence_transformers import SentenceTransformerProvider

    return SentenceTransformerProvider()
