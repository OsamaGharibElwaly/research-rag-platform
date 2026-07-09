"""TurboVec IdMapIndex provider."""
import numpy as np

from backend.services.vector_service.utils.base_index import BaseVectorIndex, SearchResult
from backend.shared.logger import get_logger

logger = get_logger("vector_service")


def _get_id_map_index():
    from turbovec import IdMapIndex

    return IdMapIndex


def _to_float32_matrix(vectors: list[list[float]]) -> np.ndarray:
    return np.asarray(vectors, dtype=np.float32)


def _to_uint64_ids(ids: list[int]) -> np.ndarray:
    return np.asarray(ids, dtype=np.uint64)


def _to_query_matrix(query: list[float]) -> np.ndarray:
    return np.asarray([query], dtype=np.float32)


class TurboVecIndex(BaseVectorIndex):
    """TurboVec IdMapIndex wrapper following official API."""

    def __init__(self, index):
        self._index = index

    @property
    def engine_name(self) -> str:
        return "turbovec"

    @property
    def dimension(self) -> int | None:
        return self._index.dim

    @property
    def vector_count(self) -> int:
        return len(self._index)

    def add_with_ids(self, vectors: list[list[float]], ids: list[int]) -> None:
        if not vectors:
            return
        matrix = _to_float32_matrix(vectors)
        id_array = _to_uint64_ids(ids)
        self._index.add_with_ids(matrix, id_array)
        logger.info(f"TurboVec added {len(ids)} vectors (total={len(self._index)})")

    def search(
        self,
        query: list[float],
        top_k: int,
        allowlist: list[int] | None = None,
    ) -> SearchResult:
        query_matrix = _to_query_matrix(query)
        allowlist_array = _to_uint64_ids(allowlist) if allowlist else None
        scores, ids = self._index.search(query_matrix, top_k, allowlist=allowlist_array)
        score_row = scores[0] if len(scores.shape) > 1 else scores
        id_row = ids[0] if len(ids.shape) > 1 else ids
        return SearchResult(
            ids=[int(vector_id) for vector_id in id_row],
            scores=[float(score) for score in score_row],
        )

    def contains(self, vector_id: int) -> bool:
        return int(vector_id) in self._index

    def remove(self, vector_id: int) -> bool:
        return self._index.remove(int(vector_id))

    def prepare(self) -> None:
        self._index.prepare()

    def save(self, path: str) -> None:
        self._index.write(path)

    @classmethod
    def load(cls, path: str, bit_width: int) -> "TurboVecIndex":
        IdMapIndex = _get_id_map_index()
        loaded = IdMapIndex.load(path)
        return cls(loaded)

    @classmethod
    def create(cls, dimension: int, bit_width: int) -> "TurboVecIndex":
        IdMapIndex = _get_id_map_index()
        return cls(IdMapIndex(dim=dimension, bit_width=bit_width))
