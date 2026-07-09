FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY backend/services/vector_service/requirements.txt ./vector-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r vector-requirements.txt

COPY backend ./backend

ENV PYTHONPATH=/app
ENV VECTOR_DATABASE_URL=sqlite:///./vector.db
ENV EMBEDDING_DATABASE_URL=sqlite:///./embedding.db
ENV CHUNK_DATABASE_URL=sqlite:///./chunk.db
ENV UPLOAD_DATABASE_URL=sqlite:///./upload.db
ENV VECTOR_INDEX_DIR=/app/vector_indexes
ENV VECTOR_BIT_WIDTH=4

CMD ["uvicorn", "backend.services.vector_service.main:app", "--host", "0.0.0.0", "--port", "8006"]
