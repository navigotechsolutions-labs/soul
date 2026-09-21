"""Soul: Jev-Style System 1 Cognitive Adversity & Affective Sentiment Appraisal Engine.

An ultra-fast, calibrated, non-autoregressive decision model for understanding
adversity, emotional affect (Valence-Arousal-Dominance), and psychological feelings,
coupled with an Anti-Bluntness Context Harmonizer for AI agents.
"""

from soul.adapters.agent_middleware import AgentEmpathyMiddleware
from soul.agent.attuned_agent import AttunedAgent, AttunedAgentResponse
from soul.engine.adversity_analyzer import AdversityAnalyzer
from soul.engine.appraiser import SoulAppraiser
from soul.engine.calibrator import Calibrator
from soul.engine.feeling_analyzer import FeelingAnalyzer
from soul.engine.go_emotions import GoEmotionsAnalyzer
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer
from soul.schemas.adversity import (
    AdversityAssessment,
    AdversityDomain,
    AppraisalStance,
    COREDimensions,
    SchererAppraisalChecks,
)
from soul.schemas.appraisal import (
    ActionUrgency,
    AgentGuidance,
    SubjectAppraisalResult,
)
from soul.schemas.sentiment import (
    FeelingScore,
    GoEmotionsDistribution,
    PlutchikEmotions,
    SentimentAssessment,
    SentimentPolarity,
    VADVector,
)

__version__ = "0.3.0"

_DEFAULT_APPRAISER = SoulAppraiser()
_DEFAULT_AGENT = AttunedAgent(appraiser=_DEFAULT_APPRAISER)


def appraise(state: str | dict, subject_id: str | None = None) -> SubjectAppraisalResult:
    """Convenience function to quickly appraise text or state dictionary."""
    return _DEFAULT_APPRAISER.appraise(state, subject_id=subject_id)


def respond(user_message: str, base_system_prompt: str | None = None) -> AttunedAgentResponse:
    """Convenience function to generate an emotionally attuned, anti-blunt response."""
    kwargs = {}
    if base_system_prompt:
        kwargs["base_system_prompt"] = base_system_prompt
    return _DEFAULT_AGENT.respond(user_message, **kwargs)


__all__ = [
    "appraise",
    "respond",
    "SoulAppraiser",
    "AttunedAgent",
    "AttunedAgentResponse",
    "BluntnessAuditor",
    "ResponseHarmonizer",
    "Calibrator",
    "AdversityAnalyzer",
    "FeelingAnalyzer",
    "GoEmotionsAnalyzer",
    "AgentEmpathyMiddleware",
    "SubjectAppraisalResult",
    "AdversityAssessment",
    "AdversityDomain",
    "AppraisalStance",
    "COREDimensions",
    "SchererAppraisalChecks",
    "SentimentAssessment",
    "SentimentPolarity",
    "VADVector",
    "PlutchikEmotions",
    "GoEmotionsDistribution",
    "FeelingScore",
    "ActionUrgency",
    "AgentGuidance",
]
