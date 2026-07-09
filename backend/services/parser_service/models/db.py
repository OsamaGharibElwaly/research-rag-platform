"""Parser service database models."""
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.services.parser_service.config import PARSER_DATABASE_URL

engine = create_engine(
    PARSER_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in PARSER_DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ParseResult(Base):
    __tablename__ = "parse_results"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    status = Column(String, default="pending", nullable=False)
    title = Column(String, nullable=True)
    authors = Column(JSON, default=list)
    abstract = Column(Text, nullable=True)
    pages = Column(Integer, default=0)
    metadata_json = Column("metadata", JSON, default=dict)
    references = Column(JSON, default=list)
    text = Column(Text, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
