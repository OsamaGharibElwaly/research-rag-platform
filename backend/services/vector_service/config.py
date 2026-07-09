"""Vector service configuration."""
import os

VECTOR_DATABASE_URL = os.getenv("VECTOR_DATABASE_URL", "sqlite:///./vector.db")
EMBEDDING_DATABASE_URL = os.getenv("EMBEDDING_DATABASE_URL", "sqlite:///./embedding.db")
CHUNK_DATABASE_URL = os.getenv("CHUNK_DATABASE_URL", "sqlite:///./chunk.db")
UPLOAD_DATABASE_URL = os.getenv("UPLOAD_DATABASE_URL", "sqlite:///./upload.db")

VECTOR_ENGINE = os.getenv("VECTOR_ENGINE", "turbovec")
VECTOR_INDEX_DIR = os.getenv("VECTOR_INDEX_DIR", "./vector_indexes")
VECTOR_BIT_WIDTH = int(os.getenv("VECTOR_BIT_WIDTH", "4"))
DEFAULT_TOP_K = int(os.getenv("VECTOR_DEFAULT_TOP_K", "5"))

SERVICE_NAME = "vector_service"
SERVICE_PORT = int(os.getenv("VECTOR_SERVICE_PORT", "8006"))
