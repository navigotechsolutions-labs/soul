"""Sensory & Aesthetic Sanitizer for Soul.

Detects generic "AI-generated design tropes" (ubiquitous neon violet/indigo gradients,
radioactive lime green accents, copy-paste bento grids, excessive glassmorphism blur)
and prescribes calibrated, high-end human editorial aesthetics.
"""

import re
from typing import Any
from pydantic import BaseModel, Field


# Infamous AI-generated violet / purple hex codes (Tailwind purple-600, violet-500, indigo-600, etc.)
GENERIC_AI_PURPLES = {
    "#7c3aed": "Tailwind Violet-600 (The default ChatGPT / V0 purple)",
    "#8a2be2": "BlueViolet (#8A2BE2) - Generic AI neon purple",
    "#6366f1": "Tailwind Indigo-500 (#6366F1)",
    "#a855f7": "Tailwind Purple-500 (#A855F7)",
    "#9333ea": "Tailwind Purple-600 (#9333EA)",
    "#8b5cf6": "Tailwind Violet-500 (#8B5CF6)",
    "#4f46e5": "Tailwind Indigo-600 (#4F46E5)",
    "#6d28d9": "Tailwind Violet-700 (#6D28D9)",
}

# Radioactive neon accents often paired with dark mode in AI templates
RADIOACTIVE_NEONS = {
    "#00ff66": "Radioactive Lime / Hacker Green",
    "#00ff00": "Pure Neon Green",
    "#39ff14": "Neon Lime (#39FF14)",
    "#00ffff": "Radioactive Cyan / Electric Aqua (#00FFFF)",
    "#06b6d4": "Tailwind Cyan-500",
}

# Curated Human Editorial Palettes
HUMAN_EDITORIAL_PALETTES = [
    {
        "name": "Obsidian & Warm Bone (Editorial Luxury)",
        "background": "#0F0F10",
        "surface": "#1A1A1C",
        "text_primary": "#F4F1EA",
        "text_secondary": "#A3A099",
        "accent": "#E06D53",  # Warm Terracotta
        "border": "#28272A",
        "description": "Tactile, warm-toned dark mode that eliminates sterile blue glare.",
    },
    {
        "name": "Swiss Monolith (High Contrast Minimalist)",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "text_primary": "#111111",
        "text_secondary": "#666666",
        "accent": "#002B49",  # Deep Prussion Blue
        "border": "#E5E5E5",
        "description": "Rigid typographical hierarchy and razor-sharp clarity without novelty gradients.",
    },
    {
        "name": "Deep Forest Slate (Calm & Grounded)",
        "background": "#0D1312",
        "surface": "#16201E",
        "text_primary": "#EAF0ED",
        "text_secondary": "#8D9E97",
        "accent": "#68A085",  # Sage patina
        "border": "#243330",
        "description": "Organic, low-arousal psychological presence ideal for focus and stress mitigation.",
    },
]


class AestheticAuditResult(BaseModel):
    """Result of an aesthetic and design trope audit."""
    aesthetic_health_score: int = Field(..., description="Score 0-100 (100 = artisanal human craft, < 50 = AI template slop).")
    has_generic_ai_purple: bool = Field(..., description="True if infamous ChatGPT / Tailwind purple-violet tones detected.")
    detected_ai_colors: list[str] = Field(default_factory=list, description="List of detected AI trope hex colors.")
    has_radioactive_neons: bool = Field(..., description="True if eye-straining neon greens/cyans detected.")
    criticisms: list[str] = Field(default_factory=list, description="Critique of the visual choices.")
    recommended_palette: dict[str, Any] = Field(..., description="Human editorial palette recommendation.")
    ui_layout_guidelines: list[str] = Field(default_factory=list, description="Directives to escape AI bento/glassmorphism slop.")


class AestheticAuditor:
    """Audits colors, styles, and UI layout patterns for synthetic AI design clichés."""

    def __init__(self):
        self._hex_pattern = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")

    def audit(self, text_or_css: str) -> AestheticAuditResult:
        """Inspects CSS, HTML, Tailwind classes, or design tokens for AI clichés."""
        lower_input = text_or_css.lower()
        found_hexes = [h.lower() for h in self._hex_pattern.findall(lower_input)]

        # Expand 3-digit hex to 6-digit for matching
        normalized_hexes = []
        for h in found_hexes:
            if len(h) == 4:
                normalized = "#" + "".join(c * 2 for c in h[1:])
                normalized_hexes.append(normalized)
            else:
                normalized_hexes.append(h)

        detected_purples: list[str] = []
        detected_neons: list[str] = []
        criticisms: list[str] = []
        penalty = 0

        # 1. Check for Generic AI Purple
        for h in normalized_hexes:
            if h in GENERIC_AI_PURPLES:
                detected_purples.append(f"{h} ({GENERIC_AI_PURPLES[h]})")
        
        # Also check Tailwind class mentions
        tailwind_purple_hints = ["violet-600", "purple-600", "indigo-600", "from-purple-", "to-indigo-", "from-violet-"]
        for hint in tailwind_purple_hints:
            if hint in lower_input:
                detected_purples.append(f"Tailwind class '{hint}'")

        if detected_purples:
            penalty += 35
            criticisms.append(
                f"Detected ubiquitous 'AI Purple/Indigo' palette ({', '.join(set(detected_purples[:3]))}). "
                "This violet gradient is used by over 85% of AI-generated templates and immediately signals synthetic origin."
            )

        # 2. Check for Radioactive Neons
        for h in normalized_hexes:
            if h in RADIOACTIVE_NEONS:
                detected_neons.append(f"{h} ({RADIOACTIVE_NEONS[h]})")

        if detected_neons:
            penalty += 25
            criticisms.append(
                f"Detected harsh radioactive neons ({', '.join(set(detected_neons[:3]))}). "
                "Causes visual glare and cognitive fatigue on OLED and high-brightness displays."
            )

        # 3. Check for glassmorphism / bento grid buzzwords
        if "backdrop-blur" in lower_input or "backdrop-filter" in lower_input:
            if "border-white/10" in lower_input or "border-white/20" in lower_input:
                penalty += 15
                criticisms.append("Excessive frosted glassmorphism (backdrop-blur + white border) detected. Increases GPU overhead and decreases contrast.")

        score = max(10, 100 - penalty)
        has_generic_ai_purple = len(detected_purples) > 0
        has_radioactive_neons = len(detected_neons) > 0

        # Curate layout guidelines
        guidelines = [
            "Break the symmetrical 6-card bento grid: use asymmetric visual anchors (e.g. 60/40 hero ratio).",
            "Replace generic drop-shadows with subtle 1px border elevation (e.g., #28272A on #0F0F10).",
            "Anchor content with high typographical scale contrast (large display headers paired with quiet body copy).",
            "Eliminate multi-color neon gradients: stick to a single, intentional warm accent color."
        ]

        return AestheticAuditResult(
            aesthetic_health_score=score,
            has_generic_ai_purple=has_generic_ai_purple,
            detected_ai_colors=list(set(detected_purples + detected_neons)),
            has_radioactive_neons=has_radioactive_neons,
            criticisms=criticisms,
            recommended_palette=HUMAN_EDITORIAL_PALETTES[0],  # Obsidian & Warm Bone
            ui_layout_guidelines=guidelines,
        )
