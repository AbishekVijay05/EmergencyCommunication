# =============================================================================
# RSA-2048 Key Generation, Encryption, and Signing
# =============================================================================
from __future__ import annotations

import base64
from dataclasses import dataclass

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


@dataclass
class RSAKeyPair:
    """RSA key pair container."""
    private_key_pem: str
    public_key_pem: str


class RSAHandler:
    """RSA-2048 key exchange, encryption, and digital signatures."""

    def __init__(self, key_size: int = 2048):
        self._key_size = key_size

    def generate_keypair(self) -> RSAKeyPair:
        """Generate a new RSA key pair."""
        key = RSA.generate(self._key_size)
        return RSAKeyPair(
            private_key_pem=key.export_key("PEM").decode(),
            public_key_pem=key.publickey().export_key("PEM").decode(),
        )

    def encrypt_with_public_key(self, plaintext: str, public_key_pem: str) -> str:
        """Encrypt data with RSA public key (for key exchange).

        Note: RSA encryption is limited to small payloads (< key_size/8 - 42 bytes).
        Use this for encrypting AES session keys, not large messages.

        Returns:
            Base64-encoded ciphertext
        """
        public_key = RSA.import_key(public_key_pem)
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
        ciphertext = cipher.encrypt(plaintext.encode("utf-8"))
        return base64.b64encode(ciphertext).decode()

    def decrypt_with_private_key(self, ciphertext_b64: str, private_key_pem: str) -> str:
        """Decrypt data with RSA private key.

        Returns:
            Decrypted plaintext string
        """
        private_key = RSA.import_key(private_key_pem)
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
        ciphertext = base64.b64decode(ciphertext_b64)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode("utf-8")

    def sign(self, message: str, private_key_pem: str) -> str:
        """Create a digital signature for a message.

        Returns:
            Base64-encoded signature
        """
        private_key = RSA.import_key(private_key_pem)
        h = SHA256.new(message.encode("utf-8"))
        signature = pkcs1_15.new(private_key).sign(h)
        return base64.b64encode(signature).decode()

    def verify(self, message: str, signature_b64: str, public_key_pem: str) -> bool:
        """Verify a digital signature.

        Returns:
            True if signature is valid
        """
        try:
            public_key = RSA.import_key(public_key_pem)
            h = SHA256.new(message.encode("utf-8"))
            signature = base64.b64decode(signature_b64)
            pkcs1_15.new(public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False

    def encrypt_aes_key(self, aes_key: bytes, public_key_pem: str) -> str:
        """Encrypt an AES session key with RSA public key for key exchange.

        This is the standard hybrid encryption pattern:
        1. Generate AES key
        2. Encrypt message with AES
        3. Encrypt AES key with recipient's RSA public key
        4. Send encrypted AES key + AES-encrypted message

        Returns:
            Base64-encoded encrypted AES key
        """
        public_key = RSA.import_key(public_key_pem)
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
        encrypted_key = cipher.encrypt(aes_key)
        return base64.b64encode(encrypted_key).decode()

    def decrypt_aes_key(self, encrypted_key_b64: str, private_key_pem: str) -> bytes:
        """Decrypt an AES session key with RSA private key.

        Returns:
            Raw AES key bytes
        """
        private_key = RSA.import_key(private_key_pem)
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
        encrypted_key = base64.b64decode(encrypted_key_b64)
        return cipher.decrypt(encrypted_key)
