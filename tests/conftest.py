"""Shared pytest fixtures."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.services.auth_service.main import app as auth_app
from backend.services.auth_service.models import Base as AuthBase
from backend.services.auth_service.models import get_db as auth_get_db
from backend.services.upload_service.main import app as upload_app
from backend.services.upload_service.models import Base as UploadBase
from backend.services.upload_service.models import get_db as upload_get_db
from backend.shared.auth import create_access_token

AUTH_DB_URL = "sqlite:///:memory:"
UPLOAD_DB_URL = "sqlite:///:memory:"

auth_engine = create_engine(
    AUTH_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
upload_engine = create_engine(
    UPLOAD_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AuthTestingSession = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)
UploadTestingSession = sessionmaker(autocommit=False, autoflush=False, bind=upload_engine)

AuthBase.metadata.create_all(bind=auth_engine)
UploadBase.metadata.create_all(bind=upload_engine)


def _auth_db_override():
    db = AuthTestingSession()
    try:
        yield db
    finally:
        db.close()


def _upload_db_override():
    db = UploadTestingSession()
    try:
        yield db
    finally:
        db.close()


auth_app.dependency_overrides[auth_get_db] = _auth_db_override
upload_app.dependency_overrides[upload_get_db] = _upload_db_override


@pytest.fixture
def auth_client():
    return TestClient(auth_app)


@pytest.fixture
def upload_client(tmp_path, monkeypatch):
    upload_dir = str(tmp_path / "uploads")
    monkeypatch.setattr("backend.services.upload_service.config.UPLOAD_DIR", upload_dir)
    monkeypatch.setattr("backend.services.upload_service.services.UPLOAD_DIR", upload_dir)
    return TestClient(upload_app)


@pytest.fixture
def auth_headers(auth_client):
    auth_client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User",
        },
    )
    login_response = auth_client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers():
    token = create_access_token({"sub": "999", "email": "other@example.com"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf():
    return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
