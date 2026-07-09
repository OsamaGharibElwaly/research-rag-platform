# Parser Service

Extracts text and metadata from uploaded PDF research papers.

## Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/parse` | Parse an uploaded paper by `paper_id` |

## Request

```json
{ "paper_id": 1 }
```

## Workflow

1. Verify JWT
2. Verify paper ownership via upload database
3. Load PDF from upload storage (no file duplication)
4. Parse with `ParserService` (default: PyMuPDF)
5. Store result in parser database
6. Return structured response

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `PARSER_DATABASE_URL` | `sqlite:///./parser.db` | Parser metadata DB |
| `UPLOAD_DATABASE_URL` | `sqlite:///./upload.db` | Upload service DB (read-only) |
| `UPLOAD_DIR` | `./uploads` | PDF storage path |
| `PARSER_SERVICE_PORT` | `8003` | Service port |

## Extensibility

Replace the parser backend by implementing `BasePDFParser` and passing it to `ParserService`.

```python
from backend.services.parser_service.services.parser_service import ParserService
from my_parser import CustomParser

service = ParserService(parser=CustomParser())
```
