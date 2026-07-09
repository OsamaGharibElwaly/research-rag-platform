"""Read-only access to text chunks."""
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.chunk_service.models.db import Chunk
from backend.services.embedding_service.config import CHUNK_DATABASE_URL

engine = create_engine(
    CHUNK_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in CHUNK_DATABASE_URL else {},
)
ChunkSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@dataclass
class ChunkRecord:
    id: int
    paper_id: int
    chunk_index: int
    chunk_text: str


def get_chunks_for_paper(paper_id: int, user_id: int) -> list[ChunkRecord]:
    db = ChunkSessionLocal()
    try:
        rows = (
            db.query(Chunk)
            .filter(Chunk.paper_id == paper_id, Chunk.user_id == user_id)
            .order_by(Chunk.chunk_index.asc())
            .all()
        )
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunks not found. Generate chunks first.",
            )
        return [
            ChunkRecord(
                id=row.id,
                paper_id=row.paper_id,
                chunk_index=row.chunk_index,
                chunk_text=row.chunk_text,
            )
            for row in rows
        ]
    finally:
        db.close()
