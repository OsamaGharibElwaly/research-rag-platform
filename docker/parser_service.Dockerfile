FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY backend/services/parser_service/requirements.txt ./parser-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r parser-requirements.txt

COPY backend ./backend

ENV PYTHONPATH=/app
ENV PARSER_DATABASE_URL=sqlite:///./parser.db
ENV UPLOAD_DATABASE_URL=sqlite:///./upload.db
ENV UPLOAD_DIR=/app/uploads

CMD ["uvicorn", "backend.services.parser_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
