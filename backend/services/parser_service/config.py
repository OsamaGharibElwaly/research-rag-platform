"""Parser service configuration."""
import os

PARSER_DATABASE_URL = os.getenv("PARSER_DATABASE_URL", "sqlite:///./parser.db")
UPLOAD_DATABASE_URL = os.getenv("UPLOAD_DATABASE_URL", "sqlite:///./upload.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
SERVICE_NAME = "parser_service"
SERVICE_PORT = int(os.getenv("PARSER_SERVICE_PORT", "8003"))
