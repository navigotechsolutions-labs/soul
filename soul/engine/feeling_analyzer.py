"""Affective Sentiment and Nuanced Feeling Appraisal Engine.

Extracts:
1. 3D Continuous Affect (Valence, Arousal, Dominance - VAD) with Conformal Bounds
2. Plutchik Basic Emotion Probabilities
3. Google Research 27 GoEmotions Distribution (Demszky et al., ACL 2020)
4. Nuanced Psychological Feeling States (Vulnerability, Burnout, Grief, Hope, etc.)
5. Calibrated Sentiment Polarity
"""

import math
import re
import numpy as np

from soul.engine.affect_lexicon import (
    INTENSIFIERS,
    NEGATIONS,
    NUANCED_FEELINGS_SEEDS,
    PLUTCHIK_SEEDS,
    VAD_LEXICON,
)
from soul.engine.calibrator import Calibrator
from soul.engine.go_emotions import GoEmotionsAnalyzer
from soul.schemas.sentiment import (
    FeelingScore,
    GoEmotionsDistribution,
    PlutchikEmotions,
    SentimentAssessment,
    SentimentPolarity,
    VADVector,
)


class FeelingAnalyzer:
    """Evaluates emotional sentiment, VAD coordinates, GoEmotions, and granular feelings."""

    def __init__(self, calibrator: Calibrator | None = None):
        self.calibrator = calibrator or Calibrator()
        self.go_emotions_analyzer = GoEmotionsAnalyzer()

    def analyze(self, text: str) -> SentimentAssessment:
        """Appraises text for sentiment, VAD coordinates, GoEmotions, and nuanced feelings."""
        clean_text = text.lower()
        tokens = re.findall(r"\b\w+(?:'\w+)?\b", clean_text)
        
        # 1. Continuous Affect Calculation (VAD)
        valences: list[float] = []
        arousals: list[float] = []
        dominances: list[float] = []
        evidence_count = 0

        for i, token in enumerate(tokens):
            if token in VAD_LEXICON:
                v, a, d = VAD_LEXICON[token]
                evidence_count += 1

                # Check preceding 2 tokens for negations and intensifiers
                negated = False
                intensity_mult = 1.0

                start_idx = max(0, i - 2)
                for prev in tokens[start_idx:i]:
                    if prev in NEGATIONS:
                        negated = True
                    if prev in INTENSIFIERS:
                        intensity_mult *= INTENSIFIERS[prev]

                if negated:
                    v = -v * 0.75
                    a = min(1.0, a * 0.9)
                    d = max(0.0, 1.0 - d)

                v = max(-1.0, min(1.0, v * intensity_mult))
                a = max(0.0, min(1.0, a * intensity_mult))
                d = max(0.0, min(1.0, d * intensity_mult))

                valences.append(v)
                arousals.append(a)
                dominances.append(d)

        # Baseline coordinates if no lexicon tokens hit
        if not valences:
            avg_valence = 0.0
            avg_arousal = 0.30
            avg_dominance = 0.50
        else:
            avg_valence = float(np.mean(valences))
            avg_arousal = float(np.mean(arousals))
            avg_dominance = float(np.mean(dominances))

        vad = VADVector(
            valence=round(avg_valence, 4),
            arousal=round(avg_arousal, 4),
            dominance=round(avg_dominance, 4),
        )

        # 2. Plutchik Basic Emotions Vector
        raw_emotions: dict[str, float] = {}
        for emotion, seeds in PLUTCHIK_SEEDS.items():
            score = 0.0
            for seed in seeds:
                if seed in clean_text:
                    score += 1.0
            raw_emotions[emotion] = score

        if avg_valence > 0.3 and avg_arousal > 0.4:
            raw_emotions["joy"] += avg_valence * 1.5
        if avg_valence < -0.3 and avg_arousal > 0.6:
            raw_emotions["fear"] += abs(avg_valence) * 1.2
            raw_emotions["anger"] += abs(avg_valence) * (avg_dominance * 1.5)
        if avg_valence < -0.2 and avg_arousal < 0.5:
            raw_emotions["sadness"] += abs(avg_valence) * 1.5
        if avg_dominance > 0.6 and avg_valence > 0.2:
            raw_emotions["trust"] += avg_dominance

        emotion_vals = list(raw_emotions.values())
        max_val = max(emotion_vals) if emotion_vals else 0.0
        
        plutchik_probs: dict[str, float] = {}
        if max_val > 0:
            exp_scores = {k: math.exp(v / 1.5) for k, v in raw_emotions.items()}
            sum_exp = sum(exp_scores.values())
            for k in raw_emotions:
                p = (exp_scores[k] / sum_exp) if sum_exp > 0 else 0.0
                plutchik_probs[k] = round(min(1.0, max(0.0, p * min(1.0, max_val * 0.8))), 4)
        else:
            for k in raw_emotions:
                plutchik_probs[k] = 0.0

        plutchik = PlutchikEmotions(
            joy=plutchik_probs.get("joy", 0.0),
            trust=plutchik_probs.get("trust", 0.0),
            fear=plutchik_probs.get("fear", 0.0),
            surprise=plutchik_probs.get("surprise", 0.0),
            sadness=plutchik_probs.get("sadness", 0.0),
            disgust=plutchik_probs.get("disgust", 0.0),
            anger=plutchik_probs.get("anger", 0.0),
            anticipation=plutchik_probs.get("anticipation", 0.0),
        )

        # 3. Google Research 27 GoEmotions Distribution
        go_emotions = self.go_emotions_analyzer.analyze(
            text=text,
            valence=avg_valence,
            arousal=avg_arousal
        )

        # 4. Granular Nuanced Feelings
        feeling_scores: list[FeelingScore] = []
        for feeling, seeds in NUANCED_FEELINGS_SEEDS.items():
            matches = sum(1 for s in seeds if s in clean_text)
            if matches > 0:
                raw_intensity = min(1.0, 0.4 + matches * 0.3)
                calibrated_intensity, conf = self.calibrator.calibrate_probability(
                    raw_intensity,
                    evidence_strength=matches * 1.5
                )
                feeling_scores.append(FeelingScore(
                    feeling=feeling,
                    intensity=round(calibrated_intensity, 4),
                    confidence=round(conf, 4),
                ))

        if not feeling_scores:
            if avg_valence < -0.5 and avg_dominance < 0.25 and avg_arousal > 0.4:
                intensity, conf = self.calibrator.calibrate_probability(0.65, evidence_strength=1.0)
                feeling_scores.append(FeelingScore(feeling="vulnerability", intensity=intensity, confidence=conf))
            elif avg_valence < -0.4 and avg_arousal < 0.3:
                intensity, conf = self.calibrator.calibrate_probability(0.60, evidence_strength=1.0)
                feeling_scores.append(FeelingScore(feeling="burnout", intensity=intensity, confidence=conf))
            elif avg_valence > 0.5:
                intensity, conf = self.calibrator.calibrate_probability(0.70, evidence_strength=1.0)
                feeling_scores.append(FeelingScore(feeling="contentment", intensity=intensity, confidence=conf))

        feeling_scores.sort(key=lambda x: x.intensity, reverse=True)

        # 5. Sentiment Polarity Bucket
        if avg_valence <= -0.55:
            polarity = SentimentPolarity.VERY_NEGATIVE
        elif avg_valence <= -0.15:
            polarity = SentimentPolarity.NEGATIVE
        elif avg_valence <= 0.15:
            polarity = SentimentPolarity.NEUTRAL
        elif avg_valence <= 0.55:
            polarity = SentimentPolarity.POSITIVE
        else:
            polarity = SentimentPolarity.VERY_POSITIVE

        # Calibration and Conformal Bounds for Valence
        _, sentiment_confidence = self.calibrator.calibrate_probability(
            raw_score=abs(avg_valence),
            evidence_strength=evidence_count * 1.2
        )
        conformal_valence = self.calibrator.compute_conformal_interval(
            value=avg_valence,
            confidence=sentiment_confidence,
            evidence_strength=evidence_count * 1.2,
            min_bound=-1.0,
            max_bound=1.0,
        )

        return SentimentAssessment(
            polarity=polarity,
            sentiment_score=round(avg_valence, 4),
            confidence=round(sentiment_confidence, 4),
            conformal_valence_interval=conformal_valence,
            vad=vad,
            emotions=plutchik,
            go_emotions=go_emotions,
            top_feelings=feeling_scores[:5],
        )
