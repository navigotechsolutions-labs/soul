"""Tests for Self-Service API Key Management and Authentication."""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from soul.engine.api_key_manager import APIKeyManager
from soul.server import app


@pytest.fixture
def temp_key_manager():
    """Create a temporary APIKeyManager with an isolated SQLite database."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    manager = APIKeyManager(db_path=db_path)
    yield manager

    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass


def test_generate_and_validate_key(temp_key_manager):
    """Test generating a personal API key and validating it."""
    result = temp_key_manager.generate_key(client_name="Test Dev", email="dev@example.com")
    
    assert "api_key" in result
    assert result["api_key"].startswith("soul_live_")
    assert result["client_name"] == "Test Dev"
    assert result["tier"] == "free"

    # Validation should succeed
    api_key = result["api_key"]
    assert temp_key_manager.validate_key(api_key) is True

    # Invalid key should fail
    assert temp_key_manager.validate_key("soul_live_invalidkey123") is False
    assert temp_key_manager.validate_key("") is False


def test_record_usage_and_key_info(temp_key_manager):
    """Test request counter increments properly."""
    result = temp_key_manager.generate_key(client_name="Analytics Bot")
    api_key = result["api_key"]

    info_initial = temp_key_manager.get_key_info(api_key)
    assert info_initial is not None
    assert info_initial["request_count"] == 0

    temp_key_manager.record_usage(api_key)
    temp_key_manager.record_usage(api_key)

    info_after = temp_key_manager.get_key_info(api_key)
    assert info_after["request_count"] == 2


def test_api_generate_endpoint():
    """Test POST /v1/auth/keys/generate via TestClient."""
    client = TestClient(app)
    response = client.post(
        "/v1/auth/keys/generate",
        json={"client_name": "Autonomous Agent", "email": "agent@acme.inc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "api_key" in data
    assert data["api_key"].startswith("soul_live_")
    assert data["client_name"] == "Autonomous Agent"
    assert data["tier"] == "free"
    assert "rate_limit" in data

    # Verify that key info endpoint works with the new key
    api_key = data["api_key"]
    info_res = client.get("/v1/auth/keys/info", headers={"Authorization": f"Bearer {api_key}"})
    assert info_res.status_code == 200
    info_data = info_res.json()
    assert info_data["status"] == "active"
    assert info_data["client"]["client_name"] == "Autonomous Agent"


def test_api_key_usage_tracking_on_appraise():
    """Test that appraise endpoint increments request counter when bearer key provided."""
    client = TestClient(app)
    # Generate key
    gen_res = client.post("/v1/auth/keys/generate", json={"client_name": "Tracker Test"})
    api_key = gen_res.json()["api_key"]

    # Call /v1/appraise with bearer token
    res = client.post(
        "/v1/appraise",
        json={"text": "I am so overwhelmed by work and life right now."},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert res.status_code == 200

    # Verify request_count incremented
    info_res = client.get("/v1/auth/keys/info", headers={"Authorization": f"Bearer {api_key}"})
    assert info_res.status_code == 200
    # At least 1 request from appraise (plus get_key_info validation if recorded)
    assert info_res.json()["client"]["request_count"] >= 1
