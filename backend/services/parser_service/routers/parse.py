"""Parser service API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.shared.auth import get_current_user
from backend.shared.logger import generate_request_id, get_logger
from backend.shared.schemas import APIResponse

from backend.services.parser_service.models.db import get_db
from backend.services.parser_service.schemas.parse import ParseRequest
from backend.services.parser_service.services.parse_workflow import parse_paper

router = APIRouter(tags=["Parser"])
logger = get_logger("parser_service")


@router.post("/parse", response_model=APIResponse)
async def parse_document(
    payload: ParseRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    user_id = int(current_user["user_id"])
    logger.info(f"[{request_id}] Parse request paper_id={payload.paper_id} user_id={user_id}")

    try:
        data = parse_paper(db, user_id, payload.paper_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return APIResponse(
        status="success",
        message="Paper parsed successfully",
        data=data,
    )
