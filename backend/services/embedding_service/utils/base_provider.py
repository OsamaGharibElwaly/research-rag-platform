"""Base embedding provider abstraction."""
from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    """Provider-agnostic interface for text embedding models."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier used for storage and API responses."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding vector dimension."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
