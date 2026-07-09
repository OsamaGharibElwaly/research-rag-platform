"""Read-only access to parsed document text."""
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.chunk_service.config import PARSER_DATABASE_URL
from backend.services.parser_service.models.db import ParseResult

engine = create_engine(
    PARSER_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in PARSER_DATABASE_URL else {},
)
ParserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_parsed_text(paper_id: int, user_id: int) -> str:
    db = ParserSessionLocal()
    try:
        result = db.query(ParseResult).filter(ParseResult.paper_id == paper_id).first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed text not found. Parse the paper first.",
            )
        if result.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access parsed text for this paper",
            )
        if result.status != "completed" or not result.text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Parsed text is empty or parsing failed",
            )
        return result.text
    finally:
        db.close()
