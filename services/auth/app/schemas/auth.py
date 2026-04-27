# =============================================================================
# Auth Pydantic Schemas
# =============================================================================
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    role: str = Field(default="responder", pattern="^(admin|coordinator|responder|observer)$")


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    public_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class KeyExchangeRequest(BaseModel):
    public_key: str


class KeyExchangeResponse(BaseModel):
    server_public_key: str
    encrypted_session_key: str
