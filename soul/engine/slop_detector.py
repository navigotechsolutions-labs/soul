"""Anti-AI-Slop & Human Language Authenticity Engine for Soul.

Detects, scores, and eradicates ubiquitous AI-generated clichés, syntactic tropes,
emoji-as-icon abuse, and robotic phrasing across text and UI copy.
"""

import re
from typing import Any
from pydantic import BaseModel, Field


# Common emojis frequently substituted for actual UI icons, bullet points, or badges
COMMON_UI_EMOJIS = {
    "🚀": "rocket / launch / start",
    "✨": "sparkles / AI magic / special",
    "💡": "lightbulb / idea / tip",
    "🔥": "fire / hot / trending",
    "⚡": "lightning / fast / speed",
    "🎯": "target / goal / focus",
    "🧠": "brain / smart / intelligence",
    "🤖": "robot / AI / automation",
    "📈": "chart / growth / performance",
    "🔑": "key / essential / unlock",
    "🛠️": "tools / build / utility",
    "🌟": "star / highlight",
    "💎": "gem / premium / value",
    "👉": "pointing finger / click here",
    "✅": "check mark / verified",
    "🎉": "party / celebration",
}

# The classic ChatGPT / AI Hallmark Lexicon
AI_CLICHE_WORDS = [
    "delve", "delving", "delves",
    "testament", "tapestries", "tapestry",
    "beacon", "beacons",
    "crucial", "paramount", "pivotal",
    "foster", "fostering", "fosters",
    "elevate", "elevating", "elevates",
    "unleash", "unleashing", "unleashes",
    "harness", "harnessing", "harnesses",
    "game-changer", "game changer",
    "dive deep", "deep dive", "diving deep",
    "demystify", "demystifying",
    "synergy", "synergies",
    "multifaceted", "plethora",
    "seamless", "seamlessly",
    "bustling", "vibrant",
    "ever-evolving", "fast-paced",
    "in today's world", "in today's digital landscape", "in today's fast-paced",
    "look no further",
    "it is important to remember", "it's important to note",
    "at the end of the day",
    "not only", "revolutionize", "revolutionary",
]

# Generic AI Naming Prefixes and Suffixes
AI_NAMING_PREFIXES = ["omni", "nexus", "synapse", "nova", "aura", "veritas", "cogni", "hyper", "neuro", "zenith"]
AI_NAMING_SUFFIXES = ["ify", "flow", "sync", "ly", "hub", "ai", "bot", "lab"]


class SlopAuditResult(BaseModel):
    """Result of an anti-slop audit."""
    human_authenticity_score: int = Field(
        ...,
        description="Authenticity score from 0 (pure AI slop) to 100 (crisp, authentic human voice)."
    )
    slop_detected: bool = Field(..., description="True if synthetic AI tropes exceed acceptable thresholds.")
    emoji_icon_count: int = Field(..., description="Count of emojis used as UI icons or bullet points.")
    emojis_found: list[str] = Field(default_factory=list, description="List of detected emojis.")
    em_dash_count: int = Field(..., description="Count of em-dashes (—) or double hyphens (--) detected.")
    ai_cliches_found: list[str] = Field(default_factory=list, description="List of detected AI buzzwords and clichés.")
    has_formulaic_parallelism: bool = Field(..., description="True if 'not only... but also' or formulaic structures found.")
    has_lecture_disclaimer: bool = Field(..., description="True if 'important to remember/note' filler found.")
    criticisms: list[str] = Field(default_factory=list, description="Human POV criticisms of the copy.")
    prescriptions: list[str] = Field(default_factory=list, description="Actionable directives to humanize the text.")
    sanitized_text: str = Field(..., description="Humanized version with AI slop and syntactic tropes eradicated.")


