"""Unit tests for the Soul Engine FastAPI REST API & OpenAI Proxy."""

import pytest
from fastapi.testclient import TestClient
from soul.server import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Soul Engine API"
    assert "endpoints" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_models_endpoint():
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    ids = [m["id"] for m in data["data"]]
    assert "soul-attuned" in ids
    assert "soul-appraiser" in ids


def test_appraise_endpoint():
    payload = {"text": "I was just laid off after 8 years and I'm in total shock."}
    response = client.post("/v1/appraise", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "adversity" in data
    assert "sentiment" in data
    assert "agent_guidance" in data
    assert data["adversity"]["primary_domain"] == "workplace_academic"
    assert data["agent_guidance"]["empathy_demand"] > 0.50


def test_harmonize_endpoint_with_user_message():
    payload = {
        "user_message": "Mama tummy hurty waaa boo-boo ouchie!",
        "draft_response": "Here are practical steps to move forward with this task:\n1. Step one\n2. Step two",
    }
    response = client.post("/v1/harmonize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["was_harmonized"] is True
    assert data["is_blunt"] is True
    assert "sweetheart" in data["harmonized_content"].lower() or "boo-boo" in data["harmonized_content"].lower()


def test_respond_endpoint():
    payload = {
        "message": "My mother passed away last night. Help me draft a short announcement.",
        "base_system_prompt": "You are a supportive assistant.",
    }
    response = client.post("/v1/respond", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "appraisal" in data
    assert data["was_harmonized"] is True
    assert data["warmth_score"] >= 0.50


def test_openai_chat_completions_proxy():
    payload = {
        "model": "soul-attuned",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "I was laid off with zero notice today and can't feed my family. What do I do?"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert len(data["choices"][0]["message"]["content"]) > 0
    assert "soul_meta" in data
    assert data["soul_meta"]["adversity_domain"] == "workplace_academic"
    assert data["soul_meta"]["was_harmonized"] is True


def test_harmonize_endpoint_without_user_message():
    """Verify user_message is optional in v0.4.0 and defaults to draft analysis."""
    payload = {
        "draft_response": "Here are practical steps to move forward with this task:\n1. Error audit\n2. Pomodoro",
    }
    response = client.post("/v1/harmonize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "harmonized_content" in data
    assert "warmth_score" in data


def test_openai_chat_completions_streaming():
    """Verify stream=True returns Server-Sent Events (SSE)."""
    payload = {
        "model": "soul-attuned",
        "stream": True,
        "messages": [
            {"role": "user", "content": "I am feeling stressed and need advice."}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    content = response.text
    assert "data: {" in content
    assert "data: [DONE]" in content


def test_anti_slop_endpoints():
    """Verify /v1/sanitize/anti-slop and /v1/anti-slop dedicated endpoints."""
    raw = "In today's fast-paced world—efficiency is crucial. 🚀 Delve into our tool!"
    
    # 1. /v1/sanitize/anti-slop with text field
    r1 = client.post("/v1/sanitize/anti-slop", json={"text": raw})
    assert r1.status_code == 200
    assert "sanitized" in r1.json()
    assert "delve" not in r1.json()["sanitized"].lower()

    # 2. /v1/anti-slop alias with content field
    r2 = client.post("/v1/anti-slop", json={"content": raw})
    assert r2.status_code == 200
    assert "sanitized" in r2.json()
    assert "delve" not in r2.json()["sanitized"].lower()


def test_seo_routes():
    """Verify /robots.txt and /sitemap.xml are served for search engines."""
    r_robots = client.get("/robots.txt")
    assert r_robots.status_code == 200
    assert "User-agent" in r_robots.text
    assert "sitemap.xml" in r_robots.text

    r_sitemap = client.get("/sitemap.xml")
    assert r_sitemap.status_code == 200
    assert "<urlset" in r_sitemap.text
    assert "https://soul.navigotechsolutions.com/" in r_sitemap.text

