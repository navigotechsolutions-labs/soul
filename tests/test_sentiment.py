"""Tests for Affect, VAD Coordinates, GoEmotions, and Nuanced Feelings."""

import pytest
from soul import appraise
from soul.schemas.sentiment import SentimentPolarity


def test_positive_affect():
    text = "I am so happy and delighted with this amazing progress! Feeling blessed and energized."
    res = appraise(text)

    assert res.sentiment.vad.valence > 0.4
    assert res.sentiment.polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]
    assert res.sentiment.emotions.joy > 0.2
    assert res.sentiment.go_emotions.joy > 0.1
    # Conformal interval
    assert res.sentiment.conformal_valence_interval[0] <= res.sentiment.vad.valence <= res.sentiment.conformal_valence_interval[1]


def test_go_emotions_gratitude():
    text = "Thank you so much for your incredible help, I truly appreciate everything you did."
    res = appraise(text)

    assert res.sentiment.go_emotions.gratitude > 0.15


def test_negative_distress_vad():
    text = "I feel terrified and anxious, everything is falling apart and I'm panicked."
    res = appraise(text)

    assert res.sentiment.vad.valence < -0.3
    assert res.sentiment.vad.arousal > 0.5
    assert res.sentiment.vad.dominance < 0.4
    assert res.sentiment.emotions.fear > 0.2
    assert res.sentiment.go_emotions.fear > 0.1


def test_negation_handling():
    text_pos = "I feel happy today."
    text_neg = "I am not happy today."

    res_pos = appraise(text_pos)
    res_neg = appraise(text_neg)

    assert res_pos.sentiment.vad.valence > res_neg.sentiment.vad.valence
    assert res_neg.sentiment.vad.valence < 0.1


def test_nuanced_feeling_burnout():
    text = "I have zero energy left, completely exhausted and running on empty fumes from burnout."
    res = appraise(text)

    burnout_feelings = [f for f in res.sentiment.top_feelings if f.feeling == "burnout"]
    assert len(burnout_feelings) > 0
    assert burnout_feelings[0].intensity > 0.5


def test_nuanced_feeling_vulnerability():
    text = "Sharing this makes me feel so vulnerable, exposed, and emotionally raw."
    res = appraise(text)

    vuln = [f for f in res.sentiment.top_feelings if f.feeling == "vulnerability"]
    assert len(vuln) > 0
