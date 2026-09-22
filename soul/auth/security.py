"""Security utilities: NIST-compliant password hashing and RFC 7519 JWT implementation."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Optional

DEFAULT_JWT_SECRET = os.getenv("SOUL_JWT_SECRET", "soul_super_secret_jwt_signing_key_2026_production")
JWT_ALGORITHM = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def _b64url_encode(data: bytes) -> str:
    """Base64 URL encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data_str: str) -> bytes:
    """Base64 URL decode with padding restoration."""
    padding = 4 - (len(data_str) % 4)
    if padding != 4:
        data_str += "=" * padding
    return base64.urlsafe_b64decode(data_str.encode("utf-8"))


def hash_password(password: str, iterations: int = 100_000) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a cryptographically random salt."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2:sha256:{iterations}${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plain password against the stored PBKDF2 hash in constant time."""
    try:
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False
        algo_part, salt_hex, key_hex = parts
        _, _, iterations_str = algo_part.split(":")
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        calculated_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(calculated_key, expected_key)
    except Exception:
        return False


def create_access_token(
    data: dict[str, Any],
    expires_delta_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    secret_key: str = DEFAULT_JWT_SECRET,
) -> str:
    """Creates an RFC 7519 compliant JWT using HMAC-SHA256."""
    to_encode = data.copy()
    expire = time.time() + (expires_delta_minutes * 60)
    to_encode.update({"exp": expire, "iat": time.time()})

    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(to_encode, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = _b64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str, secret_key: str = DEFAULT_JWT_SECRET) -> Optional[dict[str, Any]]:
    """Decodes and validates an RFC 7519 compliant JWT. Returns None if invalid or expired."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        encoded_header, encoded_payload, encoded_signature = parts

        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _b64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        exp = payload.get("exp")
        if exp is not None and time.time() > float(exp):
            return None

        return payload
    except Exception:
        return None
