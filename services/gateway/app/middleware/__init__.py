# =============================================================================
# Auth Middleware — JWT Token Verification
# =============================================================================
from __future__ import annotations

from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import get_settings, Settings


security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Verify JWT token from Authorization header."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """Extract current user info from verified token."""
    return {
        "user_id": token_data.get("sub"),
        "role": token_data.get("role", "responder"),
    }
