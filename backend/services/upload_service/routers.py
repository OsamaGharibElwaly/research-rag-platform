"""Upload service API routes."""
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from backend.shared.auth import get_current_user
from backend.shared.logger import generate_request_id, get_logger
from backend.shared.schemas import APIResponse

from .models import get_db
from .schemas import PaperResponse
from .services import delete_paper, list_papers, upload_paper

router = APIRouter(tags=["Upload"])
logger = get_logger("upload_service")


@router.post("/upload", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Upload attempt by user {current_user['user_id']}")

    content = await file.read()
    paper = upload_paper(db, int(current_user["user_id"]), file, content)

    return APIResponse(
        status="success",
        message="Paper uploaded successfully",
        data={"paper": PaperResponse.model_validate(paper).model_dump()},
    )


@router.get("/papers", response_model=APIResponse)
async def get_papers(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] List papers for user {current_user['user_id']}")

    papers = list_papers(db, int(current_user["user_id"]))
    return APIResponse(
        status="success",
        message="Papers retrieved successfully",
        data={
            "papers": [PaperResponse.model_validate(paper).model_dump() for paper in papers]
        },
    )


@router.delete("/paper/{paper_id}", response_model=APIResponse)
async def remove_paper(
    paper_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Delete paper {paper_id} by user {current_user['user_id']}")

    delete_paper(db, int(current_user["user_id"]), paper_id)
    return APIResponse(
        status="success",
        message="Paper deleted successfully",
        data={"paper_id": paper_id},
    )
