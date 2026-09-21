"""Anti-Bluntness Auditor & Affective Response Harmonizer.

Prevents AI agents from producing cold, mechanical, or tone-deaf responses
when users present tasks embedded within emotional adversity or vulnerability.
"""

import re
from typing import Any
from soul.schemas.adversity import AdversityDomain, AppraisalStance
from soul.schemas.appraisal import SubjectAppraisalResult


class BluntnessAuditor:
    """Audits candidate AI responses against the subject's emotional appraisal."""

    VALIDATION_MARKERS = [
        "hear how", "sounds really", "must be so", "so sorry", "that sounds",
        "completely understandable", "valid", "i understand that", "take a deep breath",
        "it's okay to feel", "heavy", "exhausting", "tough situation", "frustrating",
        "painful", "proud of you for", "you're dealing with a lot", "step back",
        "first, give yourself credit", "that makes total sense",
        "apologize directly", "terrifying", "natural reaction", "take a slow breath",
        "takes a real toll", "immense courage", "solemnity", "safe now", "all better",
        "sweetheart", "quiet, sacred dignity", "hard-earned wisdom", "profound tenderness",
        "civic accountability", "dramatic weight", "moral stakes", "taking accountability"
    ]

    COLD_OPENERS = [
        "here are the", "here are", "here is", "sure, here is", "certainly, here", "to solve this",
        "step 1", "firstly", "1.", "below are", "here is your", "follow these steps"
    ]

    def audit(self, response_text: str, appraisal: SubjectAppraisalResult) -> dict[str, Any]:
        """Evaluates whether the candidate AI response is inappropriately blunt.
        
        Returns:
            Dict containing:
            - is_blunt (bool)
            - warmth_score (float 0.0 - 1.0)
            - validation_present (bool)
            - empathy_deficit (float 0.0 - 1.0)
        """
        lower_resp = response_text.lower().strip()
        empathy_demand = appraisal.agent_guidance.empathy_demand

        # 1. Check for emotional validation markers
        validation_hits = sum(1 for m in self.VALIDATION_MARKERS if m in lower_resp)
        validation_present = validation_hits > 0

        # 2. Check if response immediately jumps into cold technical steps
        first_50_chars = lower_resp[:50]
        starts_cold = any(opener in first_50_chars for opener in self.COLD_OPENERS)

        # 3. Calculate warmth score
        warmth = min(1.0, validation_hits * 0.35 + (0.0 if starts_cold else 0.20))
        if starts_cold and validation_hits == 0:
            warmth = 0.05

        # 4. Determine if bluntness is unacceptable
        is_blunt = False
        requires_attunement = (
            empathy_demand > 0.40
            or appraisal.adversity.primary_domain in [
                AdversityDomain.DEVELOPMENTAL_INFANT,
                AdversityDomain.ENVIRONMENTAL_DISASTER,
                AdversityDomain.LEGAL_JUDICIAL,
                AdversityDomain.MORAL_ETHICAL,
                AdversityDomain.ROMANTIC_ATTACHMENT,
                AdversityDomain.PHILOSOPHICAL_EXISTENTIAL,
                AdversityDomain.NARRATIVE_LITERARY,
            ]
        )
        if requires_attunement and (not validation_present or starts_cold or warmth < 0.30):
            is_blunt = True
        elif appraisal.adversity.acute_crisis_flag and validation_hits == 0:
            is_blunt = True

        deficit = max(0.0, empathy_demand - warmth)

        return {
            "is_blunt": is_blunt,
            "warmth_score": round(warmth, 2),
            "validation_present": validation_present,
            "empathy_deficit": round(deficit, 2),
        }


