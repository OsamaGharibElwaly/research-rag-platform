"""Abstract chunking interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ChunkConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: list[str] = field(default_factory=lambda: ["\n\n", "\n", ". ", " "])
    minimum_chunk_length: int = 1


@dataclass
class TextChunk:
    chunk_index: int
    chunk_text: str
    start_offset: int
    end_offset: int
    chunk_length: int


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, config: ChunkConfig) -> list[TextChunk]:
        """Split text into ordered semantic chunks."""
