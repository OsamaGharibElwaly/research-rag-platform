"""Vector service API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.shared.auth import get_current_user
from backend.shared.logger import generate_request_id, get_logger
from backend.shared.schemas import APIResponse

from backend.services.vector_service.models.db import get_db
from backend.services.vector_service.schemas.vector import IndexRequest, SearchRequest
from backend.services.vector_service.services.index_workflow import (
    build_index_for_paper,
    delete_index_for_paper,
)
from backend.services.vector_service.services.search_workflow import search_vectors_for_paper

router = APIRouter(tags=["Vector"])
logger = get_logger("vector_service")


@router.post("/index", response_model=APIResponse)
async def create_index(
    payload: IndexRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    user_id = int(current_user["user_id"])
    logger.info(
        f"[{request_id}] Index request paper_id={payload.paper_id} "
        f"rebuild={payload.rebuild} user_id={user_id}"
    )

    data = build_index_for_paper(db, user_id, payload.paper_id, rebuild=payload.rebuild)
    return APIResponse(
        status="success",
        message="Vector index built successfully",
        data=data,
    )


@router.post("/search", response_model=APIResponse)
async def search_index(
    payload: SearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    user_id = int(current_user["user_id"])
    logger.info(
        f"[{request_id}] Search request paper_id={payload.paper_id} "
        f"top_k={payload.top_k} user_id={user_id}"
    )

    data = search_vectors_for_paper(
        db,
        user_id,
        payload.paper_id,
        payload.query_embedding,
        payload.top_k,
        allowlist=payload.allowlist,
    )
    return APIResponse(
        status="success",
        message="Vector search completed successfully",
        data=data,
    )


@router.delete("/index/{paper_id}", response_model=APIResponse)
async def delete_index(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    user_id = int(current_user["user_id"])
    logger.info(f"[{request_id}] Delete index paper_id={paper_id} user_id={user_id}")

    data = delete_index_for_paper(db, user_id, paper_id)
    return APIResponse(
        status="success",
        message="Vector index deleted successfully",
        data=data,
    )
