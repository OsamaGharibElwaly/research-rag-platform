# Embedding Service

Generates semantic embedding vectors for text chunks produced by the Chunk Service.

## Responsibility

Convert every generated text chunk into a semantic embedding vector. This service does **not** perform retrieval or LLM operations.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/embed` | Generate embeddings for all chunks of a paper (protected) |

### Request

```json
{ "paper_id": 1 }
```

### Response

```json
{
  "status": "success",
  "message": "Embeddings generated successfully",
  "data": {
    "paper_id": 1,
    "chunks_embedded": 295,
    "embedding_dimension": 384,
    "model": "BAAI/bge-small-en-v1.5",
    "processing_time_ms": 1248
  }
}
```

## Workflow

1. Verify JWT
2. Verify paper ownership (upload DB)
3. Load chunks (chunk DB)
4. Skip chunks already embedded for the active model
5. Generate embeddings in configurable batches
6. Store vectors in embedding DB
7. Return statistics

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_DATABASE_URL` | `sqlite:///./embedding.db` | Embedding storage |
| `CHUNK_DATABASE_URL` | `sqlite:///./chunk.db` | Chunk source |
| `UPLOAD_DATABASE_URL` | `sqlite:///./upload.db` | Ownership verification |
| `EMBEDDING_PROVIDER` | `sentence-transformers` | Provider name |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Model identifier |
| `EMBEDDING_BATCH_SIZE` | `32` | Texts per batch |
| `EMBEDDING_DEVICE` | `cpu` | `cpu` or `cuda` for GPU |
| `EMBEDDING_SERVICE_PORT` | `8005` | Service port |

## Providers

Providers implement `BaseEmbeddingProvider` in `utils/base_provider.py`.

- **sentence-transformers** (default) — local models via `SentenceTransformersProvider`
- Future: OpenAI, Gemini, VoyageAI (add provider class + factory entry)

Swap providers via `EMBEDDING_PROVIDER` without API changes.

## Database

Table `embeddings`:

- `paper_id`, `chunk_id`, `embedding_vector` (JSON), `embedding_dimension`, `embedding_model`, `created_at`
- Unique on `(chunk_id, embedding_model)` — supports re-embedding with a different model later

## Run

```bash
python -m uvicorn backend.services.embedding_service.main:app --reload --port 8005
```

Or use `backend.dev_server` / API Gateway on port 8000.
