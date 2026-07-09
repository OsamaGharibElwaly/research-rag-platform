"""Character-based semantic chunker with separator-aware splitting."""
from backend.services.chunk_service.utils.base_chunker import BaseChunker, ChunkConfig, TextChunk


class CharacterChunker(BaseChunker):
    def chunk(self, text: str, config: ChunkConfig) -> list[TextChunk]:
        if not text:
            return []

        if config.chunk_overlap >= config.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        chunks_text = self._split_text(text, config)
        results: list[TextChunk] = []
        search_from = 0

        for chunk_text in chunks_text:
            stripped = chunk_text.strip()
            if len(stripped) < config.minimum_chunk_length:
                continue

            start_offset = text.find(stripped, search_from)
            if start_offset == -1:
                start_offset = text.find(stripped)
            end_offset = start_offset + len(stripped)
            search_from = max(search_from, start_offset + 1)

            results.append(
                TextChunk(
                    chunk_index=len(results),
                    chunk_text=stripped,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    chunk_length=len(stripped),
                )
            )

        return results

    def _split_text(self, text: str, config: ChunkConfig) -> list[str]:
        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            max_end = min(start + config.chunk_size, text_length)
            end = self._find_break_point(text, start, max_end, config)

            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = end - config.chunk_overlap
            if next_start <= start:
                next_start = end
            start = next_start

        return chunks

    def _find_break_point(self, text: str, start: int, max_end: int, config: ChunkConfig) -> int:
        if max_end >= len(text):
            return len(text)

        window = text[start:max_end]
        for separator in config.separators:
            if not separator:
                continue
            break_at = window.rfind(separator)
            if break_at > 0:
                return start + break_at + len(separator)

        space_break = window.rfind(" ")
        if space_break > 0:
            return start + space_break + 1

        return max_end
