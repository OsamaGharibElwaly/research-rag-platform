"""Sentence-transformers embedding provider."""
from backend.services.embedding_service.utils.base_provider import BaseEmbeddingProvider
from backend.shared.logger import get_logger

logger = get_logger("embedding_service")


class SentenceTransformersProvider(BaseEmbeddingProvider):
    """Default local embedding provider using sentence-transformers."""

    def __init__(self, model_name: str, device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._dimension: int | None = None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        self._ensure_loaded()
        return self._dimension or 0

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading embedding model {self._model_name} on {self._device}")
        self._model = SentenceTransformer(self._model_name, device=self._device)
        sample = self._model.encode(["warmup"], convert_to_numpy=True)
        self._dimension = int(sample.shape[1])

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._ensure_loaded()
        vectors = self._model.encode(
            texts,
            batch_size=len(texts),
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return [vector.tolist() for vector in vectors]
