"""Unit tests for the autonomous continuous testing & fuzzing engine."""

import pytest
from soul.engine.autonomous_tester import (
    AdversarialFuzzer,
    AutonomousScenarioGenerator,
    AutonomousStressRunner,
)
from soul.schemas.adversity import AdversityDomain


def test_adversarial_fuzzer_perturb():
    text = "I am deeply stressed about my rent and eviction notice"
    perturbed = AdversarialFuzzer.perturb(text, noise_level=0.3)
    assert perturbed != text
    assert len(perturbed) > 0


def test_adversarial_fuzzer_edge_cases():
    cases = AdversarialFuzzer.generate_extreme_edge_cases()
    assert len(cases) >= 15
    names = [c[0] for c in cases]
    assert "empty_string" in names
    assert "massive_repetition" in names
    assert "emoji_monologue" in names


def test_autonomous_scenario_generator():
    for _ in range(30):
        prompt, domain = AutonomousScenarioGenerator.sample_scenario(apply_fuzzing=False)
        assert len(prompt) > 0
        assert isinstance(domain, AdversityDomain)


def test_autonomous_stress_battery_100_runs():
    runner = AutonomousStressRunner()
    report = runner.run_stress_battery(num_iterations=100)

    # Statistical & Reliability Assertions
    assert report.total_iterations == 100
    assert report.crash_count == 0, f"Crashes detected: {report.errors}"
    assert report.successful_runs == 100
    assert report.avg_latency_ms < 5.0, f"Average latency too high: {report.avg_latency_ms}ms"
    assert report.conformal_coverage_rate >= 80.0, f"Coverage low: {report.conformal_coverage_rate}%"
    assert len(report.domain_breakdown) >= 10
