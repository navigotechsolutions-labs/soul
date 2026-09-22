"""Unit tests for Soul Anti-AI-Slop & Human Experience Sensation Suite."""

import pytest
from soul import (
    audit_human_feel,
    audit_slop,
    sanitize_slop,
    audit_aesthetics,
    SlopAuditor,
    AestheticAuditor,
    HumanFeelAuditor,
)


def test_slop_detector_identifies_emojis():
    """Verifies that emoji-as-icon abuse is caught and flagged."""
    slop_text = "🚀 Launch your career! ✨ Get smart tips! 💡 Discover insights!"
    res = audit_slop(slop_text)

    assert res.slop_detected is True
    assert res.emoji_icon_count >= 3
    assert "🚀" in res.emojis_found
    assert res.human_authenticity_score < 70
    assert any("emoji" in crit.lower() for crit in res.criticisms)


def test_slop_detector_identifies_em_dashes_and_buzzwords():
    """Verifies that em-dash saturation and AI cliché words are detected."""
    ai_text = "In today's fast-paced world—efficiency is crucial—and our platform will delve into your needs to foster success."
    res = audit_slop(ai_text)

    assert res.slop_detected is True
    assert res.em_dash_count >= 2
    assert "delve" in res.ai_cliches_found
    assert "crucial" in res.ai_cliches_found
    assert "foster" in res.ai_cliches_found
    assert res.human_authenticity_score < 60


def test_slop_sanitization():
    """Verifies that AI slop is cleansed into grounded human phrasing."""
    ai_text = "In today's fast-paced digital landscape—our tool will delve into your workflow 🚀 and unleash your potential."
    sanitized = sanitize_slop(ai_text)

    assert "delve" not in sanitized.lower()
    assert "🚀" not in sanitized
    assert "—" not in sanitized
    assert "today" in sanitized.lower() or "explore" in sanitized.lower()


def test_aesthetic_auditor_detects_ai_purple():
    """Verifies detection of generic ChatGPT / V0 purple gradient and radioactive neons."""
    css_sample = "bg-[#0b0f19] border-[#7c3aed] text-[#00ff66] from-purple-600 to-indigo-600"
    res = audit_aesthetics(css_sample)

    assert res.has_generic_ai_purple is True
    assert res.has_radioactive_neons is True
    assert res.aesthetic_health_score < 60
    assert len(res.criticisms) >= 2
    assert "Obsidian" in res.recommended_palette["name"]


def test_human_feel_report_full_audit():
    """Verifies end-to-end human presence scorecard and cognitive friction scoring."""
    slop_input = (
        "In today's fast-paced digital landscape—efficiency is paramount. 🚀\n"
        "Delve into our multifaceted ecosystem to harness your synergy.\n"
        "- Step 1: Optimize your profile.\n"
        "- Step 2: Implement micro-actions.\n"
        "- Step 3: Unleash your performance.\n"
        "- Step 4: Scale indefinitely."
    )
    report = audit_human_feel(slop_input)

    assert report.status in ("STERILE_ROBOTIC", "CRITICAL_AI_SLOP")
    assert report.overall_human_score < 70
    assert report.cognitive_friction_score > 0.3
    assert len(report.key_criticisms) > 0
    assert len(report.actionable_prescriptions) > 0
    assert report.humanized_alternative is not None


def test_authentic_human_text_passes():
    """Verifies that genuine, well-written human text receives a high authentic score."""
    human_text = (
        "We built this tool because we got tired of software that felt cold and complicated. "
        "It focuses on one simple thing: helping you finish your work so you can go home on time."
    )
    report = audit_human_feel(human_text)

    assert report.overall_human_score >= 80
    assert report.status == "AUTHENTIC_HUMAN_CRAFT"
    assert report.slop_audit.emoji_icon_count == 0
    assert len(report.slop_audit.ai_cliches_found) == 0


def test_server_endpoints():
    """Verifies the REST API endpoints for human audit and slop sanitization."""
    from fastapi.testclient import TestClient
    from soul.server import app

    client = TestClient(app)

    # Test audit endpoint
    audit_resp = client.post(
        "/v1/audit/human-pov",
        json={"content": "In today's fast-paced world—delve into our platform! 🚀"}
    )
    assert audit_resp.status_code == 200
    data = audit_resp.json()
    assert "overall_human_score" in data
    assert "status" in data
    assert "slop_audit" in data

    # Test sanitize endpoint
    san_resp = client.post(
        "/v1/sanitize/anti-slop",
        json={"text": "Delve into this game-changer! 🚀"}
    )
    assert san_resp.status_code == 200
    san_data = san_resp.json()
    assert "sanitized" in san_data
    assert "🚀" not in san_data["sanitized"]
