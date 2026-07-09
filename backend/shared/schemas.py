"""Shared Pydantic schemas used across all services."""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    status: str = "success"
    message: str
    data: Optional[Any] = None


class APIError(BaseModel):
    """Standard API error response."""
    status: str = "error"
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    type: str = "access"  # access or refresh
