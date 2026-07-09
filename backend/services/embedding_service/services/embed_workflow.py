"""Embedding workflow orchestration."""
import time

from sqlalchemy.orm import Session

from backend.services.embedding_service.config import EMBEDDING_BATCH_SIZE
from backend.services.embedding_service.models.db import Embedding
from backend.services.embedding_service.providers.factory import get_embedding_provider
from backend.services.embedding_service.schemas.embed import EmbedStatsData
from backend.services.embedding_service.services.chunk_access import get_chunks_for_paper
from backend.services.embedding_service.services.embedding_service import EmbeddingService
from backend.services.embedding_service.services.paper_access import get_paper_for_user
from backend.services.embedding_service.utils.base_provider import BaseEmbeddingProvider
from backend.shared.logger import get_logger

logger = get_logger("embedding_service")


def _get_embedded_chunk_ids(db: Session, paper_id: int, model_name: str) -> set[int]:
    rows = (
        db.query(Embedding.chunk_id)
        .filter(Embedding.paper_id == paper_id, Embedding.embedding_model == model_name)
        .all()
    )
    return {row[0] for row in rows}


def generate_embeddings_for_paper(
    db: Session,
    user_id: int,
    paper_id: int,
    provider: BaseEmbeddingProvider | None = None,
    batch_size: int | None = None,
) -> dict:
    start = time.perf_counter()
    get_paper_for_user(paper_id, user_id)
    chunks = get_chunks_for_paper(paper_id, user_id)

    active_provider = provider or get_embedding_provider()
    service = EmbeddingService(active_provider)
    model_name = active_provider.model_name
    effective_batch_size = batch_size or EMBEDDING_BATCH_SIZE

    embedded_ids = _get_embedded_chunk_ids(db, paper_id, model_name)
    pending = [chunk for chunk in chunks if chunk.id not in embedded_ids]

    if pending:
        texts = [chunk.chunk_text for chunk in pending]
        vectors = service.embed_texts(texts, effective_batch_size)
        dimension = active_provider.dimension

        for chunk, vector in zip(pending, vectors, strict=True):
            record = Embedding(
                paper_id=paper_id,
                chunk_id=chunk.id,
                embedding_model=model_name,
                embedding_dimension=dimension,
            )
            record.set_vector(vector)
            db.add(record)

        db.commit()
        logger.info(
            f"Embeddings stored: paper_id={paper_id} new={len(pending)} model={model_name}"
        )
    else:
        dimension = active_provider.dimension
        existing = (
            db.query(Embedding)
            .filter(Embedding.paper_id == paper_id, Embedding.embedding_model == model_name)
            .first()
        )
        if existing:
            dimension = existing.embedding_dimension
        logger.info(f"No new embeddings needed: paper_id={paper_id} model={model_name}")

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return EmbedStatsData(
        paper_id=paper_id,
        chunks_embedded=len(pending),
        embedding_dimension=dimension,
        model=model_name,
        processing_time_ms=elapsed_ms,
    ).model_dump()
