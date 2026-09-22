"""Unified Human-POV Experience & Sensation Auditor for Soul.

Provides holistic evaluation of AI outputs, UI copy, and digital products
from the perspective of human perception, sensory aesthetics, and emotional resonance.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field

from soul.engine.slop_detector import SlopAuditor, SlopAuditResult
from soul.engine.aesthetic_sanitizer import AestheticAuditor, AestheticAuditResult
from soul.engine.harmonizer import BluntnessAuditor
from soul.engine.appraiser import SoulAppraiser
from soul.schemas.appraisal import SubjectAppraisalResult


class HumanFeelReport(BaseModel):
    """Complete multi-dimensional scorecard of human felt experience."""
    overall_human_score: int = Field(
        ...,
        description="Overall Human Presence Score (0-100). Higher means authentic, tactile human craft."
    )
    status: str = Field(
        ...,
        description="Verdict: 'AUTHENTIC_HUMAN_CRAFT', 'STERILE_ROBOTIC', or 'CRITICAL_AI_SLOP'."
    )
    slop_audit: SlopAuditResult = Field(..., description="Audit of linguistic tropes, em-dashes, and emojis.")
    aesthetic_audit: Optional[AestheticAuditResult] = Field(None, description="Audit of visual/color/palette tropes.")
    cognitive_friction_score: float = Field(
        ...,
        description="Cognitive load (0.0 low friction/easy to read, 1.0 exhausting wall of text)."
    )
    empathy_warmth_score: float = Field(
        ...,
        description="Warmth score (0.0 cold/robotic, 1.0 attuned and validating)."
    )
    sensory_breathing_room: str = Field(
        ...,
        description="Evaluation of text rhythm, whitespace, and conversational cadence."
    )
    key_criticisms: list[str] = Field(default_factory=list, description="Top issues preventing human connection.")
    actionable_prescriptions: list[str] = Field(default_factory=list, description="Directives to restore human feel.")
    humanized_alternative: str = Field(..., description="Sanitized, humanized rewrite.")


class HumanFeelAuditor:
    """Master evaluator of Human Felt Experience across copy, UI, and AI responses."""

    def __init__(
        self,
        slop_auditor: SlopAuditor | None = None,
        aesthetic_auditor: AestheticAuditor | None = None,
        bluntness_auditor: BluntnessAuditor | None = None,
        appraiser: SoulAppraiser | None = None,
    ):
        self.slop_auditor = slop_auditor or SlopAuditor()
        self.aesthetic_auditor = aesthetic_auditor or AestheticAuditor()
        self.bluntness_auditor = bluntness_auditor or BluntnessAuditor()
        self.appraiser = appraiser or SoulAppraiser()

    def audit(
        self,
        content: str,
        user_context: str | None = None,
        include_aesthetics: bool = True
    ) -> HumanFeelReport:
        """Audits content from the Human POV.
        
        Args:
            content: The AI-generated output, UI copy, or website text to audit.
            user_context: Optional context of what the human user originally said or needed.
            include_aesthetics: Whether to run color/palette checks on the text/css.
            
        Returns:
            HumanFeelReport with scores, diagnoses, and humanized output.
        """
        # 1. Linguistic & Slop Audit
        slop_res = self.slop_auditor.audit(content)

        # 2. Aesthetic Audit (if requested)
        aesthetic_res = None
        if include_aesthetics:
            aesthetic_res = self.aesthetic_auditor.audit(content)

        # 3. Cognitive Friction & Rhythm Check
        words = content.split()
        word_count = len(words)
        sentences = [s.strip() for s in content.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        avg_sentence_len = word_count / max(1, len(sentences))
        
        # High friction if sentences are long and uniform, or if bullet points dominate
        bullet_count = content.count("\n-") + content.count("\n*") + content.count("\n1.") + content.count("\n2.")
        friction = 0.2
        if avg_sentence_len > 22:
            friction += 0.35
        if bullet_count >= 4:
            friction += 0.25
        if word_count > 150 and "\n\n" not in content:
            friction += 0.30  # Wall of text
        friction = min(1.0, friction)

        if friction > 0.6:
            breathing_room = "SUFFOCATING (Dense paragraphs, high reading friction, lacks visual whitespace)"
        elif friction > 0.35:
            breathing_room = "MODERATE (Could use shorter sentences and rhythmic variation)"
        else:
            breathing_room = "OPEN & BREATHEABLE (Natural human cadence)"

        # 4. Empathy & Warmth Check
        if user_context:
            appraisal = self.appraiser.appraise(user_context)
            blunt_res = self.bluntness_auditor.audit(content, appraisal)
            warmth = blunt_res["warmth_score"]
        else:
            # Standalone tone appraisal
            appraisal = self.appraiser.appraise(content)
            valence = appraisal.sentiment.vad.valence
            warmth = max(0.1, min(1.0, (valence + 1.0) / 2.0))

        # 5. Composite Score Calculation
        # Weighting: 45% Slop Freedom, 25% Cognitive Breathing, 20% Warmth, 10% Aesthetics
        score_slop = slop_res.human_authenticity_score
        score_friction = int((1.0 - friction) * 100)
        score_warmth = int(warmth * 100)
        score_aes = aesthetic_res.aesthetic_health_score if aesthetic_res else 80

        overall_score = int(
            (score_slop * 0.45)
            + (score_friction * 0.25)
            + (score_warmth * 0.20)
            + (score_aes * 0.10)
        )
        overall_score = max(5, min(100, overall_score))

        # Status determination
        if overall_score >= 80:
            status = "AUTHENTIC_HUMAN_CRAFT"
        elif overall_score >= 50:
            status = "STERILE_ROBOTIC"
        else:
            status = "CRITICAL_AI_SLOP"

        # Gather key criticisms
        criticisms = list(slop_res.criticisms)
        if friction > 0.5:
            criticisms.append("High cognitive friction: Sentences are dense and fatigue the human eye.")
        if aesthetic_res and aesthetic_res.criticisms:
            criticisms.extend(aesthetic_res.criticisms)
        if warmth < 0.3:
            criticisms.append("Emotional tone is clinical, detached, or overly procedural.")

        # Gather actionable prescriptions
        prescriptions = list(slop_res.prescriptions)
        if friction > 0.5:
            prescriptions.append("Break dense paragraphs into punchy, varying rhythmic lengths. Add paragraph breaks.")
        if aesthetic_res and aesthetic_res.has_generic_ai_purple:
            prescriptions.append(f"Replace generic AI purple with: {aesthetic_res.recommended_palette['name']}.")
        if warmth < 0.3:
            prescriptions.append("Inject warmth: acknowledge the human context before jumping into procedural lists.")

        return HumanFeelReport(
            overall_human_score=overall_score,
            status=status,
            slop_audit=slop_res,
            aesthetic_audit=aesthetic_res,
            cognitive_friction_score=round(friction, 2),
            empathy_warmth_score=round(warmth, 2),
            sensory_breathing_room=breathing_room,
            key_criticisms=criticisms,
            actionable_prescriptions=prescriptions,
            humanized_alternative=slop_res.sanitized_text,
        )
