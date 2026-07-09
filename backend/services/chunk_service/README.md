# Chunk Service

Transforms parsed PDF text into semantic chunks optimized for RAG pipelines.

## Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chunk` | Generate chunks for a parsed paper |

## Request

```json
{
  "paper_id": 1,
  "config": {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "separators": ["\n\n", "\n", ". ", " "],
    "minimum_chunk_length": 1
  }
}
```

`config` is optional. Defaults come from environment variables.

## Workflow

1. Verify JWT
2. Verify paper ownership (upload DB)
3. Load parsed text (parser DB)
4. Clean and split text
5. Store chunk records
6. Return statistics

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_DATABASE_URL` | `sqlite:///./chunk.db` | Chunk storage DB |
| `PARSER_DATABASE_URL` | `sqlite:///./parser.db` | Parser DB (read-only) |
| `UPLOAD_DATABASE_URL` | `sqlite:///./upload.db` | Upload DB (read-only) |
| `CHUNK_SIZE` | `1000` | Default chunk size (characters) |
| `CHUNK_OVERLAP` | `200` | Default overlap (characters) |
| `MINIMUM_CHUNK_LENGTH` | `1` | Minimum valid chunk length |
| `CHUNK_SEPARATORS` | `\n\n|\n|. \| ` | Separator list (`|` delimited) |
| `CHUNK_SERVICE_PORT` | `8004` | Service port |

## Extensibility

Implement `BaseChunker` and inject into `ChunkService`:

```python
from backend.services.chunk_service.services.chunk_service import ChunkService
from my_chunker import TokenChunker

service = ChunkService(chunker=TokenChunker())
```
