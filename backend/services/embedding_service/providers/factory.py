"""Embedding provider factory."""
from backend.services.embedding_service.config import (
    EMBEDDING_DEVICE,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
)
from backend.services.embedding_service.providers.sentence_transformers import (
    SentenceTransformersProvider,
)
from backend.services.embedding_service.utils.base_provider import BaseEmbeddingProvider


def get_embedding_provider(
    provider_name: str | None = None,
    model_name: str | None = None,
    device: str | None = None,
) -> BaseEmbeddingProvider:
    name = (provider_name or EMBEDDING_PROVIDER).lower()
    model = model_name or EMBEDDING_MODEL
    target_device = device or EMBEDDING_DEVICE

    if name == "sentence-transformers":
        return SentenceTransformersProvider(model_name=model, device=target_device)

    raise ValueError(f"Unsupported embedding provider: {name}")
