"""Embedding service Pydantic schemas."""
from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    paper_id: int = Field(..., gt=0)


class EmbedStatsData(BaseModel):
    paper_id: int
    chunks_embedded: int
    embedding_dimension: int
    model: str
    processing_time_ms: int
