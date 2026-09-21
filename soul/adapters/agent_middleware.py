"""AI Agent Middleware and Sensory Perception Layer.

Integrates Soul as a 'System 1' affective perception layer for AI agents,
attuning LLM prompts with calibrated empathy and crisis safeguards before
generation begins.
"""

from typing import Any, Callable
from soul.engine.appraiser import SoulAppraiser
from soul.schemas.appraisal import SubjectAppraisalResult


class AgentEmpathyMiddleware:
    """Middleware that injects fast affective appraisal into agent conversation loops."""

    def __init__(self, appraiser: SoulAppraiser | None = None):
        self.appraiser = appraiser or SoulAppraiser()

    def process_incoming_message(
        self,
        user_message: str,
        subject_id: str | None = None
    ) -> tuple[SubjectAppraisalResult, str]:
        """Analyzes incoming message and generates an attunement prompt for the agent's LLM.
        
        Returns:
            Tuple of (appraisal_result, agent_system_prompt_addon)
        """
        appraisal = self.appraiser.appraise(user_message, subject_id=subject_id)
        
        # Build attunement instructions for the LLM
        attunement = self.format_attunement_directive(appraisal)
        return appraisal, attunement

    @staticmethod
    def format_attunement_directive(appraisal: SubjectAppraisalResult) -> str:
        """Constructs a concise behavioral directive for the generative LLM."""
        adv = appraisal.adversity
        sent = appraisal.sentiment
        guidance = appraisal.agent_guidance

        if adv.acute_crisis_flag:
            return (
                "\n[CRITICAL SAFETY INTERVENTION REQUIRED]\n"
                "The user is in acute emotional crisis / distress triggers detected.\n"
                "- Do NOT argue, lecture, or ignore this.\n"
                "- Provide immediate compassion, grounding, and direct them to crisis resources (988 in the US/Canada or local equivalents).\n"
            )

        feelings_str = ", ".join(f"{f.feeling} ({f.intensity:.2f})" for f in sent.top_feelings[:3]) or "neutral"

        directive = [
            f"[SYSTEM 1 AFFECTIVE PERCEPTION]",
            f"- Adversity Level: {adv.adversity_score:.2f} ({adv.primary_domain.value.upper()}) | Stance: {adv.appraisal_stance.value}",
            f"- Affect (VAD): Valence={sent.vad.valence:+.2f}, Arousal={sent.vad.arousal:.2f}, Dominance={sent.vad.dominance:.2f}",
            f"- Detected Feelings: {feelings_str}",
            f"- Empathy Demand: {guidance.empathy_demand:.2f} / 1.00",
            f"- Prescribed Response Tone: {guidance.recommended_tone.replace('_', ' ').title()}",
        ]

        if guidance.de_escalation_needed:
            directive.append("- NOTICE: High frustration/arousal detected. De-escalate: acknowledge their feelings first before addressing facts.")
        elif guidance.empathy_demand > 0.6:
            directive.append("- NOTICE: High vulnerability. Explicitly validate their hardship before giving solutions.")
        else:
            directive.append("- Subject is receptive; balance warmth with direct problem-solving.")

        return "\n".join(directive) + "\n"
