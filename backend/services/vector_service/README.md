# Vector Service

Indexes embedding vectors and performs similarity search using TurboVec.

## Responsibility

Vector indexing and search only. This service does **not** generate embeddings or call LLMs.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/index` | Build or incrementally update a paper index (protected) |
| POST | `/search` | Similarity search over a paper index (protected) |
| DELETE | `/index/{paper_id}` | Delete a paper index (protected) |

### Index Request

```json
{ "paper_id": 1, "rebuild": false }
```

### Search Request

```json
{
  "paper_id": 1,
  "query_embedding": [0.1, 0.2, ...],
  "top_k": 5,
  "allowlist": [101, 102]
}
```

## Workflow (`POST /index`)

1. Verify JWT
2. Verify paper ownership (upload DB)
3. Load embeddings (embedding DB)
4. Load existing TurboVec `IdMapIndex` or create new
5. Incrementally add missing chunk vectors (skip duplicates)
6. `prepare()` + `write()` to `.tvim` file
7. Store metadata in vector DB

## TurboVec Integration

Uses official `IdMapIndex` API:

- `add_with_ids(vectors, uint64_ids)` — incremental insert with stable chunk ids
- `search(queries, k, allowlist=...)` — top-k similarity with optional filtering
- `remove(id)` — O(1) deletion
- `write(path)` / `IdMapIndex.load(path)` — `.tvim` persistence
- `prepare()` — eager SIMD cache build before search

## Provider Abstraction

`BaseVectorIndex` in `utils/base_index.py` allows swapping TurboVec for FAISS, Qdrant, etc. without API changes.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_DATABASE_URL` | `sqlite:///./vector.db` | Index metadata |
| `EMBEDDING_DATABASE_URL` | `sqlite:///./embedding.db` | Embedding source |
| `CHUNK_DATABASE_URL` | `sqlite:///./chunk.db` | Chunk metadata for search hits |
| `UPLOAD_DATABASE_URL` | `sqlite:///./upload.db` | Ownership verification |
| `VECTOR_ENGINE` | `turbovec` | Engine name |
| `VECTOR_INDEX_DIR` | `./vector_indexes` | Persistent index files |
| `VECTOR_BIT_WIDTH` | `4` | TurboVec quantization (2, 3, or 4) |
| `VECTOR_SERVICE_PORT` | `8006` | Service port |

## Run

```bash
python -m uvicorn backend.services.vector_service.main:app --reload --port 8006
```

Or use `backend.dev_server` / API Gateway on port 8000.
