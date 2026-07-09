"""Read-only access to uploaded papers for ownership verification."""
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.services.chunk_service.config import UPLOAD_DATABASE_URL
from backend.services.upload_service.models import Paper

engine = create_engine(
    UPLOAD_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in UPLOAD_DATABASE_URL else {},
)
UploadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_paper_for_user(paper_id: int, user_id: int) -> Paper:
    db = UploadSessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found",
            )
        if paper.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to chunk this paper",
            )
        return paper
    finally:
        db.close()
