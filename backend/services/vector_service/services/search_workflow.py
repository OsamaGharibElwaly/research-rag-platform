"""Vector search workflow orchestration."""
import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.services.vector_service.config import VECTOR_BIT_WIDTH, VECTOR_ENGINE
from backend.services.vector_service.models.db import VectorIndex
from backend.services.vector_service.providers.factory import load_index
from backend.services.vector_service.schemas.vector import SearchHit, SearchResultData
from backend.services.vector_service.services.chunk_access import get_chunk_metadata_map
from backend.services.vector_service.services.paper_access import get_paper_for_user
from backend.services.vector_service.utils.index_paths import index_path_for_paper
from backend.shared.logger import get_logger

logger = get_logger("vector_service")


def search_vectors_for_paper(
    db: Session,
    user_id: int,
    paper_id: int,
    query_embedding: list[float],
    top_k: int,
    allowlist: list[int] | None = None,
    index_loader=None,
) -> dict:
    loader = index_loader or load_index
    start = time.perf_counter()
    get_paper_for_user(paper_id, user_id)

    metadata = db.query(VectorIndex).filter(VectorIndex.paper_id == paper_id).first()
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector index not found. Build the index first.",
        )

    index_path = index_path_for_paper(paper_id)
    if metadata.dimension != len(query_embedding):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Query dimension {len(query_embedding)} does not match "
                f"index dimension {metadata.dimension}"
            ),
        )

    index = loader(index_path, VECTOR_ENGINE, metadata.bit_width or VECTOR_BIT_WIDTH)
    if index.vector_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector index is empty",
        )

    result = index.search(query_embedding, top_k, allowlist=allowlist)
    chunk_map = get_chunk_metadata_map(paper_id, user_id)

    hits: list[SearchHit] = []
    for chunk_id, score in zip(result.ids, result.scores, strict=True):
        chunk = chunk_map.get(chunk_id)
        if not chunk:
            continue
        hits.append(
            SearchHit(
                chunk_id=chunk_id,
                score=score,
                paper_id=chunk.paper_id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text[:500],
            )
        )

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    logger.info(f"Search complete: paper_id={paper_id} hits={len(hits)} latency_ms={elapsed_ms}")
    return SearchResultData(
        paper_id=paper_id,
        top_k=top_k,
        engine=metadata.engine,
        results=hits,
        search_latency_ms=elapsed_ms,
    ).model_dump()
