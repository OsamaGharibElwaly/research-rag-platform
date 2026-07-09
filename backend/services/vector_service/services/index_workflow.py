"""Vector indexing workflow orchestration."""
import os
import time
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.vector_service.config import VECTOR_BIT_WIDTH, VECTOR_ENGINE
from backend.services.vector_service.models.db import VectorIndex
from backend.services.vector_service.providers.factory import create_index, load_index
from backend.services.vector_service.schemas.vector import IndexStatsData
from backend.services.vector_service.services.embedding_access import get_embeddings_for_paper
from backend.services.vector_service.services.paper_access import get_paper_for_user
from backend.services.vector_service.services.vector_service import VectorIndexService
from backend.services.vector_service.utils.index_paths import (
    delete_index_file,
    index_path_for_paper,
    index_size_bytes,
)
from backend.shared.logger import get_logger

logger = get_logger("vector_service")


def _validate_dimension(dimension: int) -> None:
    if dimension <= 0 or dimension % 8 != 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Embedding dimension {dimension} is invalid for TurboVec (must be positive multiple of 8)",
        )


def _upsert_metadata(
    db: Session,
    paper_id: int,
    index_path: str,
    engine: str,
    vector_count: int,
    dimension: int,
    bit_width: int,
    embedding_model: str,
    existing: VectorIndex | None,
) -> None:
    if existing:
        existing.index_path = index_path
        existing.engine = engine
        existing.vector_count = vector_count
        existing.dimension = dimension
        existing.bit_width = bit_width
        existing.embedding_model = embedding_model
        existing.updated_at = datetime.utcnow()
    else:
        db.add(
            VectorIndex(
                paper_id=paper_id,
                index_path=index_path,
                engine=engine,
                vector_count=vector_count,
                dimension=dimension,
                bit_width=bit_width,
                embedding_model=embedding_model,
            )
        )
    db.commit()


def build_index_for_paper(
    db: Session,
    user_id: int,
    paper_id: int,
    rebuild: bool = False,
    index_factory=None,
    index_loader=None,
) -> dict:
    factory = index_factory or create_index
    loader = index_loader or load_index
    start = time.perf_counter()
    get_paper_for_user(paper_id, user_id)
    embeddings = get_embeddings_for_paper(paper_id)
    dimension = embeddings[0].dimension
    embedding_model = embeddings[0].model
    _validate_dimension(dimension)

    existing = db.query(VectorIndex).filter(VectorIndex.paper_id == paper_id).first()
    if existing and not rebuild and existing.vector_count > 0 and not os.path.exists(existing.index_path):
        rebuild = True

    if rebuild:
        delete_index_file(index_path_for_paper(paper_id))
        index = factory(dimension, VECTOR_ENGINE, VECTOR_BIT_WIDTH)
        service = VectorIndexService(index)
        vectors_indexed = service.rebuild(embeddings)
        status_label = "rebuilt"
    else:
        index_path = index_path_for_paper(paper_id)
        if existing and os.path.exists(index_path):
            index = loader(index_path, VECTOR_ENGINE, VECTOR_BIT_WIDTH)
            status_label = "updated"
        else:
            index = factory(dimension, VECTOR_ENGINE, VECTOR_BIT_WIDTH)
            status_label = "created"
        service = VectorIndexService(index)
        vectors_indexed = service.add_embeddings(embeddings)
        if vectors_indexed == 0 and existing:
            status_label = "unchanged"

    index_path = index_path_for_paper(paper_id)
    index.prepare()
    index.save(index_path)

    _upsert_metadata(
        db,
        paper_id,
        index_path,
        VECTOR_ENGINE,
        index.vector_count,
        dimension,
        VECTOR_BIT_WIDTH,
        embedding_model,
        existing,
    )

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        f"Index {status_label}: paper_id={paper_id} vectors={index.vector_count} new={vectors_indexed}"
    )
    return IndexStatsData(
        paper_id=paper_id,
        engine=VECTOR_ENGINE,
        vector_count=index.vector_count,
        dimension=dimension,
        vectors_indexed=vectors_indexed,
        index_path=index_path,
        index_size_bytes=index_size_bytes(index_path),
        bit_width=VECTOR_BIT_WIDTH,
        status=status_label,
        processing_time_ms=elapsed_ms,
    ).model_dump()


def delete_index_for_paper(db: Session, user_id: int, paper_id: int) -> dict:
    get_paper_for_user(paper_id, user_id)
    existing = db.query(VectorIndex).filter(VectorIndex.paper_id == paper_id).first()
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector index not found",
        )
    delete_index_file(existing.index_path)
    db.delete(existing)
    db.commit()
    return {"paper_id": paper_id, "deleted": True}
