# =============================================================================
# Auth Routes — Login, Register, Refresh, Key Exchange
# =============================================================================
from __future__ import annotations

import sys
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

# Add project root to path so we can import security module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.db import get_db
from app.config import get_settings, Settings
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    UserResponse,
    KeyExchangeRequest,
    KeyExchangeResponse,
)
from services.security.jwt_handler import JWTHandler
from services.security.rsa_handler import RSAHandler
from services.security.aes_cipher import AESCipher

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_jwt_handler(settings: Settings) -> JWTHandler:
    return JWTHandler(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_expire_days=settings.jwt_refresh_token_expire_days,
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Check existing
    existing = await db.execute(
        select(User).where((User.username == data.username) | (User.email == data.email))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Generate RSA keypair for the user
    rsa = RSAHandler()
    keypair = rsa.generate_keypair()

    user = User(
        username=data.username,
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        role=data.role,
        public_key=keypair.public_key_pem,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        public_key=user.public_key,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Authenticate user and return JWT tokens."""
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    jwt_handler = _get_jwt_handler(settings)
    access_token = jwt_handler.create_access_token(
        subject=str(user.id),
        role=user.role,
    )
    refresh_token = jwt_handler.create_refresh_token(subject=str(user.id))

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        role=user.role,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Refresh an expired access token."""
    jwt_handler = _get_jwt_handler(settings)

    try:
        payload = jwt_handler.verify_token(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or disabled")

    access_token = jwt_handler.create_access_token(
        subject=str(user.id),
        role=user.role,
    )
    new_refresh = jwt_handler.create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Get current user profile (requires auth header forwarded by gateway)."""
    # In production, user_id comes from gateway X-User-Id header
    # For direct access, we'd need token verification here
    return {"detail": "Use through gateway with authentication"}


@router.post("/keys/exchange", response_model=KeyExchangeResponse)
async def key_exchange(
    data: KeyExchangeRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """RSA key exchange — encrypt an AES session key with client's public key.

    Flow:
    1. Client sends their RSA public key
    2. Server generates AES session key
    3. Server encrypts AES key with client's public key
    4. Server returns its own public key + encrypted session key
    """
    rsa = RSAHandler(key_size=settings.rsa_key_size)
    server_keypair = rsa.generate_keypair()

    # Generate AES session key
    aes = AESCipher()
    encrypted_session_key = rsa.encrypt_aes_key(
        aes_key=aes.key,
        public_key_pem=data.public_key,
    )

    return KeyExchangeResponse(
        server_public_key=server_keypair.public_key_pem,
        encrypted_session_key=encrypted_session_key,
    )
