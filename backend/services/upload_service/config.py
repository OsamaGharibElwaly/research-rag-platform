"""Upload service configuration."""
import os

DATABASE_URL = os.getenv("UPLOAD_DATABASE_URL", "sqlite:///./upload.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
SERVICE_NAME = "upload_service"
SERVICE_PORT = int(os.getenv("UPLOAD_SERVICE_PORT", "8002"))
