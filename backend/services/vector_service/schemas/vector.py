"""Vector service Pydantic schemas."""
from typing import Optional

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    paper_id: int = Field(..., gt=0)
    rebuild: bool = False


class IndexStatsData(BaseModel):
    paper_id: int
    engine: str
    vector_count: int
    dimension: int
    vectors_indexed: int
    index_path: str
    index_size_bytes: int
    bit_width: int
    status: str
    processing_time_ms: int


class SearchRequest(BaseModel):
    paper_id: int = Field(..., gt=0)
    query_embedding: list[float] = Field(..., min_length=1)
    top_k: int = Field(default=5, gt=0, le=100)
    allowlist: Optional[list[int]] = None


class SearchHit(BaseModel):
    chunk_id: int
    score: float
    paper_id: int
    chunk_index: int
    chunk_text: str


class SearchResultData(BaseModel):
    paper_id: int
    top_k: int
    engine: str
    results: list[SearchHit]
    search_latency_ms: int
