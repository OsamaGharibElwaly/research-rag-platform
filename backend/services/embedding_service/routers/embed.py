"""Embedding service API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.shared.auth import get_current_user
from backend.shared.logger import generate_request_id, get_logger
from backend.shared.schemas import APIResponse

from backend.services.embedding_service.models.db import get_db
from backend.services.embedding_service.schemas.embed import EmbedRequest
from backend.services.embedding_service.services.embed_workflow import generate_embeddings_for_paper

router = APIRouter(tags=["Embedding"])
logger = get_logger("embedding_service")


@router.post("/embed", response_model=APIResponse)
async def create_embeddings(
    payload: EmbedRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    user_id = int(current_user["user_id"])
    logger.info(f"[{request_id}] Embed request paper_id={payload.paper_id} user_id={user_id}")

    data = generate_embeddings_for_paper(db, user_id, payload.paper_id)

    return APIResponse(
        status="success",
        message="Embeddings generated successfully",
        data=data,
    )
