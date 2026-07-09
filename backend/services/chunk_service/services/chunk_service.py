"""Core chunking service."""
from backend.services.chunk_service.utils.base_chunker import BaseChunker, ChunkConfig, TextChunk
from backend.services.chunk_service.utils.character_chunker import CharacterChunker
from backend.services.chunk_service.utils.text_cleaner import clean_text
from backend.shared.logger import get_logger

logger = get_logger("chunk_service")


class ChunkService:
    def __init__(self, chunker: BaseChunker | None = None):
        self._chunker = chunker or CharacterChunker()

    def generate_chunks(self, text: str, config: ChunkConfig) -> list[TextChunk]:
        cleaned = clean_text(text)
        if not cleaned:
            raise ValueError("Cannot chunk empty text")

        logger.info(
            "Generating chunks "
            f"(size={config.chunk_size}, overlap={config.chunk_overlap}, length={len(cleaned)})"
        )
        chunks = self._chunker.chunk(cleaned, config)
        if not chunks:
            raise ValueError("Chunking produced no valid chunks")
        return chunks
