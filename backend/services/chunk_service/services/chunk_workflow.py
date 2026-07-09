"""Chunk workflow orchestration."""
from sqlalchemy.orm import Session

from backend.services.chunk_service.config import (
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHUNK_SIZE,
    MINIMUM_CHUNK_LENGTH,
)
from backend.services.chunk_service.models.db import Chunk
from backend.services.chunk_service.schemas.chunk import ChunkConfigSchema, ChunkStatsData
from backend.services.chunk_service.services.chunk_service import ChunkService
from backend.services.chunk_service.services.parse_access import get_parsed_text
from backend.services.chunk_service.services.paper_access import get_paper_for_user
from backend.services.chunk_service.utils.base_chunker import ChunkConfig
from backend.shared.logger import get_logger

logger = get_logger("chunk_service")


def _build_config(override: ChunkConfigSchema | None = None) -> ChunkConfig:
    if override:
        return ChunkConfig(
            chunk_size=override.chunk_size,
            chunk_overlap=override.chunk_overlap,
            separators=override.separators,
            minimum_chunk_length=override.minimum_chunk_length,
        )
    return ChunkConfig(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
        minimum_chunk_length=MINIMUM_CHUNK_LENGTH,
    )


def _compute_stats(paper_id: int, chunks: list[Chunk]) -> dict:
    lengths = [chunk.chunk_length for chunk in chunks]
    return ChunkStatsData(
        paper_id=paper_id,
        chunks_created=len(chunks),
        average_chunk_size=round(sum(lengths) / len(lengths), 2),
        largest_chunk=max(lengths),
        smallest_chunk=min(lengths),
        first_chunk=chunks[0].chunk_text[:500] if chunks else "",
        last_chunk=chunks[-1].chunk_text[:500] if chunks else "",
    ).model_dump()


def generate_chunks_for_paper(
    db: Session,
    user_id: int,
    paper_id: int,
    config_override: ChunkConfigSchema | None = None,
    chunk_service: ChunkService | None = None,
) -> dict:
    get_paper_for_user(paper_id, user_id)
    parsed_text = get_parsed_text(paper_id, user_id)
    config = _build_config(config_override)
    service = chunk_service or ChunkService()

    text_chunks = service.generate_chunks(parsed_text, config)

    db.query(Chunk).filter(Chunk.paper_id == paper_id).delete()
    db.commit()

    stored: list[Chunk] = []
    for text_chunk in text_chunks:
        record = Chunk(
            paper_id=paper_id,
            user_id=user_id,
            chunk_index=text_chunk.chunk_index,
            chunk_text=text_chunk.chunk_text,
            start_offset=text_chunk.start_offset,
            end_offset=text_chunk.end_offset,
            chunk_length=text_chunk.chunk_length,
        )
        db.add(record)
        stored.append(record)

    db.commit()
    for record in stored:
        db.refresh(record)

    logger.info(f"Chunks generated: paper_id={paper_id} count={len(stored)}")
    return _compute_stats(paper_id, stored)
