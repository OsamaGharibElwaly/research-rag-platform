"""Read-only access to text chunks for search metadata."""
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.chunk_service.models.db import Chunk
from backend.services.vector_service.config import CHUNK_DATABASE_URL

engine = create_engine(
    CHUNK_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in CHUNK_DATABASE_URL else {},
)
ChunkSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@dataclass
class ChunkMetadata:
    id: int
    paper_id: int
    chunk_index: int
    chunk_text: str


def get_chunk_metadata_map(paper_id: int, user_id: int) -> dict[int, ChunkMetadata]:
    db = ChunkSessionLocal()
    try:
        rows = (
            db.query(Chunk)
            .filter(Chunk.paper_id == paper_id, Chunk.user_id == user_id)
            .order_by(Chunk.chunk_index.asc())
            .all()
        )
        return {
            row.id: ChunkMetadata(
                id=row.id,
                paper_id=row.paper_id,
                chunk_index=row.chunk_index,
                chunk_text=row.chunk_text,
            )
            for row in rows
        }
    finally:
        db.close()


def get_chunk_metadata(chunk_id: int) -> ChunkMetadata | None:
    db = ChunkSessionLocal()
    try:
        row = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if not row:
            return None
        return ChunkMetadata(
            id=row.id,
            paper_id=row.paper_id,
            chunk_index=row.chunk_index,
            chunk_text=row.chunk_text,
        )
    finally:
        db.close()
