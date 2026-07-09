"""Read-only access to embedding vectors."""
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.embedding_service.models.db import Embedding
from backend.services.vector_service.config import EMBEDDING_DATABASE_URL

engine = create_engine(
    EMBEDDING_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in EMBEDDING_DATABASE_URL else {},
)
EmbeddingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@dataclass
class EmbeddingRecord:
    chunk_id: int
    paper_id: int
    vector: list[float]
    dimension: int
    model: str


def get_embeddings_for_paper(paper_id: int) -> list[EmbeddingRecord]:
    db = EmbeddingSessionLocal()
    try:
        rows = (
            db.query(Embedding)
            .filter(Embedding.paper_id == paper_id)
            .order_by(Embedding.chunk_id.asc())
            .all()
        )
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Embeddings not found. Generate embeddings first.",
            )
        return [
            EmbeddingRecord(
                chunk_id=row.chunk_id,
                paper_id=row.paper_id,
                vector=row.get_vector(),
                dimension=row.embedding_dimension,
                model=row.embedding_model,
            )
            for row in rows
        ]
    finally:
        db.close()
