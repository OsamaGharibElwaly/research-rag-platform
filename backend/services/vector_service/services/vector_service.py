"""Core vector indexing service."""
from backend.services.vector_service.services.embedding_access import EmbeddingRecord
from backend.services.vector_service.utils.base_index import BaseVectorIndex
from backend.shared.logger import get_logger

logger = get_logger("vector_service")


class VectorIndexService:
    def __init__(self, index: BaseVectorIndex):
        self._index = index

    @property
    def index(self) -> BaseVectorIndex:
        return self._index

    def add_embeddings(self, embeddings: list[EmbeddingRecord]) -> int:
        pending_vectors: list[list[float]] = []
        pending_ids: list[int] = []
        for record in embeddings:
            if self._index.contains(record.chunk_id):
                continue
            pending_vectors.append(record.vector)
            pending_ids.append(record.chunk_id)
        if pending_vectors:
            self._index.add_with_ids(pending_vectors, pending_ids)
            logger.info(f"Indexed {len(pending_ids)} new vectors")
        return len(pending_ids)

    def rebuild(self, embeddings: list[EmbeddingRecord]) -> int:
        for record in embeddings:
            while self._index.contains(record.chunk_id):
                self._index.remove(record.chunk_id)
        vectors = [record.vector for record in embeddings]
        chunk_ids = [record.chunk_id for record in embeddings]
        if vectors:
            self._index.add_with_ids(vectors, chunk_ids)
        return len(chunk_ids)
