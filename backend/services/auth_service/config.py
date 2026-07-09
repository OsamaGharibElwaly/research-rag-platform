"""Auth service configuration."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auth.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
SERVICE_NAME = "auth_service"
SERVICE_PORT = int(os.getenv("AUTH_SERVICE_PORT", "8001"))
