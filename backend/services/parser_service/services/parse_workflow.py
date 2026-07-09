"""Parse workflow orchestration."""
from sqlalchemy.orm import Session

from backend.services.parser_service.models.db import ParseResult
from backend.services.parser_service.schemas.parse import ParseResultData
from backend.services.parser_service.services.paper_access import get_paper_for_user
from backend.services.parser_service.services.parser_service import ParserService
from backend.shared.logger import get_logger

logger = get_logger("parser_service")


def _to_response_data(result: ParseResult) -> dict:
    return ParseResultData(
        paper_id=result.paper_id,
        title=result.title or "",
        authors=result.authors or [],
        abstract=result.abstract or "",
        pages=result.pages or 0,
        metadata=result.metadata_json or {},
        references=result.references or [],
        text=result.text or "",
        status=result.status,
    ).model_dump()


def parse_paper(
    db: Session,
    user_id: int,
    paper_id: int,
    parser_service: ParserService | None = None,
) -> dict:
    paper = get_paper_for_user(paper_id, user_id)
    service = parser_service or ParserService()

    existing = db.query(ParseResult).filter(ParseResult.paper_id == paper_id).first()
    if existing is None:
        existing = ParseResult(
            paper_id=paper_id,
            user_id=user_id,
            status="pending",
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)

    try:
        parsed = service.parse_pdf(paper.file_path)
        existing.status = "completed"
        existing.title = parsed.title
        existing.authors = parsed.authors
        existing.abstract = parsed.abstract
        existing.pages = parsed.pages
        existing.metadata_json = parsed.metadata
        existing.references = parsed.references
        existing.text = parsed.text
        existing.error_message = None
        db.commit()
        db.refresh(existing)
        logger.info(f"Paper parsed successfully: paper_id={paper_id}")
        return _to_response_data(existing)
    except ValueError as exc:
        existing.status = "failed"
        existing.error_message = str(exc)
        db.commit()
        db.refresh(existing)
        raise
