"""Vector service database models."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.services.vector_service.config import VECTOR_DATABASE_URL

engine = create_engine(
    VECTOR_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in VECTOR_DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class VectorIndex(Base):
    __tablename__ = "vector_indexes"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, unique=True, index=True, nullable=False)
    index_path = Column(String, nullable=False)
    engine = Column(String, nullable=False)
    vector_count = Column(Integer, nullable=False, default=0)
    dimension = Column(Integer, nullable=False)
    bit_width = Column(Integer, nullable=False, default=4)
    embedding_model = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
