"""Vector index file management."""
import os
from pathlib import Path

from backend.services.vector_service.config import VECTOR_INDEX_DIR


def ensure_index_dir() -> str:
    Path(VECTOR_INDEX_DIR).mkdir(parents=True, exist_ok=True)
    return VECTOR_INDEX_DIR


def index_path_for_paper(paper_id: int) -> str:
    ensure_index_dir()
    return str(Path(VECTOR_INDEX_DIR) / f"paper_{paper_id}.tvim")


def index_size_bytes(path: str) -> int:
    if not os.path.exists(path):
        return 0
    return os.path.getsize(path)


def delete_index_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)
