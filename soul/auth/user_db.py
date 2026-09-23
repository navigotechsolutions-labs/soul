"""User, Account, and API Key Database Management."""

import hashlib
import os
import secrets
import sqlite3
import time
import uuid
from typing import Any, Optional

from soul.auth.security import hash_password, verify_password


class UserManager:
    """Manages user accounts, authentication, and multi-key provisioning."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("SOUL_USERS_DB_PATH", "soul_users.db")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    full_name TEXT,
                    avatar_url TEXT,
                    auth_provider TEXT NOT NULL DEFAULT 'email',
                    google_sub TEXT,
                    tier TEXT NOT NULL DEFAULT 'free',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at REAL NOT NULL,
                    last_login_at REAL
                )
            """)

            # User API keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_hash TEXT UNIQUE NOT NULL,
                    key_prefix TEXT NOT NULL,
                    name TEXT NOT NULL,
                    tier TEXT NOT NULL DEFAULT 'free',
                    rate_limit TEXT NOT NULL DEFAULT '120 req/min',
                    request_count INTEGER NOT NULL DEFAULT 0,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at REAL NOT NULL,
                    last_used_at REAL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Key lookup index
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_keys_hash ON user_api_keys(key_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_keys_user ON user_api_keys(user_id)")
            conn.commit()

    # --- User Account Management ---

    def create_user_with_email(
        self, email: str, password: str, full_name: Optional[str] = None
    ) -> dict[str, Any]:
        """Registers a new user with email and password."""
        email = email.lower().strip()
        user_id = str(uuid.uuid4())
        hashed = hash_password(password)
        now = time.time()
        name = full_name.strip() if full_name else email.split("@")[0]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO users (id, email, password_hash, full_name, auth_provider, tier, is_active, created_at, last_login_at)
                    VALUES (?, ?, ?, ?, 'email', 'free', 1, ?, ?)
                    """,
                    (user_id, email, hashed, name, now, now),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError("An account with this email address already exists.")

        return self.get_user_by_id(user_id)

    def authenticate_user(self, email: str, password: str) -> Optional[dict[str, Any]]:
        """Authenticates a user with email and password."""
        email = email.lower().strip()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
            row = cursor.fetchone()
            if not row or not row["password_hash"]:
                return None

            if verify_password(password, row["password_hash"]):
                cursor.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (time.time(), row["id"]))
                conn.commit()
                return dict(row)
        return None

    def find_or_create_google_user(
        self, email: str, full_name: str, avatar_url: str = "", google_sub: str = ""
    ) -> dict[str, Any]:
        """Finds or provisions an account authenticated via Google OAuth."""
        email = email.lower().strip()
        now = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row:
                # Update existing user
                user_id = row["id"]
                cursor.execute(
                    """
                    UPDATE users 
                    SET full_name = COALESCE(NULLIF(?, ''), full_name),
                        avatar_url = COALESCE(NULLIF(?, ''), avatar_url),
                        google_sub = COALESCE(NULLIF(?, ''), google_sub),
                        last_login_at = ?
                    WHERE id = ?
                    """,
                    (full_name, avatar_url, google_sub, now, user_id),
                )
                conn.commit()
                return self.get_user_by_id(user_id)
            else:
                # Provision new Google user
                user_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO users (id, email, full_name, avatar_url, auth_provider, google_sub, tier, is_active, created_at, last_login_at)
                    VALUES (?, ?, ?, ?, 'google', ?, 'free', 1, ?, ?)
                    """,
                    (user_id, email, full_name, avatar_url, google_sub, now, now),
                )
                conn.commit()
                return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: str) -> Optional[dict[str, Any]]:
        """Retrieves user profile without password hash."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, full_name, avatar_url, auth_provider, tier, is_active, created_at, last_login_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """Retrieves user profile by email."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, full_name, avatar_url, auth_provider, tier, is_active, created_at, last_login_at FROM users WHERE email = ?", (email.lower().strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- User API Key Lifecycle ---

    def create_api_key_for_user(
        self, user_id: str, key_name: str = "Default API Key"
    ) -> dict[str, Any]:
        """Generates a new secret API key for a specific registered user."""
        raw_secret = f"soul_live_{secrets.token_hex(20)}"
        key_hash = hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()
        key_prefix = raw_secret[:14] + "..."
        key_id = str(uuid.uuid4())
        now = time.time()

        user = self.get_user_by_id(user_id)
        tier = user["tier"] if user else "free"
        rate_limit = "120 req/min"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_api_keys (id, user_id, key_hash, key_prefix, name, tier, rate_limit, request_count, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1, ?)
                """,
                (key_id, user_id, key_hash, key_prefix, key_name, tier, rate_limit, now),
            )
            conn.commit()

        return {
            "id": key_id,
            "api_key": raw_secret,  # Shown only once!
            "key_prefix": key_prefix,
            "name": key_name,
            "tier": tier,
            "rate_limit": rate_limit,
            "created_at": now,
        }

    def list_api_keys_for_user(self, user_id: str) -> list[dict[str, Any]]:
        """Lists all API keys created by a user (secret hashes excluded)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, key_prefix, name, tier, rate_limit, request_count, is_active, created_at, last_used_at
                FROM user_api_keys
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def revoke_api_key_for_user(self, user_id: str, key_id: str) -> bool:
        """Revokes an API key belonging to a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_api_keys SET is_active = 0 WHERE id = ? AND user_id = ?",
                (key_id, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def validate_api_key(self, api_key: str) -> Optional[dict[str, Any]]:
        """Validates any incoming API key, checks active status, and returns key & user metadata."""
        if not api_key or not isinstance(api_key, str):
            return None

        key_hash = hashlib.sha256(api_key.strip().encode("utf-8")).hexdigest()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT k.id as key_id, k.user_id, k.key_prefix, k.name as key_name, k.tier, k.rate_limit,
                       k.request_count, k.is_active, u.email, u.full_name
                FROM user_api_keys k
                JOIN users u ON k.user_id = u.id
                WHERE k.key_hash = ? AND k.is_active = 1 AND u.is_active = 1
                """,
                (key_hash,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            # Increment request count
            cursor.execute(
                "UPDATE user_api_keys SET request_count = request_count + 1, last_used_at = ? WHERE id = ?",
                (time.time(), row["key_id"]),
            )
            conn.commit()
            return dict(row)
