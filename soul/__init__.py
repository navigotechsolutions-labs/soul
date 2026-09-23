"""Soul: Jev-Style System 1 Cognitive Adversity & Affective Sentiment Appraisal Engine.

An ultra-fast, calibrated, non-autoregressive decision model for understanding
adversity, emotional affect (Valence-Arousal-Dominance), and psychological feelings,
coupled with an Anti-Bluntness Context Harmonizer for AI agents.
"""

from soul.adapters.agent_middleware import AgentEmpathyMiddleware
from soul.agent.attuned_agent import AttunedAgent, AttunedAgentResponse
from soul.client import SoulClient, SoulAPIError
from soul.engine.adversity_analyzer import AdversityAnalyzer
from soul.engine.appraiser import SoulAppraiser
from soul.engine.calibrator import Calibrator
from soul.engine.feeling_analyzer import FeelingAnalyzer
from soul.engine.go_emotions import GoEmotionsAnalyzer
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer
from soul.engine.slop_detector import SlopAuditor, SlopAuditResult
from soul.engine.aesthetic_sanitizer import AestheticAuditor, AestheticAuditResult
from soul.engine.human_feel_auditor import HumanFeelAuditor, HumanFeelReport
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

__version__ = "0.4.0"


_DEFAULT_APPRAISER = SoulAppraiser()
_DEFAULT_AGENT = AttunedAgent(appraiser=_DEFAULT_APPRAISER)
_DEFAULT_SLOP_AUDITOR = SlopAuditor()
_DEFAULT_AESTHETIC_AUDITOR = AestheticAuditor()
_DEFAULT_HUMAN_AUDITOR = HumanFeelAuditor(
    slop_auditor=_DEFAULT_SLOP_AUDITOR,
    aesthetic_auditor=_DEFAULT_AESTHETIC_AUDITOR,
    appraiser=_DEFAULT_APPRAISER,
)


def appraise(state: str | dict, subject_id: str | None = None) -> SubjectAppraisalResult:
    """Convenience function to quickly appraise text or state dictionary."""
    return _DEFAULT_APPRAISER.appraise(state, subject_id=subject_id)


def respond(user_message: str, base_system_prompt: str | None = None) -> AttunedAgentResponse:
    """Convenience function to generate an emotionally attuned, anti-blunt response."""
    kwargs = {}
    if base_system_prompt:
        kwargs["base_system_prompt"] = base_system_prompt
    return _DEFAULT_AGENT.respond(user_message, **kwargs)


def audit_human_feel(
    content: str,
    user_context: str | None = None,
    include_aesthetics: bool = True
) -> HumanFeelReport:
    """Audits content from the Human POV (detecting AI slop, emojis-as-icons, em-dashes, and palettes)."""
    return _DEFAULT_HUMAN_AUDITOR.audit(
        content, user_context=user_context, include_aesthetics=include_aesthetics
    )


def audit_slop(text: str) -> SlopAuditResult:
    """Audits text for synthetic AI clichés, emoji-as-icon abuse, and syntactic tropes."""
    return _DEFAULT_SLOP_AUDITOR.audit(text)


def sanitize_slop(text: str) -> str:
    """Removes AI buzzwords, replaces em-dashes, and strips emoji crutches for authentic human cadence."""
    return _DEFAULT_SLOP_AUDITOR.sanitize(text)


def audit_aesthetics(text_or_css: str) -> AestheticAuditResult:
    """Audits CSS/colors for generic AI purple, radioactive neons, and glassmorphism tropes."""
    return _DEFAULT_AESTHETIC_AUDITOR.audit(text_or_css)


__all__ = [
    "appraise",
    "respond",
    "audit_human_feel",
    "audit_slop",
    "sanitize_slop",
    "audit_aesthetics",
    "SoulClient",
    "SoulAPIError",
    "SoulAppraiser",
    "AttunedAgent",
    "AttunedAgentResponse",
    "BluntnessAuditor",
    "ResponseHarmonizer",
    "SlopAuditor",
    "SlopAuditResult",
    "AestheticAuditor",
    "AestheticAuditResult",
    "HumanFeelAuditor",
    "HumanFeelReport",
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

