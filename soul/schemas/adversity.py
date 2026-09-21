"""Schemas for Adversity and Cognitive Stress Appraisal (Lazarus, Scherer CPM, Stoltz CORE)."""

from enum import Enum
from pydantic import BaseModel, Field


class AdversityDomain(str, Enum):
    """Categorical domain of adversity or stressor."""
    NONE = "none"
    FINANCIAL = "financial"
    INTERPERSONAL = "interpersonal"
    HEALTH_PHYSICAL = "health_physical"
    WORKPLACE_ACADEMIC = "workplace_academic"
    EXISTENTIAL_GRIEF = "existential_grief"
    RESOURCE_CONSTRAINT = "resource_constraint"
    SAFETY_TRAUMA = "safety_trauma"
    LEGAL_JUDICIAL = "legal_judicial"
    ENVIRONMENTAL_DISASTER = "environmental_disaster"
    MORAL_ETHICAL = "moral_ethical"
    PHILOSOPHICAL_EXISTENTIAL = "philosophical_existential"
    ROMANTIC_ATTACHMENT = "romantic_attachment"
    DEVELOPMENTAL_INFANT = "developmental_infant"
    POLITICAL_CIVIC = "political_civic"
    NARRATIVE_LITERARY = "narrative_literary"


class AppraisalStance(str, Enum):
    """Lazarus & Folkman Cognitive Appraisal Stance.
    
    - THREAT: Anticipation of impending harm or loss with high perceived vulnerability.
    - HARM_LOSS: Damage has already occurred (grief, acute defeat).
    - CHALLENGE: Demanding obstacle viewed with mobilization, growth, or coping potential.
    - BENIGN: Neutral or non-stressful situation.
    """
    BENIGN = "benign"
    THREAT = "threat"
    HARM_LOSS = "harm_loss"
    CHALLENGE = "challenge"


class COREDimensions(BaseModel):
    """Dr. Paul Stoltz's CORE Model of Adversity Quotient (AQ).
    
    - Control: Perceived influence over the difficulty (0.0=helpless, 1.0=high influence).
    - Ownership: Accountability and readiness to act regardless of origin (0.0=deflection, 1.0=full agency).
    - Reach: Perceived fallout across other life domains (0.0=strictly compartmentalized, 1.0=catastrophized).
    - Endurance: Perceived permanence/duration of the problem (0.0=transient, 1.0=interminable/permanent).
    """
    control: float = Field(..., ge=0.0, le=1.0, description="Perceived influence over the situation")
    ownership: float = Field(..., ge=0.0, le=1.0, description="Accountability and readiness to act")
    reach: float = Field(..., ge=0.0, le=1.0, description="Catastrophizing vs Compartmentalizing")
    endurance: float = Field(..., ge=0.0, le=1.0, description="Perceived permanence vs transience")


class SchererAppraisalChecks(BaseModel):
    """Klaus Scherer's Component Process Model (CPM) Stimulus Evaluation Checks.
    
    - Goal Conduciveness: Facilitation (+1.0) vs Obstruction (-1.0) of core goals.
    - Coping Potential: Perceived capacity to adjust or master the obstacle (0.0 to 1.0).
    - Action Urgency: Demands immediate cognitive or behavioral mobilization (0.0 to 1.0).
    """
    goal_conduciveness: float = Field(..., ge=-1.0, le=1.0, description="Goal facilitation (+1) vs obstruction (-1)")
    coping_potential: float = Field(..., ge=0.0, le=1.0, description="Capacity to master or adapt to the event")
    action_urgency: float = Field(..., ge=0.0, le=1.0, description="Urgency of behavioral mobilization")


class AdversityAssessment(BaseModel):
    """Calibrated adversity and cognitive stress evaluation."""
    
    adversity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Calibrated adversity intensity from 0.0 (no adversity) to 1.0 (catastrophic stress)."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Epistemic confidence score reflecting calibration honesty."
    )
    conformal_interval: tuple[float, float] = Field(
        ...,
        description="90% Conformal Prediction uncertainty interval [y_min, y_max]."
    )
    primary_domain: AdversityDomain = Field(
        default=AdversityDomain.NONE,
        description="Dominant domain of the adversity."
    )
    appraisal_stance: AppraisalStance = Field(
        default=AppraisalStance.BENIGN,
        description="Cognitive stance: threat, harm_loss, challenge, or benign."
    )
    threat_vs_challenge_ratio: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="-1.0 indicates total threat/helplessness, +1.0 indicates strong challenge/resilience mobilization."
    )
    coping_agency: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Perceived subject control & self-efficacy: 0.0 (hopeless/paralyzed) to 1.0 (empowered/taking action)."
    )
    core: COREDimensions = Field(
        ...,
        description="Stoltz's CORE Adversity Quotient dimensions (Control, Ownership, Reach, Endurance)."
    )
    cpm_checks: SchererAppraisalChecks = Field(
        ...,
        description="Scherer's Component Process Model Stimulus Evaluation Checks."
    )
    acute_crisis_flag: bool = Field(
        default=False,
        description="Emergency flag for acute crisis (suicidal ideation, severe panic, imminent self-harm, trauma)."
    )
    crisis_indicators: list[str] = Field(
        default_factory=list,
        description="Specific triggers or phrases that contributed to crisis flags."
    )
