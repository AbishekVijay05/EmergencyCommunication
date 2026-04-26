# =============================================================================
# Redis-Backed Key Store for Session Keys
# =============================================================================
from __future__ import annotations

import json
from typing import Optional

import redis.asyncio as aioredis


class KeyStore:
    """Redis-backed storage for encryption keys and session data."""

    def __init__(self, redis_url: str):
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._prefix = "keystore:"

    async def store_user_public_key(self, user_id: str, public_key_pem: str) -> None:
        """Store a user's RSA public key."""
        await self._redis.set(
            f"{self._prefix}pubkey:{user_id}",
            public_key_pem,
        )

    async def get_user_public_key(self, user_id: str) -> Optional[str]:
        """Retrieve a user's RSA public key."""
        return await self._redis.get(f"{self._prefix}pubkey:{user_id}")

    async def store_session_key(
        self,
        session_id: str,
        encrypted_key: str,
        ttl_seconds: int = 3600,
    ) -> None:
        """Store an encrypted session key with TTL."""
        await self._redis.setex(
            f"{self._prefix}session:{session_id}",
            ttl_seconds,
            encrypted_key,
        )

    async def get_session_key(self, session_id: str) -> Optional[str]:
        """Retrieve an encrypted session key."""
        return await self._redis.get(f"{self._prefix}session:{session_id}")

    async def revoke_session(self, session_id: str) -> None:
        """Revoke a session key."""
        await self._redis.delete(f"{self._prefix}session:{session_id}")

    async def blacklist_token(self, token_jti: str, ttl_seconds: int = 86400) -> None:
        """Add a JWT to the blacklist (for logout)."""
        await self._redis.setex(
            f"{self._prefix}blacklist:{token_jti}",
            ttl_seconds,
            "1",
        )

    async def is_token_blacklisted(self, token_jti: str) -> bool:
        """Check if a JWT is blacklisted."""
        return await self._redis.exists(f"{self._prefix}blacklist:{token_jti}") > 0

    async def close(self) -> None:
        """Close Redis connection."""
        await self._redis.close()
