"""Schemas for Continuous Affect (VAD), Discrete Emotions, and 27 GoEmotions."""

from enum import Enum
from pydantic import BaseModel, Field


class SentimentPolarity(str, Enum):
    """Categorical sentiment polarity."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class VADVector(BaseModel):
    """Russell's Circumplex Affect Model: 3D Continuous Affect Space.
    
    - Valence: How positive/pleasant vs negative/distressed the feeling is (-1.0 to +1.0)
    - Arousal: Energy/physiological activation level (0.0=calm/sleepy, 1.0=hyper-aroused/panic/euphoria)
    - Dominance: Perceived sense of power and agency (0.0=submissive/powerless, 1.0=in control)
    """
    valence: float = Field(..., ge=-1.0, le=1.0, description="Pleasure vs Displeasure")
    arousal: float = Field(..., ge=0.0, le=1.0, description="Activation / Excitement vs Deactivation / Calm")
    dominance: float = Field(..., ge=0.0, le=1.0, description="Control vs Powerlessness / Overwhelmed")


class PlutchikEmotions(BaseModel):
    """Primary emotional vectors based on Robert Plutchik's Wheel of Emotions (0.0 - 1.0)."""
    joy: float = Field(default=0.0, ge=0.0, le=1.0)
    trust: float = Field(default=0.0, ge=0.0, le=1.0)
    fear: float = Field(default=0.0, ge=0.0, le=1.0)
    surprise: float = Field(default=0.0, ge=0.0, le=1.0)
    sadness: float = Field(default=0.0, ge=0.0, le=1.0)
    disgust: float = Field(default=0.0, ge=0.0, le=1.0)
    anger: float = Field(default=0.0, ge=0.0, le=1.0)
    anticipation: float = Field(default=0.0, ge=0.0, le=1.0)


class GoEmotionsDistribution(BaseModel):
    """Google Research 27-Class Fine-Grained Emotion Taxonomy (Demszky et al., ACL 2020)."""
    admiration: float = Field(default=0.0, ge=0.0, le=1.0)
    amusement: float = Field(default=0.0, ge=0.0, le=1.0)
    anger: float = Field(default=0.0, ge=0.0, le=1.0)
    annoyance: float = Field(default=0.0, ge=0.0, le=1.0)
    approval: float = Field(default=0.0, ge=0.0, le=1.0)
    caring: float = Field(default=0.0, ge=0.0, le=1.0)
    confusion: float = Field(default=0.0, ge=0.0, le=1.0)
    curiosity: float = Field(default=0.0, ge=0.0, le=1.0)
    desire: float = Field(default=0.0, ge=0.0, le=1.0)
    disappointment: float = Field(default=0.0, ge=0.0, le=1.0)
    disapproval: float = Field(default=0.0, ge=0.0, le=1.0)
    disgust: float = Field(default=0.0, ge=0.0, le=1.0)
    embarrassment: float = Field(default=0.0, ge=0.0, le=1.0)
    excitement: float = Field(default=0.0, ge=0.0, le=1.0)
    fear: float = Field(default=0.0, ge=0.0, le=1.0)
    gratitude: float = Field(default=0.0, ge=0.0, le=1.0)
    grief: float = Field(default=0.0, ge=0.0, le=1.0)
    joy: float = Field(default=0.0, ge=0.0, le=1.0)
    love: float = Field(default=0.0, ge=0.0, le=1.0)
    nervousness: float = Field(default=0.0, ge=0.0, le=1.0)
    optimism: float = Field(default=0.0, ge=0.0, le=1.0)
    pride: float = Field(default=0.0, ge=0.0, le=1.0)
    realization: float = Field(default=0.0, ge=0.0, le=1.0)
    relief: float = Field(default=0.0, ge=0.0, le=1.0)
    remorse: float = Field(default=0.0, ge=0.0, le=1.0)
    sadness: float = Field(default=0.0, ge=0.0, le=1.0)
    surprise: float = Field(default=0.0, ge=0.0, le=1.0)


class FeelingScore(BaseModel):
    """A specific nuanced psychological feeling state with intensity and confidence."""
    feeling: str = Field(..., description="E.g., vulnerability, burnout, loneliness, grief, hope, longing")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Felt intensity of the emotion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Epistemic confidence")


class SentimentAssessment(BaseModel):
    """Comprehensive sentiment and emotional state appraisal."""
    polarity: SentimentPolarity = Field(..., description="High-level polarity bucket")
    sentiment_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Continuous sentiment score (-1.0=most negative, +1.0=most positive)"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Epistemic confidence")
    conformal_valence_interval: tuple[float, float] = Field(
        ...,
        description="90% Conformal uncertainty bounds for valence [v_min, v_max]."
    )
    vad: VADVector = Field(..., description="3D continuous Valence-Arousal-Dominance affect coordinates")
    emotions: PlutchikEmotions = Field(..., description="Plutchik basic emotion probabilities")
    go_emotions: GoEmotionsDistribution = Field(..., description="Google Research 27 GoEmotions distribution")
    top_feelings: list[FeelingScore] = Field(
        default_factory=list,
        description="Top detected granular psychological feeling states"
    )
