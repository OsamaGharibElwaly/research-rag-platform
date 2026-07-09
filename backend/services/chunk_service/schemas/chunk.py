"""Chunk service Pydantic schemas."""
from typing import Optional

from pydantic import BaseModel, Field


class ChunkConfigSchema(BaseModel):
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=200, ge=0)
    separators: list[str] = Field(default_factory=lambda: ["\n\n", "\n", ". ", " "])
    minimum_chunk_length: int = Field(default=1, ge=1)


class ChunkRequest(BaseModel):
    paper_id: int = Field(..., gt=0)
    config: Optional[ChunkConfigSchema] = None


class ChunkStatsData(BaseModel):
    paper_id: int
    chunks_created: int
    average_chunk_size: float
    largest_chunk: int
    smallest_chunk: int
    first_chunk: str = ""
    last_chunk: str = ""
