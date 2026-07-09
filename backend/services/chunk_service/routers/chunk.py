"""Chunk service API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.shared.auth import get_current_user
from backend.shared.logger import generate_request_id, get_logger
from backend.shared.schemas import APIResponse

from backend.services.chunk_service.models.db import get_db
from backend.services.chunk_service.schemas.chunk import ChunkRequest
from backend.services.chunk_service.services.chunk_workflow import generate_chunks_for_paper

router = APIRouter(tags=["Chunk"])
logger = get_logger("chunk_service")


@router.post("/chunk", response_model=APIResponse)
async def create_chunks(
    payload: ChunkRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    user_id = int(current_user["user_id"])
    logger.info(f"[{request_id}] Chunk request paper_id={payload.paper_id} user_id={user_id}")

    try:
        data = generate_chunks_for_paper(
            db,
            user_id,
            payload.paper_id,
            config_override=payload.config,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return APIResponse(
        status="success",
        message="Chunks generated successfully",
        data=data,
    )
