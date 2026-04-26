# =============================================================================
# AES-256-GCM Encryption / Decryption
# =============================================================================
from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass

from Crypto.Cipher import AES


@dataclass
class EncryptedPayload:
    """Encrypted message payload with IV, ciphertext, and auth tag."""
    ciphertext: str  # base64
    iv: str          # base64
    tag: str         # base64

    def to_dict(self) -> dict:
        return {"ciphertext": self.ciphertext, "iv": self.iv, "tag": self.tag}

    @classmethod
    def from_dict(cls, data: dict) -> EncryptedPayload:
        return cls(
            ciphertext=data["ciphertext"],
            iv=data["iv"],
            tag=data["tag"],
        )


class AESCipher:
    """AES-256-GCM authenticated encryption.

    Provides confidentiality + integrity + authenticity.
    Each encryption uses a unique 96-bit nonce (IV).
    """

    def __init__(self, key: bytes | None = None):
        """Initialize with a 256-bit key, or generate one."""
        if key is None:
            self._key = os.urandom(32)  # 256 bits
        else:
            if len(key) != 32:
                raise ValueError("AES-256 requires a 32-byte key")
            self._key = key

    @property
    def key(self) -> bytes:
        return self._key

    @property
    def key_b64(self) -> str:
        return base64.b64encode(self._key).decode()

    @classmethod
    def from_b64_key(cls, key_b64: str) -> AESCipher:
        """Create cipher from base64-encoded key."""
        return cls(key=base64.b64decode(key_b64))

    def encrypt(self, plaintext: str, aad: bytes | None = None) -> EncryptedPayload:
        """Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: UTF-8 text to encrypt
            aad: Additional Authenticated Data (optional)

        Returns:
            EncryptedPayload with base64-encoded components
        """
        iv = os.urandom(12)  # 96-bit nonce for GCM
        cipher = AES.new(self._key, AES.MODE_GCM, nonce=iv)

        if aad:
            cipher.update(aad)

        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))

        return EncryptedPayload(
            ciphertext=base64.b64encode(ciphertext).decode(),
            iv=base64.b64encode(iv).decode(),
            tag=base64.b64encode(tag).decode(),
        )

    def decrypt(self, payload: EncryptedPayload, aad: bytes | None = None) -> str:
        """Decrypt an encrypted payload.

        Args:
            payload: EncryptedPayload with base64-encoded components
            aad: Additional Authenticated Data (must match encryption)

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If authentication fails (tampered data)
        """
        iv = base64.b64decode(payload.iv)
        ciphertext = base64.b64decode(payload.ciphertext)
        tag = base64.b64decode(payload.tag)

        cipher = AES.new(self._key, AES.MODE_GCM, nonce=iv)

        if aad:
            cipher.update(aad)

        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode("utf-8")
        except (ValueError, KeyError) as e:
            raise ValueError(f"Decryption failed: authentication error — {e}")

    def benchmark(self, message: str = "Test message for benchmarking", iterations: int = 1000) -> dict:
        """Benchmark encryption/decryption performance."""
        # Encryption benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            payload = self.encrypt(message)
        enc_time = (time.perf_counter() - start) * 1000 / iterations

        # Decryption benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            self.decrypt(payload)
        dec_time = (time.perf_counter() - start) * 1000 / iterations

        return {
            "encryption_avg_ms": round(enc_time, 3),
            "decryption_avg_ms": round(dec_time, 3),
            "total_avg_ms": round(enc_time + dec_time, 3),
            "iterations": iterations,
            "message_bytes": len(message.encode()),
        }
