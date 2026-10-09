from __future__ import annotations

import math

import httpx

from app.core.config import settings
from app.services.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Generate embeddings through Gemini's hosted API instead of loading PyTorch locally."""

    @property
    def dimension(self) -> int:
        return settings.embedding_dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if settings.gemini_api_key is None:
            raise RuntimeError(
                "GEMINI_API_KEY is required when EMBEDDING_PROVIDER=gemini"
            )

        api_key = settings.gemini_api_key.get_secret_value()
        model = settings.gemini_embedding_model
        base_url = settings.gemini_base_url.rstrip("/")
        vectors: list[list[float]] = []

        # One text per request keeps payload and peak memory small on free instances.
        with httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
            for text in texts:
                response = client.post(
                    f"{base_url}/models/{model}:embedContent",
                    headers={"x-goog-api-key": api_key},
                    json={
                        "model": f"models/{model}",
                        "content": {"parts": [{"text": text[:12000]}]},
                        "outputDimensionality": self.dimension,
                    },
                )
                if response.is_error:
                    # Do not include the request URL, which contains the API key.
                    raise RuntimeError(
                        f"Gemini embedding request failed with HTTP {response.status_code}: "
                        f"{response.text[:500]}"
                    )
                data = response.json()
                raw = data.get("embedding", {}).get("values")
                if not isinstance(raw, list) or len(raw) != self.dimension:
                    raise RuntimeError(
                        f"Gemini returned an invalid embedding dimension; expected {self.dimension}"
                    )
                vector = [float(value) for value in raw]
                norm = math.sqrt(sum(value * value for value in vector))
                if norm:
                    vector = [value / norm for value in vector]
                vectors.append(vector)
        return vectors
