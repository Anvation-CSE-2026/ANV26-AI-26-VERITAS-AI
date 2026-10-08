"""Security utilities: password hashing, verification, JWT generation,
and FastAPI dependency for authenticated user extraction.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.config import settings
from app.models.auth import UserRecord
from app.services.storage import get_user_by_id

# Reusable HTTPBearer security scheme
bearer_scheme = HTTPBearer(auto_error=False)


# ==========================================================
# SECURE PASSWORD HASHING (PBKDF2-HMAC-SHA256)
# ==========================================================

def hash_password(password: str) -> str:
    """Hashes password using PBKDF2-HMAC-SHA256 with a cryptographically secure random salt."""
    salt = os.urandom(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifies plaintext password against hashed string in constant time."""
    try:
        parts = hashed.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(derived, expected_hash)
    except Exception:
        return False


# ==========================================================
# JWT TOKEN GENERATION & VERIFICATION
# ==========================================================

def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token for the authenticated user."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decodes and validates JWT token signature and expiration."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==========================================================
# FASTAPI AUTH DEPENDENCIES
# ==========================================================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> UserRecord:
    """Strict authentication dependency: requires valid bearer token and existing user."""
    if not credentials or not credentials.credentials:
        # Check backward-compatibility toggle if explicitly enabled
        if settings.allow_legacy_unauthenticated_access:
            return UserRecord(
                id="legacy-unauthenticated-user",
                email="legacy@veritas.internal",
                password_hash="",
                created_at=datetime.now(timezone.utc).isoformat(),
                trial_used=False,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[UserRecord]:
    """Optional authentication dependency: returns user if valid token present, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        return get_user_by_id(user_id) if user_id else None
    except HTTPException:
        return None

