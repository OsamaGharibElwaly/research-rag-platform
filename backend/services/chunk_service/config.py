"""Chunk service configuration."""
import os

CHUNK_DATABASE_URL = os.getenv("CHUNK_DATABASE_URL", "sqlite:///./chunk.db")
PARSER_DATABASE_URL = os.getenv("PARSER_DATABASE_URL", "sqlite:///./parser.db")
UPLOAD_DATABASE_URL = os.getenv("UPLOAD_DATABASE_URL", "sqlite:///./upload.db")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
MINIMUM_CHUNK_LENGTH = int(os.getenv("MINIMUM_CHUNK_LENGTH", "1"))
CHUNK_SEPARATORS = os.getenv("CHUNK_SEPARATORS", "\n\n|\n|. | ").split("|")

SERVICE_NAME = "chunk_service"
SERVICE_PORT = int(os.getenv("CHUNK_SERVICE_PORT", "8004"))
