"""Adapter for TypeSafe AI's Jev API (using typesafe-sdk).

Allows running queries through TypeSafe AI's hosted Jev System One model
when TYPESAFE_API_KEY is available, outputting into the standard Soul schema.
"""

import os
import time
from typing import Any

from soul.schemas.adversity import AdversityAssessment, AdversityDomain, AppraisalStance
from soul.schemas.appraisal import ActionUrgency, AgentGuidance, SubjectAppraisalResult
from soul.schemas.sentiment import (
    FeelingScore,
    PlutchikEmotions,
    SentimentAssessment,
    SentimentPolarity,
    VADVector,
)

try:
    from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
    TYPESAFE_SDK_AVAILABLE = True
except ImportError:
    TYPESAFE_SDK_AVAILABLE = False


class TypeSafeJevAdapter:
    """Invokes TypeSafe AI's Jev model via questions schema."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TYPESAFE_API_KEY")
        if not TYPESAFE_SDK_AVAILABLE:
            raise RuntimeError("typesafe-sdk is not installed. Install via `pip install typesafe-sdk`.")

    def appraise(self, state: str | dict[str, Any]) -> SubjectAppraisalResult:
        """Runs Jev System One schema-locked questions against state."""
        if not self.api_key:
            raise ValueError("TYPESAFE_API_KEY is not set. Please set the environment variable.")

        start_time = time.perf_counter()
        
        # Prepare typed questions for Jev
        questions = {
            "is_adversity": Noul(instructions="Is the subject experiencing hardship, stress, conflict, or adversity?"),
            "adversity_severity": Score(
                instructions="Rate the severity of the adversity or distress.",
                criteria={
                    "0": "No adversity or distress",
                    "1": "Mild daily friction",
                    "2": "Moderate stress or obstacle",
                    "3": "Severe crisis, trauma, or overwhelming difficulty"
                }
            ),
            "adversity_domain": Choice(
                instructions="What is the primary domain of adversity?",
                criteria={
                    "none": "No significant adversity",
                    "financial": "Financial hardship, bills, poverty",
                    "interpersonal": "Relationship conflict, divorce, loneliness, bullying",
                    "health_physical": "Illness, chronic pain, injury, medical issue",
                    "workplace_academic": "Job loss, burnout, workplace toxicity, school failure",
                    "existential_grief": "Death, mourning, loss of meaning",
                    "resource_constraint": "Lack of food, shelter, or basic necessities",
                    "safety_trauma": "Assault, abuse, physical danger, violence"
                }
            ),
            "stance": Choice(
                instructions="What is the cognitive stance of the subject?",
                criteria={
                    "benign": "No stress or threat",
                    "threat": "Impending threat or dread",
                    "harm_loss": "Damage or loss already occurred",
                    "challenge": "Active mobilization and challenge orientation"
                }
            ),
            "valence": Score(
                instructions="How pleasant or positive vs distressing or negative is the emotional state?",
                criteria={
                    "0": "Deeply distressed, miserable, or negative",
                    "1": "Mildly negative",
                    "2": "Neutral or mixed",
                    "3": "Positive, happy, or relieved"
                }
            ),
            "crisis_flag": Noul(instructions="Does this indicate acute crisis (e.g. self-harm, suicidal ideation, immediate danger)?")
        }

        with TypeSafeClient(api_key=self.api_key) as client:
            resp = client.system_one(state=state, questions=questions)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Parse responses
        is_adv_p = resp.nouls["is_adversity"].noul
        adv_score_raw = resp.scores["adversity_severity"].score / 3.0
        domain_str = resp.choices["adversity_domain"].choice
        stance_str = resp.choices["stance"].choice
        valence_raw = (resp.scores["valence"].score / 1.5) - 1.0  # map 0..3 to -1..1
        crisis = resp.nouls["crisis_flag"].noul > 0.65

        adversity = AdversityAssessment(
            adversity_score=round(float(adv_score_raw), 4),
            confidence=round(float(is_adv_p), 4),
            primary_domain=AdversityDomain(domain_str if domain_str in AdversityDomain.__members__.values() else "none"),
            appraisal_stance=AppraisalStance(stance_str if stance_str in AppraisalStance.__members__.values() else "benign"),
            threat_vs_challenge_ratio=-0.5 if stance_str == "threat" else (0.5 if stance_str == "challenge" else 0.0),
            coping_agency=0.6 if stance_str == "challenge" else 0.3,
            acute_crisis_flag=crisis,
            crisis_indicators=["jev_crisis_flag"] if crisis else []
        )

        vad = VADVector(valence=round(valence_raw, 4), arousal=0.6 if is_adv_p > 0.5 else 0.3, dominance=0.4)
        sentiment = SentimentAssessment(
            polarity=SentimentPolarity.NEGATIVE if valence_raw < -0.2 else (SentimentPolarity.POSITIVE if valence_raw > 0.2 else SentimentPolarity.NEUTRAL),
            sentiment_score=round(valence_raw, 4),
            confidence=0.88,
            vad=vad,
            emotions=PlutchikEmotions(),
            top_feelings=[FeelingScore(feeling="distress", intensity=adv_score_raw, confidence=0.85)] if adv_score_raw > 0.3 else []
        )

        guidance = AgentGuidance(
            empathy_demand=round(float(adv_score_raw * 0.8 + 0.2), 4) if is_adv_p > 0.5 else 0.1,
            urgency=ActionUrgency.CRITICAL_EMERGENCY if crisis else (ActionUrgency.HIGH if adv_score_raw > 0.7 else ActionUrgency.LOW),
            recommended_tone="empathetic_calm" if is_adv_p > 0.5 else "neutral_helpful",
            de_escalation_needed=False,
            action_triggers=["typesafe_jev_pipeline"]
        )

        return SubjectAppraisalResult(
            text_length=len(str(state)),
            adversity=adversity,
            sentiment=sentiment,
            agent_guidance=guidance,
            execution_time_ms=round(elapsed_ms, 2),
            engine_backend="typesafe-jev-cloud"
        )
