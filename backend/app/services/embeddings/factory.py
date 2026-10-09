from app.core.config import settings
from app.services.embeddings.base import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    """Create the configured provider without importing ML runtimes during API startup."""
    provider = settings.embedding_provider.strip().lower()

    if provider == "gemini":
        from app.services.embeddings.gemini import GeminiEmbeddingProvider
        return GeminiEmbeddingProvider()

    if provider == "sentence-transformers":
        from app.services.embeddings.sentence_transformers import SentenceTransformerProvider
        return SentenceTransformerProvider()

    raise ValueError(
        f"Unsupported embedding provider: {provider}. "
        "Supported providers: gemini, sentence-transformers"
    )
