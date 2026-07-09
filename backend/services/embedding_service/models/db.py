"""Embedding service database models."""
import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.services.embedding_service.config import EMBEDDING_DATABASE_URL

engine = create_engine(
    EMBEDDING_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in EMBEDDING_DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, index=True, nullable=False)
    chunk_id = Column(Integer, index=True, nullable=False)
    embedding_vector = Column(Text, nullable=False)
    embedding_dimension = Column(Integer, nullable=False)
    embedding_model = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("chunk_id", "embedding_model", name="uq_chunk_embedding_model"),
    )

    def set_vector(self, vector: list[float]) -> None:
        self.embedding_vector = json.dumps(vector)
        self.embedding_dimension = len(vector)

    def get_vector(self) -> list[float]:
        return json.loads(self.embedding_vector)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