class SlopAuditor:
    """Audits text and UI copy for synthetic AI hallmarks and provides human sanitization."""

    def __init__(self):
        # Compile regex for em-dashes and double hyphens
        self._em_dash_pattern = re.compile(r"(\s*—\s*|\s*--\s*)")
        self._emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA70-\U0001FAFF"
            "]+",
            flags=re.UNICODE
        )

    def audit(self, text: str) -> SlopAuditResult:
        """Evaluates text for synthetic AI clichés, emoji-as-icon abuse, and syntactic tropes."""
        if not text or not text.strip():
            return SlopAuditResult(
                human_authenticity_score=100,
                slop_detected=False,
                emoji_icon_count=0,
                emojis_found=[],
                em_dash_count=0,
                ai_cliches_found=[],
                has_formulaic_parallelism=False,
                has_lecture_disclaimer=False,
                criticisms=[],
                prescriptions=[],
                sanitized_text="",
            )

        lower_text = text.lower()
        criticisms: list[str] = []
        prescriptions: list[str] = []
        penalty = 0

        # 1. Emoji-as-icon check
        emojis_found = self._emoji_pattern.findall(text)
        emoji_count = len(emojis_found)
        if emoji_count > 0:
            penalty += min(40, emoji_count * 12)
            criticisms.append(
                f"Detected {emoji_count} emoji(s) ({', '.join(set(emojis_found))}) used as decorative visual crutches or faux-icons. "
                "This gives a toy-like, low-trust appearance."
            )
            prescriptions.append("Replace emojis with clean semantic SVG icons (e.g. Lucide) or rely on strong typographic hierarchy.")

        # 2. Em-dash saturation check
        em_dash_matches = self._em_dash_pattern.findall(text)
        em_dash_count = len(em_dash_matches)
        word_count = max(1, len(text.split()))
        dash_density = (em_dash_count / word_count) * 100

        if em_dash_count >= 2 or dash_density > 2.0:
            penalty += min(30, em_dash_count * 12)
            criticisms.append(
                f"High em-dash density ({em_dash_count} em-dashes across {word_count} words). "
                "AI uses em-dashes obsessively to stitch fragmented clauses without committing to crisp sentences."
            )
            prescriptions.append("Break compound em-dash clauses into direct, confident standalone sentences or use commas.")

        # 3. AI Cliché Lexicon check
        found_cliches: list[str] = []
        for cliche in AI_CLICHE_WORDS:
            # Word boundary search
            pattern = rf"\b{re.escape(cliche)}\b"
            if re.search(pattern, lower_text):
                found_cliches.append(cliche)

        if found_cliches:
            cliche_penalty = len(found_cliches) * 15
            penalty += min(45, cliche_penalty)
            criticisms.append(
                f"Detected signature AI buzzwords: {', '.join(found_cliches)}. "
                "These words instantly trigger human uncanny-valley fatigue."
            )
            prescriptions.append(f"Eradicate buzzwords ({', '.join(found_cliches)}) in favor of precise, grounded verbs and nouns.")

        # 4. Formulaic structures ("not only... but also", "it is important to remember")
        has_parallelism = "not only" in lower_text and ("but also" in lower_text or "but" in lower_text)
        if has_parallelism:
            penalty += 12
            criticisms.append("Formulaic 'not only... but also' parallelism detected. Classic LLM persuasive template.")
            prescriptions.append("State the primary value proposition directly without rhetorical preamble.")

        has_lecture_disclaimer = any(
            phrase in lower_text for phrase in [
                "important to remember", "important to note", "crucial to keep in mind", "in conclusion"
            ]
        )
        if has_lecture_disclaimer:
            penalty += 15
            criticisms.append("Patronizing 'important to note/remember' lecturing disclaimer detected.")
            prescriptions.append("Cut the disclaimer entirely and deliver the information with respect for the reader's intelligence.")

        # Calculate authenticity score
        human_authenticity_score = max(5, 100 - penalty)
        slop_detected = penalty >= 25 or len(found_cliches) > 0 or emoji_count >= 2 or em_dash_count >= 2

        # Generate sanitized text
        sanitized_text = self.sanitize(text, found_cliches=found_cliches, remove_emojis=True)

        return SlopAuditResult(
            human_authenticity_score=human_authenticity_score,
            slop_detected=slop_detected,
            emoji_icon_count=emoji_count,
            emojis_found=list(set(emojis_found)),
            em_dash_count=em_dash_count,
            ai_cliches_found=found_cliches,
            has_formulaic_parallelism=has_parallelism,
            has_lecture_disclaimer=has_lecture_disclaimer,
            criticisms=criticisms,
            prescriptions=prescriptions,
            sanitized_text=sanitized_text,
        )

    def sanitize(self, text: str, found_cliches: list[str] | None = None, remove_emojis: bool = True) -> str:
        """Sanitizes AI text by stripping buzzwords, replacing em-dashes, and cleaning emojis."""
        result = text

        # 1. Strip emojis if requested
        if remove_emojis:
            result = self._emoji_pattern.sub("", result)

        # 2. Replace em-dashes and double hyphens with crisp punctuation
        # If em-dash is in middle of sentence, replace with comma or period
        result = re.sub(r"\s*—\s*", ", ", result)
        result = re.sub(r"\s*--\s*", ", ", result)

        # 3. Replace common AI cliché phrases with human alternatives
        replacements = {
            r"\bin today's fast-paced digital landscape\b": "today",
            r"\bin today's fast-paced world\b": "today",
            r"\bin today's world\b": "today",
            r"\bdelve into\b": "explore",
            r"\bdelves into\b": "explores",
            r"\bdelving into\b": "exploring",
            r"\bdelve\b": "look closely",
            r"\ba testament to\b": "proof of",
            r"\btestament to\b": "proof of",
            r"\brich tapestry of\b": "depth of",
            r"\btapestry of\b": "range of",
            r"\btapestry\b": "fabric",
            r"\bbeacon of\b": "model of",
            r"\bgame-changer\b": "major step forward",
            r"\bgame changer\b": "major step forward",
            r"\bdive deep into\b": "examine",
            r"\bdive deep\b": "focus closely",
            r"\bdeep dive\b": "close examination",
            r"\bplethora of\b": "many",
            r"\bmultifaceted\b": "complex",
            r"\bseamlessly\b": "smoothly",
            r"\bseamless\b": "smooth",
            r"\bunleash the power of\b": "use",
            r"\bunleash\b": "release",
            r"\bharness the power of\b": "use",
            r"\bharness\b": "apply",
            r"\belevate your\b": "improve your",
            r"\belevate\b": "lift",
            r"\bfoster\b": "support",
            r"\bfostering\b": "supporting",
            r"\bcrucial\b": "essential",
            r"\bparamount\b": "critical",
            r"\bpivotal\b": "decisive",
            r"\blook no further\b": "",
            r"\bit is important to remember that\b": "",
            r"\bit's important to remember that\b": "",
            r"\bit is important to note that\b": "",
            r"\bit's important to note that\b": "",
            r"\bit is crucial to keep in mind that\b": "",
            r"\bin conclusion,?\b": "",
        }

        for pat, repl in replacements.items():
            result = re.sub(pat, repl, result, flags=re.IGNORECASE)

        # 4. Clean up consecutive commas, spaces, or awkward punctuation
        result = re.sub(r",\s*,", ",", result)
        result = re.sub(r"\s+", " ", result)
        result = re.sub(r"\s+([.,;:!?])", r"\1", result)
        result = result.strip()

        # Capitalize first letter of sentences
        sentences = re.split(r"([.!?]\s+)", result)
        capitalized = "".join(
            s.capitalize() if i % 2 == 0 and s else s for i, s in enumerate(sentences)
        )

        return capitalized.strip()
