"""Unit tests for User Authentication, JWT Tokens, and User API Key Management."""

import os
import tempfile
import pytest

from soul.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from soul.auth.user_db import UserManager


@pytest.fixture
def temp_user_mgr():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    manager = UserManager(db_path=db_path)
    yield manager

    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass


def test_password_hashing():
    """Verify PBKDF2 password hashing and constant-time verification."""
    password = "SuperSecretPassword!123"
    hashed = hash_password(password)

    assert hashed.startswith("pbkdf2:sha256:")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_creation_and_decoding():
    """Verify RFC 7519 HS256 JWT creation and decoding."""
    payload = {"sub": "user-12345", "email": "alice@navigotechsolutions.com", "role": "admin"}
    secret = "test_jwt_secret_key"

    token = create_access_token(payload, expires_delta_minutes=30, secret_key=secret)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = decode_access_token(token, secret_key=secret)
    assert decoded is not None
    assert decoded["sub"] == "user-12345"
    assert decoded["email"] == "alice@navigotechsolutions.com"
    assert "exp" in decoded

    # Tampered token or wrong secret should fail
    assert decode_access_token(token, secret_key="wrong_secret") is None
    assert decode_access_token(token + "tampered", secret_key=secret) is None


def test_user_registration_and_auth(temp_user_mgr):
    """Test user signup, duplicate prevention, and login authentication."""
    # 1. Signup
    user = temp_user_mgr.create_user_with_email(
        email="john.doe@example.com",
        password="MyPassword2026",
        full_name="John Doe",
    )
    assert user["email"] == "john.doe@example.com"
    assert user["full_name"] == "John Doe"
    assert user["tier"] == "free"

    # 2. Duplicate signup should raise ValueError
    with pytest.raises(ValueError):
        temp_user_mgr.create_user_with_email("john.doe@example.com", "another_pass")

    # 3. Successful authentication
    auth_user = temp_user_mgr.authenticate_user("john.doe@example.com", "MyPassword2026")
    assert auth_user is not None
    assert auth_user["id"] == user["id"]

    # 4. Failed authentication (wrong password / wrong email)
    assert temp_user_mgr.authenticate_user("john.doe@example.com", "WrongPassword") is None
    assert temp_user_mgr.authenticate_user("unknown@example.com", "MyPassword2026") is None


def test_google_user_provisioning(temp_user_mgr):
    """Test finding or auto-provisioning a Google OAuth authenticated user."""
    # First time: auto-provisions
    user = temp_user_mgr.find_or_create_google_user(
        email="google.dev@example.com",
        full_name="Google Developer",
        avatar_url="https://lh3.googleusercontent.com/avatar.jpg",
        google_sub="google-sub-9999",
    )
    assert user["auth_provider"] == "google"
    assert user["email"] == "google.dev@example.com"

    # Second time: finds existing user
    existing = temp_user_mgr.find_or_create_google_user(
        email="google.dev@example.com",
        full_name="Google Developer Updated",
    )
    assert existing["id"] == user["id"]
    assert existing["full_name"] == "Google Developer Updated"


def test_user_api_keys_lifecycle(temp_user_mgr):
    """Test creating, listing, validating, and revoking API keys for a user."""
    user = temp_user_mgr.create_user_with_email("developer@company.org", "Pass1234!")
    user_id = user["id"]

    # 1. Create key
    key_info = temp_user_mgr.create_api_key_for_user(user_id, key_name="Production Bot")
    assert key_info["api_key"].startswith("soul_live_")
    assert key_info["name"] == "Production Bot"
    api_key = key_info["api_key"]
    key_id = key_info["id"]

    # 2. List keys
    keys = temp_user_mgr.list_api_keys_for_user(user_id)
    assert len(keys) == 1
    assert keys[0]["id"] == key_id
    assert keys[0]["name"] == "Production Bot"
    assert keys[0]["request_count"] == 0

    # 3. Validate key and track usage
    validated = temp_user_mgr.validate_api_key(api_key)
    assert validated is not None
    assert validated["user_id"] == user_id
    assert validated["email"] == "developer@company.org"

    # Request count incremented
    keys_after = temp_user_mgr.list_api_keys_for_user(user_id)
    assert keys_after[0]["request_count"] == 1

    # 4. Revoke key
    assert temp_user_mgr.revoke_api_key_for_user(user_id, key_id) is True

    # Validation after revoke should fail
    assert temp_user_mgr.validate_api_key(api_key) is None


def test_api_auth_endpoints_flow():
    """Test full FastAPI signup, login, me, key generation, and appraise via TestClient."""
    import uuid
    from fastapi.testclient import TestClient
    from soul.server import app

    client = TestClient(app)

    # 1. Signup
    email = f"agent.{uuid.uuid4().hex[:6]}@navigotech.ai"
    signup_res = client.post(
        "/v1/auth/signup",
        json={"email": email, "password": "SecretPassword123", "full_name": "Agent Builder"},
    )
    assert signup_res.status_code == 200
    data = signup_res.json()
    assert "access_token" in data
    jwt_token = data["access_token"]
    assert data["user"]["email"] == email

    # 2. GET /v1/auth/me
    me_res = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {jwt_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 3. Create User API Key
    create_key_res = client.post(
        "/v1/keys",
        json={"name": "SaaS Test Key"},
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert create_key_res.status_code == 200
    key_data = create_key_res.json()
    assert "api_key" in key_data
    user_api_key = key_data["api_key"]
    key_id = key_data["id"]

    # 4. List keys
    list_keys_res = client.get("/v1/keys", headers={"Authorization": f"Bearer {jwt_token}"})
    assert list_keys_res.status_code == 200
    assert len(list_keys_res.json()) >= 1

    # 5. Use user_api_key on /v1/appraise
    appraise_res = client.post(
        "/v1/appraise",
        json={"text": "I am so overwhelmed by work and life right now."},
        headers={"Authorization": f"Bearer {user_api_key}"},
    )
    assert appraise_res.status_code == 200
    assert "adversity" in appraise_res.json()

    # 6. Revoke key
    revoke_res = client.delete(f"/v1/keys/{key_id}", headers={"Authorization": f"Bearer {jwt_token}"})
    assert revoke_res.status_code == 200

    # 7. Test Google login demo token
    google_res = client.post("/v1/auth/google", json={"token": "demo_google_token"})
    assert google_res.status_code == 200
    assert "access_token" in google_res.json()
