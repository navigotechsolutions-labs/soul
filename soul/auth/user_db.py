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

            # Community feedback & ratings table (Rate Soul Engine)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id TEXT PRIMARY KEY,
                    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
                    author_name TEXT,
                    feedback TEXT,
                    user_id TEXT,
                    created_at REAL NOT NULL
                )
            """)

            # Email OTP verification table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_otps (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    consumed INTEGER NOT NULL DEFAULT 0
                )
            """)

            # Key lookup index
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_keys_hash ON user_api_keys(key_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_keys_user ON user_api_keys(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_created ON ratings(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_otps_lookup ON email_otps(email, expires_at, consumed)")
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

    # --- Community Ratings & Reviews ---

    def submit_rating(
        self,
        score: int,
        author_name: Optional[str] = None,
        feedback: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Saves a developer/user rating (1 to 5 stars) and optional feedback."""
        score = max(1, min(5, int(score)))
        rating_id = str(uuid.uuid4())
        now = time.time()
        name = (author_name or "Anonymous Engineer").strip()
        comment = (feedback or "").strip()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO ratings (id, score, author_name, feedback, user_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (rating_id, score, name, comment, user_id, now),
            )
            conn.commit()

        return {
            "id": rating_id,
            "score": score,
            "author_name": name,
            "feedback": comment,
            "created_at": now,
        }

    def get_ratings_summary(self) -> dict[str, Any]:
        """Returns average score, total rating count, and recent reviews."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total, AVG(score) as avg_score FROM ratings")
            agg = cursor.fetchone()
            total = agg["total"] or 0
            avg_score = round(float(agg["avg_score"] or 5.0), 2)

            cursor.execute(
                """
                SELECT id, score, author_name, feedback, created_at
                FROM ratings
                ORDER BY created_at DESC
                LIMIT 6
                """
            )
            recent = [dict(r) for r in cursor.fetchall()]

        return {
            "total_ratings": total,
            "average_score": avg_score,
            "recent_reviews": recent,
        }

    # --- Email OTP Authentication ---

    def store_otp(self, email: str, code: str, validity_seconds: int = 600) -> str:
        """Stores a hashed 6-digit OTP code with expiration window."""
        email = email.lower().strip()
        code_hash = hash_password(code)
        otp_id = str(uuid.uuid4())
        now = time.time()
        expires_at = now + validity_seconds

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Invalidate any prior unconsumed OTPs for this email
            cursor.execute(
                "UPDATE email_otps SET consumed = 1 WHERE email = ? AND consumed = 0",
                (email,),
            )
            cursor.execute(
                """
                INSERT INTO email_otps (id, email, code_hash, created_at, expires_at, attempts, consumed)
                VALUES (?, ?, ?, ?, ?, 0, 0)
                """,
                (otp_id, email, code_hash, now, expires_at),
            )
            conn.commit()

        return otp_id

    def verify_otp(self, email: str, code: str) -> bool:
        """Verifies the latest unconsumed OTP code for an email address."""
        email = email.lower().strip()
        now = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, code_hash, attempts, expires_at 
                FROM email_otps 
                WHERE email = ? AND consumed = 0 AND expires_at > ?
                ORDER BY created_at DESC 
                LIMIT 1
                """,
                (email, now),
            )
            row = cursor.fetchone()
            if not row:
                return False

            otp_id = row["id"]
            attempts = row["attempts"] + 1

            if attempts > 5:
                # Rate-limit: consume code after 5 failed attempts
                cursor.execute(
                    "UPDATE email_otps SET attempts = ?, consumed = 1 WHERE id = ?",
                    (attempts, otp_id),
                )
                conn.commit()
                return False

            is_valid = verify_password(code.strip(), row["code_hash"])

            if is_valid:
                cursor.execute(
                    "UPDATE email_otps SET attempts = ?, consumed = 1 WHERE id = ?",
                    (attempts, otp_id),
                )
            else:
                cursor.execute(
                    "UPDATE email_otps SET attempts = ? WHERE id = ?",
                    (attempts, otp_id),
                )
            conn.commit()

            return is_valid

    def find_or_create_otp_user(self, email: str, full_name: Optional[str] = None) -> dict[str, Any]:
        """Finds or auto-provisions an account authenticated via verified Email OTP."""
        email = email.lower().strip()
        now = time.time()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row:
                user_id = row["id"]
                cursor.execute(
                    """
                    UPDATE users 
                    SET last_login_at = ?,
                        full_name = COALESCE(NULLIF(?, ''), full_name)
                    WHERE id = ?
                    """,
                    (now, full_name, user_id),
                )
                conn.commit()
                return self.get_user_by_id(user_id)
            else:
                user_id = str(uuid.uuid4())
                name = (full_name or email.split("@")[0].replace(".", " ").title()).strip()
                cursor.execute(
                    """
                    INSERT INTO users (id, email, full_name, avatar_url, auth_provider, tier, is_active, created_at, last_login_at)
                    VALUES (?, ?, ?, '', 'email_otp', 'free', 1, ?, ?)
                    """,
                    (user_id, email, name, now, now),
                )
                conn.commit()
                return self.get_user_by_id(user_id)

