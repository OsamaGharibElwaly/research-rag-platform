"""Core embedding generation service."""
from backend.services.embedding_service.utils.base_provider import BaseEmbeddingProvider
from backend.shared.logger import get_logger

logger = get_logger("embedding_service")


class EmbeddingService:
    def __init__(self, provider: BaseEmbeddingProvider):
        self._provider = provider

    @property
    def provider(self) -> BaseEmbeddingProvider:
        return self._provider

    def embed_texts(self, texts: list[str], batch_size: int) -> list[list[float]]:
        if not texts:
            return []

        all_vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            logger.info(f"Embedding batch {start // batch_size + 1} ({len(batch)} texts)")
            vectors = self._provider.embed(batch)
            if len(vectors) != len(batch):
                raise ValueError("Provider returned mismatched embedding count")
            all_vectors.extend(vectors)
        return all_vectors
