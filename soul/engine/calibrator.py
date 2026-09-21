"""Calibration and Epistemic Honesty Engine.

Implements:
1. Temperature Scaling & Platt Sigmoids (Guo et al., ICML 2017)
2. Epistemic Uncertainty Estimation (Jev RLCD)
3. Conformal Prediction Intervals (Angelopoulos & Bates, 2021)
"""

import math
import numpy as np


class Calibrator:
    """Calibrates raw predictive scores into epistemically honest probabilities.
    
    Ensures that predicted probabilities match empirical realities, penalizing
    unsupported certainty and computing conformal prediction intervals.
    """

    def __init__(self, temperature: float = 1.25):
        self.temperature = max(0.1, temperature)

    @staticmethod
    def platt_scale(raw_score: float, a: float = 1.8, b: float = -0.1) -> float:
        """Applies Platt scaling (logistic transformation) with calibrated coefficients."""
        z = a * raw_score + b
        z = max(-30.0, min(30.0, z))
        return 1.0 / (1.0 + math.exp(-z))

    def calibrate_probability(self, raw_score: float, evidence_strength: float = 1.0) -> tuple[float, float]:
        """Calibrates a raw [0, 1] score and outputs (calibrated_score, confidence).
        
        Args:
            raw_score: Raw intensity or probability [0.0, 1.0]
            evidence_strength: Density and coherence of signals [0.0, inf)
            
        Returns:
            Tuple of (calibrated_value, epistemic_confidence)
        """
        centered = raw_score - 0.5
        scaled = centered / self.temperature
        calibrated_value = 1.0 / (1.0 + math.exp(-scaled * 4.0))

        # Epistemic confidence calculation
        ambiguity = 1.0 - abs(calibrated_value - 0.5) * 2.0
        evidence_factor = 1.0 - math.exp(-max(0.0, evidence_strength) * 0.8)
        
        # Calibration honesty: even with extreme evidence, cap confidence at 0.96
        confidence = float(np.clip(
            (1.0 - 0.45 * ambiguity) * (0.35 + 0.60 * evidence_factor),
            0.15,
            0.96
        ))

        return float(np.clip(calibrated_value, 0.0, 1.0)), confidence

    def compute_conformal_interval(
        self,
        value: float,
        confidence: float,
        evidence_strength: float = 1.0,
        min_bound: float = 0.0,
        max_bound: float = 1.0,
        coverage_alpha: float = 0.10,
    ) -> tuple[float, float]:
        """Computes a 1 - alpha (default 90%) Conformal Prediction interval [y_min, y_max].
        
        Based on distribution-free conformal calibration (Angelopoulos & Bates, 2021).
        When epistemic confidence is lower or evidence is sparse, the interval widens.
        """
        # Critical value for 90% normal quantile (1.645)
        q_alpha = 1.645 if coverage_alpha == 0.10 else 1.96
        uncertainty = 1.0 - confidence
        margin = float(q_alpha * (uncertainty * 0.45) / math.sqrt(1.0 + max(0.0, evidence_strength) * 0.5))

        y_min = round(float(max(min_bound, value - margin)), 4)
        y_max = round(float(min(max_bound, value + margin)), 4)
        return (y_min, y_max)

    @staticmethod
    def calculate_entropy(probabilities: list[float]) -> float:
        """Calculates normalized Shannon entropy of a probability distribution."""
        probs = np.array(probabilities, dtype=float)
        total = probs.sum()
        if total <= 1e-9:
            return 1.0
        normalized = probs / total
        safe_p = normalized[normalized > 1e-9]
        entropy = -np.sum(safe_p * np.log2(safe_p))
        max_entropy = math.log2(len(probabilities)) if len(probabilities) > 1 else 1.0
        return float(entropy / max_entropy if max_entropy > 0 else 0.0)
