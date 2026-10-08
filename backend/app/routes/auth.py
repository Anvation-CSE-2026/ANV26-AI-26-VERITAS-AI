"""Authentication routes: registration, login, logout, and current user profile."""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRecord,
    UserRegisterRequest,
    UserResponse,
)
from app.services.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.services.storage import get_user_by_email, save_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest) -> TokenResponse:
    """Registers a new user account with secure password hashing and returns an auth token."""
    existing = get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    user_id = str(uuid4())
    now_utc = datetime.now(timezone.utc).isoformat()
    pwd_hash = hash_password(request.password)

    user = UserRecord(
        id=user_id,
        email=request.email,
        password_hash=pwd_hash,
        created_at=now_utc,
        trial_used=False,
    )
    save_user(user)

    token = create_access_token(user_id=user.id, email=user.email)
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        trial_used=user.trial_used,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=60 * 24 * 60,
        user=user_response,
    )


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest) -> TokenResponse:
    """Authenticates user credentials and returns a signed access token."""
    user = get_user_by_email(request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user_id=user.id, email=user.email)
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        trial_used=user.trial_used,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=60 * 24 * 60,
        user=user_response,
    )


@router.post("/logout")
def logout(current_user: UserRecord = Depends(get_current_user)) -> dict:
    """Invalidates user session from the client."""
    return {
        "status": "ok",
        "message": f"Successfully logged out user {current_user.email}.",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserRecord = Depends(get_current_user)) -> UserResponse:
    """Returns the authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        trial_used=current_user.trial_used,
    )