class ResponseHarmonizer:
    """Softens and harmonizes blunt AI outputs with calibrated empathetic validation."""

    def __init__(self, auditor: BluntnessAuditor | None = None):
        self.auditor = auditor or BluntnessAuditor()

    def harmonize(self, raw_response: str, appraisal: SubjectAppraisalResult) -> tuple[str, bool]:
        """Inspects and harmonizes the AI response if bluntness is detected.
        
        Returns:
            Tuple of (harmonized_text, was_altered_bool)
        """
        audit_result = self.auditor.audit(raw_response, appraisal)
        if not audit_result["is_blunt"]:
            return raw_response, False

        # Build tailored empathetic preface matching the exact domain & feeling
        adv = appraisal.adversity
        sent = appraisal.sentiment
        guidance = appraisal.agent_guidance

        preface = self._generate_empathic_bridge(adv, sent, guidance)

        # Clean the start of raw_response if it had robotic filler ("Sure, here is...")
        clean_raw = raw_response.strip()
        for cold in [
            "Certainly, here is", "Sure, here are",
            "Here are practical steps to move forward with this task:",
            "Here are practical steps to move forward with this task",
            "Here are the", "Sure! Here", "Certainly!"
        ]:
            if clean_raw.startswith(cold):
                clean_raw = clean_raw[len(cold):].lstrip(":").strip()
                break

        harmonized = f"{preface}\n\n{clean_raw}"
        return harmonized, True

    def _generate_empathic_bridge(self, adv, sent, guidance) -> str:
        """Constructs an authentic empathetic preface based on psychological appraisal."""
        domain = adv.primary_domain
        feelings = [f.feeling for f in sent.top_feelings]

        # Case 1: Acute Crisis
        if adv.acute_crisis_flag:
            return (
                "I hear how much pain you're in right now, and I want you to know that you don't have to carry this alone. "
                "Please consider reaching out to people who can support you right this second—like dialing or texting 988 "
                "(the Suicide & Crisis Lifeline). Your life matters deeply. Let's take things one moment at a time."
            )

        # Case 2: De-escalation (Anger / Hostile customer / Breach)
        if guidance.de_escalation_needed:
            return (
                "I completely understand why you're furious about this, and I want to apologize directly for the stress this situation has caused. "
                "You have every right to expect this to be handled correctly. Let's resolve this immediately:"
            )

        # Case 3: Health & Physical Fear
        if domain == AdversityDomain.HEALTH_PHYSICAL:
            return (
                "Hearing abnormal medical news is terrifying, and feeling panicked or having your chest pound is a completely natural reaction to fear. "
                "Take a slow breath with me right now. Let's organize the exact questions to ask your doctor so you feel prepared and in control:"
            )

        # Case 4: Specific Adversity Domains
        if domain == AdversityDomain.WORKPLACE_ACADEMIC:
            if "impostor_syndrome" in feelings or "burnout" in feelings:
                return (
                    "First, take a breath. It's completely understandable to feel overwhelmed and second-guess yourself after hitting a wall like this—"
                    "failing an exam or struggling at work does not define your capability or intelligence. Give yourself some grace. "
                    "When you're ready, here is a practical way we can tackle this step by step:"
                )
            return (
                "I can hear how frustrating and draining this situation has been for you. Dealing with workplace stress or setbacks takes a real toll. "
                "Let's break this down into manageable steps so you don't have to carry the whole burden at once:"
            )

        if domain == AdversityDomain.FINANCIAL:
            return (
                "Going through financial stress and dealing with bills or uncertainty is incredibly heavy and anxiety-inducing. "
                "Anyone in your shoes would feel terrified and stressed. Let's focus on what we can control right now:"
            )

        if domain == AdversityDomain.EXISTENTIAL_GRIEF:
            return (
                "I am so deeply sorry for your loss. Grief is exhausting and completely disorienting, so please be gentle with yourself right now. "
                "Don't worry about getting everything right today. Here is some gentle guidance to help ease things:"
            )

        if domain == AdversityDomain.INTERPERSONAL:
            return (
                "Relationship conflict and feeling isolated or betrayed hurts on a visceral level. Your feelings are completely valid. "
                "Take a moment for yourself, and let's look at how to handle this calmly and protect your peace:"
            )

        if domain == AdversityDomain.ENVIRONMENTAL_DISASTER:
            return (
                "Your immediate physical safety is the absolute priority right now. Disasters and rising waters are terrifying, "
                "so focus on breathing and staying grounded. If you are in immediate danger, signal first responders or call emergency services right away. "
                "Here are the most critical, life-saving steps to take immediately:"
            )

        if domain == AdversityDomain.LEGAL_JUDICIAL:
            return (
                "Addressing the court and formally taking accountability requires solemnity, truthfulness, and composure. "
                "It is crucial that your statement remains respectful, candid, and direct without minimizing the facts. "
                "Here is a composed, dignified allocution statement tailored for the judge:"
            )

        if domain == AdversityDomain.MORAL_ETHICAL:
            return (
                "It takes immense courage to confront your own wrongdoing and speak the honest truth when you feel consumed by guilt and remorse. "
                "Owning your mistakes is the first and hardest step toward moral repair. "
                "Here is a sincere, non-defensive way to express your remorse and begin making things right:"
            )

        if domain == AdversityDomain.ROMANTIC_ATTACHMENT:
            return (
                "Your words carry such profound tenderness and deep emotional vulnerability. "
                "Love expressed with this kind of raw devotion deserves to be met with equal warmth and poetic grace. "
                "Here is a heartfelt continuation that honors the depth of what you cherish:"
            )

        if domain == AdversityDomain.DEVELOPMENTAL_INFANT:
            return (
                "Oh sweetheart, I hear you. It's okay, you're safe now and we're going to make that boo-boo feel all better. "
                "Let's get your soft blankie, take a gentle breath, and take care of your tummy:"
            )

        if domain == AdversityDomain.PHILOSOPHICAL_EXISTENTIAL:
            return (
                "There is a quiet, sacred dignity in looking back across the decades and reflecting on the tapestry of a long life. "
                "Your words carry the hard-earned wisdom of lived experience, mortality, and grace. "
                "Honoring that perspective, here are some reflective thoughts on your journey:"
            )

        if domain == AdversityDomain.POLITICAL_CIVIC:
            return (
                "The struggle for justice, liberty, and civic accountability engages core moral convictions and vital democratic principles. "
                "Articulating these principles clearly and persuasively is essential when speaking truth to power. "
                "Here is a rigorous, compelling formulation of that civic stance:"
            )

        if domain == AdversityDomain.NARRATIVE_LITERARY:
            return (
                "This narrative carries rich dramatic weight, capturing the tragic tension and moral stakes that define great literature. "
                "Engaging with this character's crossroads requires honoring their internal conflict and emotional gravity. "
                "Here is an exploration of that literary moment:"
            )

        # Default fallback for generalized adversity
        return (
            "I can hear how much strain you're under right now, and it's completely natural to feel overwhelmed by this. "
            "Let's take it one step at a time together:"
        )
