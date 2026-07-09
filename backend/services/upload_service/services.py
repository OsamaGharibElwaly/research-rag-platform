"""Upload service business logic."""
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.shared.logger import get_logger
from backend.services.upload_service.config import MAX_FILE_SIZE_MB, UPLOAD_DIR
from backend.services.upload_service.models import Paper

logger = get_logger("upload_service")

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _validate_pdf(file: UploadFile, content: bytes) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file",
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB",
        )


def upload_paper(db: Session, user_id: int, file: UploadFile, content: bytes) -> Paper:
    _validate_pdf(file, content)

    stored_name = f"{uuid.uuid4().hex}.pdf"
    user_dir = Path(UPLOAD_DIR) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / stored_name

    with open(file_path, "wb") as output:
        output.write(content)

    paper = Paper(
        user_id=user_id,
        filename=stored_name,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        content_type=file.content_type or "application/pdf",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    logger.info(f"Paper uploaded: id={paper.id} user_id={user_id}")
    return paper


def list_papers(db: Session, user_id: int) -> list[Paper]:
    return (
        db.query(Paper)
        .filter(Paper.user_id == user_id)
        .order_by(Paper.created_at.desc())
        .all()
    )


def delete_paper(db: Session, user_id: int, paper_id: int) -> None:
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )

    if paper.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this paper",
        )

    if os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    db.delete(paper)
    db.commit()
    logger.info(f"Paper deleted: id={paper_id} user_id={user_id}")
