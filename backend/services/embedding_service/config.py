"""Embedding service configuration."""
import os

EMBEDDING_DATABASE_URL = os.getenv("EMBEDDING_DATABASE_URL", "sqlite:///./embedding.db")
CHUNK_DATABASE_URL = os.getenv("CHUNK_DATABASE_URL", "sqlite:///./chunk.db")
UPLOAD_DATABASE_URL = os.getenv("UPLOAD_DATABASE_URL", "sqlite:///./upload.db")

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

SERVICE_NAME = "embedding_service"
SERVICE_PORT = int(os.getenv("EMBEDDING_SERVICE_PORT", "8005"))
