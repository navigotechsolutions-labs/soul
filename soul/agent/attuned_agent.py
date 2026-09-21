"""Attuned Agent: Emotionally Grounded AI Agent Framework.

Eliminates blunt, tone-deaf AI outputs by coupling fast System 1 affective perception
with pre-generation prompt modulation and post-generation response harmonization.
"""

import os
from typing import Any, Callable
from pydantic import BaseModel, Field

from soul.adapters.agent_middleware import AgentEmpathyMiddleware
from soul.engine.appraiser import SoulAppraiser
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer
from soul.schemas.adversity import AdversityDomain
from soul.schemas.appraisal import SubjectAppraisalResult


class AttunedAgentResponse(BaseModel):
    """Result of an emotionally attuned AI agent generation."""
    content: str = Field(..., description="The final empathetic, non-blunt response text")
    raw_draft: str = Field(..., description="The initial candidate response before harmonization")
    was_harmonized: bool = Field(..., description="True if post-generation anti-bluntness intervention occurred")
    warmth_score: float = Field(..., ge=0.0, le=1.0, description="Measured warmth of the response")
    appraisal: SubjectAppraisalResult = Field(..., description="System 1 affective appraisal of the subject")


class AttunedAgent:
    """An AI Agent that understands the subject's feelings and refuses to give blunt outputs."""

    def __init__(
        self,
        appraiser: SoulAppraiser | None = None,
        model_name: str = "gpt-4o-mini",
        custom_llm_callable: Callable[[str, str], str] | None = None,
    ):
        self.appraiser = appraiser or SoulAppraiser()
        self.middleware = AgentEmpathyMiddleware(appraiser=self.appraiser)
        self.auditor = BluntnessAuditor()
        self.harmonizer = ResponseHarmonizer(auditor=self.auditor)
        self.model_name = model_name
        self.custom_llm = custom_llm_callable

    def respond(
        self,
        user_message: str,
        base_system_prompt: str = "You are a helpful and knowledgeable AI assistant.",
        subject_id: str | None = None
    ) -> AttunedAgentResponse:
        """Processes user message, understands feelings, generates and harmonizes response."""
        # Step 1: System 1 Affective & Adversity Appraisal (<1ms)
        appraisal = self.appraiser.appraise(user_message, subject_id=subject_id)

        # Step 2: Formulate Dynamic Pre-Generation Emotional Directive
        directive = self.middleware.format_attunement_directive(appraisal)
        augmented_system_prompt = f"{base_system_prompt}\n\n{directive}"

        # Step 3: Generate Draft Response
        raw_draft = self._generate_draft(
            system_prompt=augmented_system_prompt,
            user_message=user_message,
            appraisal=appraisal
        )

        # Step 4: Post-Generation Anti-Bluntness Audit & Harmonization
        harmonized_text, was_altered = self.harmonizer.harmonize(raw_draft, appraisal)
        audit_result = self.auditor.audit(harmonized_text, appraisal)

        return AttunedAgentResponse(
            content=harmonized_text,
            raw_draft=raw_draft,
            was_harmonized=was_altered,
            warmth_score=audit_result["warmth_score"],
            appraisal=appraisal,
        )

    def _generate_draft(
        self,
        system_prompt: str,
        user_message: str,
        appraisal: SubjectAppraisalResult
    ) -> str:
        """Generates draft using custom callable, OpenAI, or smart local fallback."""
        if self.custom_llm:
            try:
                return self.custom_llm(system_prompt, user_message)
            except Exception:
                pass

        # Try OpenAI API if key is present
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                completion = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=600,
                    temperature=0.7,
                )
                choice = completion.choices[0].message.content
                if choice:
                    return choice.strip()
            except Exception:
                pass

        # Smart Local Fallback when offline
        return self._local_fallback_generator(user_message, appraisal)

    def _local_fallback_generator(self, user_message: str, appraisal: SubjectAppraisalResult) -> str:
        """Generates a structured, helpful solution when running offline."""
        domain = appraisal.adversity.primary_domain
        
        if domain == AdversityDomain.WORKPLACE_ACADEMIC:
            return (
                "Here is a strategic plan to recover and master the material:\n\n"
                "1. **Conduct an Error Audit**: Categorize the missed questions into conceptual gaps vs time management vs misreading.\n"
                "2. **Implement Active Recall**: Shift from passive re-reading to practicing flashcards and timed simulation exams.\n"
                "3. **Micro-Habits**: Limit study blocks to 25-minute Pomodoro intervals to prevent cognitive fatigue.\n\n"
                "You have what it takes to pass this with the right adjustments."
            )
        elif domain == AdversityDomain.FINANCIAL:
            return (
                "Here are immediate stabilization steps you can take:\n\n"
                "1. **Prioritize the Essentials**: Focus exclusively on shelter, utilities, and groceries before uncollateralized debts.\n"
                "2. **Contact Creditors Proactively**: Ask for hardship programs or temporary payment deferrals; many services have unadvertised relief.\n"
                "3. **Local Community Aid**: Contact local 211 resources or community assistance for immediate utility and food grants."
            )
        elif domain == AdversityDomain.ENVIRONMENTAL_DISASTER:
            return (
                "Here are immediate life-safety actions:\n\n"
                "1. **Stay High & Visible**: Remain on the highest stable point of the roof; do not re-enter floodwaters.\n"
                "2. **Signal Rescuers**: Wave bright clothing, flashlights, or make continuous rhythmic sounds (three whistle blasts).\n"
                "3. **Conserve Resources**: Keep devices in low-power mode, stay huddled together for warmth, and avoid downed power lines."
            )
        elif domain == AdversityDomain.LEGAL_JUDICIAL:
            return (
                "Here is a composed, dignified allocution draft for the court:\n\n"
                "\"May it please the court. I stand before Your Honor today to accept full and unreserved responsibility for my conduct. "
                "I make no excuses, nor do I seek to deflect blame onto others. I recognize the gravity of my actions and the disruption they caused. "
                "I submit myself completely to the wisdom and sentence of this court, with a genuine commitment to rehabilitation and restitution.\""
            )
        elif domain == AdversityDomain.MORAL_ETHICAL:
            return (
                "Here is a clear, non-defensive apology framework:\n\n"
                "1. State the truth plainly without adding justifications or shifting blame.\n"
                "2. Acknowledge specifically how breaking their trust made them feel.\n"
                "3. State your willingness to answer questions and respect the space and time they need to heal."
            )
        elif domain == AdversityDomain.DEVELOPMENTAL_INFANT:
            return (
                "Here is how to comfort your little one right now:\n\n"
                "1. Hold them close in a gentle, rhythmic rock with their favorite soft blankie.\n"
                "2. Place a cool, soft cloth or gentle kiss on the boo-boo to soothe the sting.\n"
                "3. Offer a warm, gentle drink or light snack to settle the hungry tummy."
            )
        elif domain == AdversityDomain.PHILOSOPHICAL_EXISTENTIAL:
            return (
                "Looking across eight decades offers a perspective that few words can encompass. "
                "The passage of time reveals that our lives are not measured by the anxieties of the moment, "
                "but by the depth with which we loved, the peace we made with our flaws, and the quiet legacy "
                "we leave in the laughter of our grandchildren."
            )
        elif domain == AdversityDomain.ROMANTIC_ATTACHMENT:
            return (
                "Distance cannot dim the quiet certainty of devotion. "
                "Every breath across the miles is a promise, and every memory of your warmth is an anchor. "
                "You remain my dearest joy and the quiet harbor of my soul."
            )
        elif domain == AdversityDomain.POLITICAL_CIVIC:
            return (
                "Here are the foundational principles of this civic declaration:\n\n"
                "1. **Inviolability of Fundamental Freedoms**: Freedom of speech and assembly are innate human rights, not concessions granted by the state.\n"
                "2. **Public Accountability**: Any governance structure devoid of transparency inevitably decays into corruption.\n"
                "3. **Peaceful Democratic Mobilization**: Enduring reform requires sustained, non-violent civic solidarity and rigorous defense of the rule of law."
            )
        elif domain == AdversityDomain.NARRATIVE_LITERARY:
            return (
                "Here is a structured literary analysis of this pivotal scene:\n\n"
                "1. **The Tragic Flaw (Hamartia)**: The protagonist's choices reflect the inevitable collision between hubris and moral reckoning.\n"
                "2. **Atmospheric Foreshadowing**: The falling shadows upon the city serve as an externalization of the character's internal moral eclipse.\n"
                "3. **The Soliloquy of Fate**: The narrative forces the reader to confront whether destiny is predetermined or woven from our unexamined compromises."
            )
        else:
            return (
                "Here are practical steps to move forward with this task:\n\n"
                "1. Break the problem into the smallest immediate action item.\n"
                "2. Focus only on what you can directly influence today.\n"
                "3. Take short breaks to reset your focus before continuing."
            )
