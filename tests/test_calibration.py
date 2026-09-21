"""Tests for Epistemic Calibration and Conformal Prediction Intervals."""

import pytest
from soul.engine.calibrator import Calibrator


def test_calibration_bounds():
    cal = Calibrator()

    for raw in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        val, conf = cal.calibrate_probability(raw, evidence_strength=1.0)
        assert 0.0 <= val <= 1.0
        assert 0.10 <= conf <= 0.96


def test_conformal_interval_bracketing():
    cal = Calibrator()

    val, conf = cal.calibrate_probability(0.75, evidence_strength=2.0)
    low, high = cal.compute_conformal_interval(val, conf, evidence_strength=2.0)

    assert low <= val <= high
    assert 0.0 <= low <= 1.0
    assert 0.0 <= high <= 1.0
    assert high - low > 0.0


def test_ambiguity_penalizes_confidence():
    cal = Calibrator()

    _, conf_ambiguous = cal.calibrate_probability(0.5, evidence_strength=1.0)
    _, conf_clear = cal.calibrate_probability(0.95, evidence_strength=1.0)

    assert conf_clear > conf_ambiguous


def test_entropy_computation():
    cal = Calibrator()

    uniform_entropy = cal.calculate_entropy([0.25, 0.25, 0.25, 0.25])
    assert pytest.approx(uniform_entropy, 0.01) == 1.0

    skewed_entropy = cal.calculate_entropy([0.95, 0.02, 0.02, 0.01])
    assert skewed_entropy < uniform_entropy
