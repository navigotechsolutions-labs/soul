"""Self-Service API Key Management & Authentication Engine for Soul.

Enables anyone to generate their own personal API key, authenticate requests,
and track usage metrics with local SQLite persistence.
"""

import hashlib
import os
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class APIKeyInfo:
    key_id: str
    client_name: str
    email: str
    created_at: float
    is_active: bool
    request_count: int
    tier: str


class APIKeyManager:
    """Manages creation, hashing, validation, and usage tracking of self-service API keys."""

    DEFAULT_DB_PATH = Path(os.getenv("SOUL_DB_PATH", "soul_keys.db"))

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path or self.DEFAULT_DB_PATH)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes the database schema if not already present."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_hash TEXT PRIMARY KEY,
                    key_prefix TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    email TEXT,
                    created_at REAL NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    tier TEXT NOT NULL DEFAULT 'free'
                )
            """)
            conn.commit()

    @staticmethod
    def _hash_key(api_key: str) -> str:
        """Computes SHA-256 hash of the API key for safe storage."""
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def generate_key(self, client_name: str, email: str = "", tier: str = "free") -> dict:
        """Generates a new self-service API key for any user or developer."""
        clean_name = client_name.strip() or "Anonymous Developer"
        clean_email = email.strip()

        # Generate secure token: soul_live_<32 hex chars>
        raw_secret = secrets.token_hex(20)
        api_key = f"soul_live_{raw_secret}"
        key_hash = self._hash_key(api_key)
        key_prefix = api_key[:14] + "..."  # e.g. soul_live_a1b2...

        now = time.time()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO api_keys (key_hash, key_prefix, client_name, email, created_at, is_active, request_count, tier)
                VALUES (?, ?, ?, ?, ?, 1, 0, ?)
                """,
                (key_hash, key_prefix, clean_name, clean_email, now, tier)
            )
            conn.commit()

        return {
            "api_key": api_key,
            "key_prefix": key_prefix,
            "client_name": clean_name,
            "email": clean_email,
            "tier": tier,
            "created_at": now,
            "rate_limit": "120 requests/minute",
            "message": "Store this key safely. You can use it as a Bearer token in your HTTP Authorization header.",
        }

    def validate_key(self, api_key: str) -> bool:
        """Validates whether an API key exists and is active."""
        if not api_key or not api_key.startswith("soul_"):
            return False

        key_hash = self._hash_key(api_key)
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT is_active FROM api_keys WHERE key_hash = ?",
                (key_hash,)
            ).fetchone()
            if row and row["is_active"] == 1:
                return True
        return False

    def record_usage(self, api_key: str) -> bool:
        """Increments the request count for an API key."""
        if not api_key:
            return False

        key_hash = self._hash_key(api_key)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE api_keys SET request_count = request_count + 1 WHERE key_hash = ? AND is_active = 1",
                (key_hash,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_key_info(self, api_key: str) -> Optional[dict]:
        """Retrieves usage and metadata for a given API key."""
        key_hash = self._hash_key(api_key)
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT key_prefix, client_name, email, created_at, is_active, request_count, tier FROM api_keys WHERE key_hash = ?",
                (key_hash,)
            ).fetchone()
            if row:
                return {
                    "key_prefix": row["key_prefix"],
                    "client_name": row["client_name"],
                    "email": row["email"],
                    "created_at": row["created_at"],
                    "is_active": bool(row["is_active"]),
                    "request_count": row["request_count"],
                    "tier": row["tier"],
                }
        return None

    def revoke_key(self, api_key: str) -> bool:
        """Deactivates an API key."""
        key_hash = self._hash_key(api_key)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE api_keys SET is_active = 0 WHERE key_hash = ?",
                (key_hash,)
            )
            conn.commit()
            return cursor.rowcount > 0
