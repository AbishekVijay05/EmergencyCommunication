# =============================================================================
# JWT Token Handler — Create, Verify, Refresh
# =============================================================================
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt


class JWTHandler:
    """JWT token management with HS256/RS256 signing."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_expire_minutes: int = 30,
        refresh_expire_days: int = 7,
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire = timedelta(minutes=access_expire_minutes)
        self._refresh_expire = timedelta(days=refresh_expire_days)

    def create_access_token(
        self,
        subject: str,
        role: str = "responder",
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create a JWT access token.

        Args:
            subject: User ID or username
            role: User role for RBAC
            extra_claims: Additional JWT claims

        Returns:
            Encoded JWT string
        """
        now = datetime.now(timezone.utc)
        claims = {
            "sub": subject,
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + self._access_expire,
        }
        if extra_claims:
            claims.update(extra_claims)

        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, subject: str) -> str:
        """Create a JWT refresh token (longer-lived)."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": subject,
            "type": "refresh",
            "iat": now,
            "exp": now + self._refresh_expire,
        }
        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode a JWT token.

        Returns:
            Decoded claims dictionary

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")

    def get_subject(self, token: str) -> str:
        """Extract subject (user ID) from token."""
        payload = self.verify_token(token)
        subject = payload.get("sub")
        if not subject:
            raise ValueError("Token missing subject claim")
        return subject

    def get_role(self, token: str) -> str:
        """Extract role from token."""
        payload = self.verify_token(token)
        return payload.get("role", "responder")

    def is_access_token(self, token: str) -> bool:
        """Check if token is an access token."""
        try:
            payload = self.verify_token(token)
            return payload.get("type") == "access"
        except ValueError:
            return False

    def is_refresh_token(self, token: str) -> bool:
        """Check if token is a refresh token."""
        try:
            payload = self.verify_token(token)
            return payload.get("type") == "refresh"
        except ValueError:
            return False
