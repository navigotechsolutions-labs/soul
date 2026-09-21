"""Tests for Adversity & Cognitive Stress Appraisal (Lazarus, Stoltz CORE, Scherer CPM)."""

import pytest
from soul import appraise
from soul.schemas.adversity import AdversityDomain, AppraisalStance
from soul.schemas.appraisal import ActionUrgency


def test_high_adversity_financial():
    text = "I lost my job yesterday and I can't afford rent. The debt collector is threatening eviction."
    res = appraise(text)
    
    assert res.adversity.adversity_score > 0.60
    assert res.adversity.primary_domain == AdversityDomain.FINANCIAL
    assert res.adversity.appraisal_stance in [AppraisalStance.THREAT, AppraisalStance.HARM_LOSS]
    assert res.agent_guidance.empathy_demand > 0.50
    # CORE Checks
    assert res.adversity.core.control < 0.50
    assert res.adversity.core.reach > 0.40
    # Conformal interval
    assert res.adversity.conformal_interval[0] <= res.adversity.adversity_score <= res.adversity.conformal_interval[1]


def test_adversity_interpersonal_grief():
    text = "My grandfather passed away this morning and my heart is completely shattered. The grief is unbearable."
    res = appraise(text)

    assert res.adversity.adversity_score > 0.60
    assert res.adversity.primary_domain == AdversityDomain.EXISTENTIAL_GRIEF
    assert res.adversity.appraisal_stance == AppraisalStance.HARM_LOSS
    assert res.adversity.cpm_checks.goal_conduciveness < -0.30
    assert any(f.feeling == "grief" for f in res.sentiment.top_feelings)


def test_challenge_stance_with_high_agency():
    text = "This project has severe roadblocks, but I will fight through it, plan every step, and overcome this challenge."
    res = appraise(text)

    assert res.adversity.appraisal_stance == AppraisalStance.CHALLENGE
    assert res.adversity.threat_vs_challenge_ratio > 0.0
    assert res.adversity.coping_agency > 0.55
    assert res.adversity.core.control > 0.50
    assert res.adversity.core.ownership > 0.50


def test_low_adversity_benign():
    text = "Just had a nice coffee with colleagues and finished reading an interesting book."
    res = appraise(text)

    assert res.adversity.adversity_score < 0.25
    assert res.adversity.appraisal_stance == AppraisalStance.BENIGN
    assert res.agent_guidance.urgency == ActionUrgency.LOW


def test_acute_crisis_detection():
    text = "I have no reason to live anymore and I want to end it all tonight."
    res = appraise(text)

    assert res.adversity.acute_crisis_flag is True
    assert res.agent_guidance.urgency == ActionUrgency.CRITICAL_EMERGENCY
    assert res.adversity.cpm_checks.action_urgency > 0.70
    assert "emergency_hotline_intervention" in res.agent_guidance.action_triggers
