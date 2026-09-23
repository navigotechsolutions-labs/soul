"""Unified Subject Cognitive & Emotional Appraisal Schema."""

from enum import Enum
from pydantic import BaseModel, Field

from soul.schemas.adversity import AdversityAssessment
from soul.schemas.sentiment import SentimentAssessment


class ActionUrgency(str, Enum):
    """Advisory urgency label; do not use alone for safety routing."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL_EMERGENCY = "critical_emergency"


class AgentGuidance(BaseModel):
    """Calibrated recommendations for AI agents interacting with this subject."""
    
    empathy_demand: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Calculated requirement for empathetic attunement vs purely technical/factual answers."
    )
    urgency: ActionUrgency = Field(
        default=ActionUrgency.LOW,
        description="Heuristic advisory urgency; not a validated triage or emergency determination."
    )
    recommended_tone: str = Field(
        ...,
        description="Prescribed communication tone for the agent (e.g., 'calm_validating', 'reassuring_empowering', 'neutral_direct')."
    )
    de_escalation_needed: bool = Field(
        default=False,
        description="Flag indicating high emotional arousal or anger requiring active de-escalation."
    )
    action_triggers: list[str] = Field(
        default_factory=list,
        description="Rules triggered (e.g., 'flag_for_human_supervisor', 'offer_grounding_exercise')."
    )


class SubjectAppraisalResult(BaseModel):
    """Jev-Style System 1 Schema-Locked Output for Subject Appraisal.
    
    Returns structured, non-generative, calibrated decisions:
    - Adversity Profile
    - Sentiment & Feelings
    - Agent Guidance & Empathy Demand
    - Performance Metadata
    """
    subject_id: str | None = Field(default=None, description="Optional subject/user identifier")
    text_length: int = Field(..., description="Character count of evaluated state")
    adversity: AdversityAssessment = Field(..., description="Cognitive stress and adversity assessment")
    sentiment: SentimentAssessment = Field(..., description="Continuous affect and nuanced feelings")
    agent_guidance: AgentGuidance = Field(..., description="Agent routing and empathy recommendations")
    execution_time_ms: float = Field(..., description="Latency in milliseconds (System 1 fast pass)")
    engine_backend: str = Field(default="soul-system-one-local", description="Backend engine that produced this result")
