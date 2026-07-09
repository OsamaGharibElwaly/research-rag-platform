"""Base vector index provider abstraction."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    ids: list[int]
    scores: list[float]


class BaseVectorIndex(ABC):
    """Provider-agnostic interface for vector indexing and search."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Return the engine identifier."""

    @property
    @abstractmethod
    def dimension(self) -> int | None:
        """Return vector dimension, or None if not yet committed."""

    @property
    @abstractmethod
    def vector_count(self) -> int:
        """Return number of indexed vectors."""

    @abstractmethod
    def add_with_ids(self, vectors: list[list[float]], ids: list[int]) -> None:
        """Add vectors with stable external ids."""

    @abstractmethod
    def search(
        self,
        query: list[float],
        top_k: int,
        allowlist: list[int] | None = None,
    ) -> SearchResult:
        """Search for nearest neighbors."""

    @abstractmethod
    def contains(self, vector_id: int) -> bool:
        """Check if an id exists in the index."""

    @abstractmethod
    def remove(self, vector_id: int) -> bool:
        """Remove a vector by id."""

    @abstractmethod
    def prepare(self) -> None:
        """Eagerly build search caches."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist index to disk."""

    @classmethod
    @abstractmethod
    def load(cls, path: str, bit_width: int) -> "BaseVectorIndex":
        """Load index from disk."""

    @classmethod
    @abstractmethod
    def create(cls, dimension: int, bit_width: int) -> "BaseVectorIndex":
        """Create a new empty index."""
