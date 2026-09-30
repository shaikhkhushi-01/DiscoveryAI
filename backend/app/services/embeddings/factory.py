from app.core.config import settings
from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.sentence_transformers import SentenceTransformerProvider

def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding_provider
    if provider != "sentence-transformers":
        raise ValueError(f"Unsupported embedding provider: {provider}")
    return SentenceTransformerProvider()
