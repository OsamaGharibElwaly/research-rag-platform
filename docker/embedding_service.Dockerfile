FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY backend/services/embedding_service/requirements.txt ./embedding-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r embedding-requirements.txt

COPY backend ./backend

ENV PYTHONPATH=/app
ENV EMBEDDING_DATABASE_URL=sqlite:///./embedding.db
ENV CHUNK_DATABASE_URL=sqlite:///./chunk.db
ENV UPLOAD_DATABASE_URL=sqlite:///./upload.db
ENV EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
ENV EMBEDDING_BATCH_SIZE=32

CMD ["uvicorn", "backend.services.embedding_service.main:app", "--host", "0.0.0.0", "--port", "8005"]
