"""Master System 1 Appraisal Engine for Soul.

Coordinates Adversity, Affect/VAD, and Agent Guidance in a fast,
calibrated, schema-locked execution pass (<50ms).
"""

import time
from typing import Any

from soul.engine.adversity_analyzer import AdversityAnalyzer
from soul.engine.calibrator import Calibrator
from soul.engine.feeling_analyzer import FeelingAnalyzer
from soul.schemas.adversity import (
    AdversityAssessment,
    AdversityDomain,
    AppraisalStance,
)
from soul.schemas.appraisal import (
    ActionUrgency,
    AgentGuidance,
    SubjectAppraisalResult,
)
from soul.schemas.sentiment import SentimentAssessment


class SoulAppraiser:
    """Jev-Style System 1 Fast Decision & Affective Appraisal Engine."""

    def __init__(self, temperature: float = 1.25):
        self.calibrator = Calibrator(temperature=temperature)
        self.feeling_analyzer = FeelingAnalyzer(calibrator=self.calibrator)
        self.adversity_analyzer = AdversityAnalyzer(calibrator=self.calibrator)

    def appraise(
        self,
        state: str | dict[str, Any],
        subject_id: str | None = None
    ) -> SubjectAppraisalResult:
        """Appraises the subject's input state for adversity, sentiment, and feelings.
        
        Args:
            state: Text string or structured dictionary containing user message/state.
            subject_id: Optional ID of the subject being evaluated.
            
        Returns:
            SubjectAppraisalResult with strictly typed, calibrated decisions.
        """
        start_time = time.perf_counter()

        # Extract text from state
        if isinstance(state, dict):
            # Support multiple common keys: "message", "text", "content", "body"
            text = (
                state.get("message")
                or state.get("text")
                or state.get("content")
                or state.get("body")
                or str(state)
            )
        else:
            text = str(state)

        # 1. Step: Affect & Nuanced Feeling Appraisal
        sentiment: SentimentAssessment = self.feeling_analyzer.analyze(text)

        # 2. Step: Adversity & Cognitive Coping Appraisal
        adversity: AdversityAssessment = self.adversity_analyzer.analyze(
            text=text,
            valence=sentiment.vad.valence,
            dominance=sentiment.vad.dominance
        )

        # 3. Step: Synthesize Agent Guidance & Triage
        guidance = self._synthesize_guidance(adversity, sentiment)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return SubjectAppraisalResult(
            subject_id=subject_id,
            text_length=len(text),
            adversity=adversity,
            sentiment=sentiment,
            agent_guidance=guidance,
            execution_time_ms=round(elapsed_ms, 2),
            engine_backend="soul-system-one-local",
        )

    def _synthesize_guidance(
        self,
        adversity: AdversityAssessment,
        sentiment: SentimentAssessment
    ) -> AgentGuidance:
        """Synthesizes actionable recommendations and empathy demand for downstream AI agents."""
        # Calculate Empathy Demand [0.0 - 1.0]
        # High adversity + negative valence + vulnerable feeling = high empathy demand
        feelings_set = {f.feeling for f in sentiment.top_feelings}
        vulnerable_factor = 0.25 if any(f in feelings_set for f in [
            "vulnerability", "grief", "loneliness", "burnout", "infant_distress", "disaster_terror", "moral_remorse"
        ]) else 0.0
        
        domain_factor = 0.15 if adversity.primary_domain in [
            AdversityDomain.DEVELOPMENTAL_INFANT,
            AdversityDomain.ENVIRONMENTAL_DISASTER,
            AdversityDomain.MORAL_ETHICAL,
        ] else 0.0

        raw_empathy = (
            adversity.adversity_score * 0.45
            + (max(0.0, -sentiment.vad.valence) * 0.35)
            + vulnerable_factor
            + domain_factor
        )
        empathy_demand = float(min(1.0, max(0.0, raw_empathy)))

        # Determine Urgency
        action_triggers: list[str] = []
        if adversity.acute_crisis_flag:
            urgency = ActionUrgency.CRITICAL_EMERGENCY
            action_triggers.append("emergency_hotline_intervention")
            action_triggers.append("pause_automated_agent_triage")
        elif adversity.adversity_score > 0.75:
            urgency = ActionUrgency.HIGH
            action_triggers.append("prioritize_empathetic_validation")
            action_triggers.append("route_to_human_or_senior_agent")
        elif adversity.adversity_score > 0.40 or sentiment.vad.arousal > 0.70:
            urgency = ActionUrgency.MODERATE
            action_triggers.append("acknowledge_emotional_strain")
        else:
            urgency = ActionUrgency.LOW

        # Check for de-escalation needs (High Anger, Hostility, or Aggression)
        de_escalation_needed = (
            sentiment.emotions.anger > 0.25
            or sentiment.go_emotions.anger > 0.15
            or sentiment.go_emotions.annoyance > 0.25
        )
        if de_escalation_needed:
            action_triggers.append("apply_de_escalation_protocol")

        # Determine Tone
        if adversity.acute_crisis_flag:
            recommended_tone = "gentle_grounding_supportive"
        elif de_escalation_needed:
            recommended_tone = "calm_validating_unreactive"
        elif adversity.primary_domain == AdversityDomain.DEVELOPMENTAL_INFANT:
            recommended_tone = "gentle_soothing_caregiver"
        elif adversity.primary_domain == AdversityDomain.ROMANTIC_ATTACHMENT:
            recommended_tone = "tender_poetic_resonant"
        elif adversity.primary_domain == AdversityDomain.ENVIRONMENTAL_DISASTER:
            recommended_tone = "urgent_calm_protective"
        elif adversity.primary_domain == AdversityDomain.LEGAL_JUDICIAL:
            recommended_tone = "solemn_respectful_composed"
        elif adversity.primary_domain == AdversityDomain.MORAL_ETHICAL:
            recommended_tone = "compassionate_nonjudgmental_clear"
        elif adversity.primary_domain == AdversityDomain.PHILOSOPHICAL_EXISTENTIAL:
            recommended_tone = "contemplative_reverent_honoring"
        elif adversity.primary_domain == AdversityDomain.POLITICAL_CIVIC:
            recommended_tone = "rigorous_principled_balanced"
        elif adversity.primary_domain == AdversityDomain.NARRATIVE_LITERARY:
            recommended_tone = "dramatic_resonant_attuned"
        elif empathy_demand > 0.48 or (adversity.primary_domain in [
            AdversityDomain.EXISTENTIAL_GRIEF,
            AdversityDomain.INTERPERSONAL,
            AdversityDomain.WORKPLACE_ACADEMIC,
            AdversityDomain.HEALTH_PHYSICAL
        ] and adversity.adversity_score > 0.35):
            recommended_tone = "warm_validating_empathetic"
        elif adversity.appraisal_stance == AppraisalStance.CHALLENGE:
            recommended_tone = "encouraging_collaborative"
        elif sentiment.vad.valence > 0.3:
            recommended_tone = "positive_engaged"
        else:
            recommended_tone = "neutral_helpful"

        return AgentGuidance(
            empathy_demand=round(empathy_demand, 4),
            urgency=urgency,
            recommended_tone=recommended_tone,
            de_escalation_needed=de_escalation_needed,
            action_triggers=action_triggers,
        )
