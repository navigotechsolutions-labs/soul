"""Tests for Bluntness Auditor, Response Harmonizer, and AttunedAgent."""

import pytest
from soul import appraise, respond
from soul.agent.attuned_agent import AttunedAgent
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer


def test_blunt_response_detected():
    auditor = BluntnessAuditor()
    user_msg = "I just failed my certification exam for the third time and I feel completely stupid and hopeless."
    appraisal = appraise(user_msg)

    # Completely cold, clinical AI output
    cold_ai_output = "Here are the 4 steps to pass your exam: 1. Read syllabus. 2. Practice questions. 3. Study 2 hours daily."
    
    audit = auditor.audit(cold_ai_output, appraisal)
    assert audit["is_blunt"] is True
    assert audit["warmth_score"] < 0.20
    assert audit["validation_present"] is False


def test_harmonizer_transforms_blunt_response():
    harmonizer = ResponseHarmonizer()
    user_msg = "I lost my job yesterday and can't afford rent. What should I do first?"
    appraisal = appraise(user_msg)

    cold_ai_output = "1. File for unemployment. 2. Call landlord. 3. Cut streaming subscriptions."
    
    harmonized, was_altered = harmonizer.harmonize(cold_ai_output, appraisal)
    assert was_altered is True
    # The harmonized output must acknowledge the emotional weight
    assert any(term in harmonized.lower() for term in ["financial stress", "incredibly heavy", "anxiety", "bills"])
    # The original advice is preserved
    assert "File for unemployment" in harmonized


def test_attuned_agent_end_to_end():
    agent = AttunedAgent()
    user_msg = "I'm experiencing severe burnout and impostor syndrome at work, feeling like a fraud."
    
    response = agent.respond(user_msg)
    
    assert response.warmth_score > 0.30
    assert "burnout" in response.content.lower() or "overwhelm" in response.content.lower() or "grace" in response.content.lower()
    assert response.appraisal.adversity.adversity_score > 0.40
