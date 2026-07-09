"""Auth service API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.shared.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from backend.shared.logger import generate_request_id, get_logger
from backend.shared.schemas import APIResponse

from .models import get_db
from .schemas import TokenRefresh, UserCreate, UserLogin, UserResponse
from .services import authenticate_user, create_user, generate_tokens, get_user_by_id


router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger("auth_service")


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Registration attempt: {user_data.email}")

    user = create_user(db, user_data)
    tokens = generate_tokens(user)

    return APIResponse(
        status="success",
        message="User registered successfully",
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens
        }
    )


@router.post("/login", response_model=APIResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Login attempt: {login_data.email}")

    user = authenticate_user(db, login_data)
    tokens = generate_tokens(user)

    return APIResponse(
        status="success",
        message="Login successful",
        data={
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens
        }
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(refresh_data: TokenRefresh):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Token refresh attempt")

    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    token_data = {
        "sub": payload["sub"],
        "email": payload.get("email", ""),
        "username": payload.get("username", ""),
    }
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return APIResponse(
        status="success",
        message="Token refreshed successfully",
        data={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    )


@router.get("/me", response_model=APIResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Get user profile: {current_user['user_id']}")

    user = get_user_by_id(db, int(current_user["user_id"]))

    return APIResponse(
        status="success",
        message="User profile retrieved",
        data={"user": UserResponse.model_validate(user).model_dump()}
    )