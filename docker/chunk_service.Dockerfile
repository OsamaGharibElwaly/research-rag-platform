FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY backend/services/chunk_service/requirements.txt ./chunk-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r chunk-requirements.txt

COPY backend ./backend

ENV PYTHONPATH=/app
ENV CHUNK_DATABASE_URL=sqlite:///./chunk.db
ENV PARSER_DATABASE_URL=sqlite:///./parser.db
ENV UPLOAD_DATABASE_URL=sqlite:///./upload.db

CMD ["uvicorn", "backend.services.chunk_service.main:app", "--host", "0.0.0.0", "--port", "8004"]
