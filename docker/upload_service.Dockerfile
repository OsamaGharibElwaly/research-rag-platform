FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

RUN mkdir -p /app/uploads

ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/uploads

CMD ["uvicorn", "backend.services.upload_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
