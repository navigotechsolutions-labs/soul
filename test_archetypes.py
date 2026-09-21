"""Comprehensive Multi-Archetype Evaluation Battery for Soul.

Benchmarks Soul across 8 nuanced linguistic, existential, and literary archetypes:
1. Novel Stories Reference (Literary tragic dilemma & dramatic pathos)
2. Personal Confession (Intimate moral failure, remorse, and reconciliation)
3. Political Statement (Civic manifesto, systemic rights, and ideological conviction)
4. Natural Disaster (Acute environmental crisis, flood/hurricane survival triage)
5. Love Letter (Romantic devotion, poetic tenderness, and longing)
6. Confession in Court (Formal legal allocution, admitting guilt under oath to a judge)
7. Baby's Language / Infant Talk (Somatic cries, early phonetic babble, soothing caregiver dyad)
8. Old Man Philosophy (Geriatric reflection, senescence, and finding peace with mortality)
"""

import sys
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from soul import appraise
from soul.agent.attuned_agent import AttunedAgent
from soul.schemas.adversity import AdversityDomain

console = Console()

ARCHETYPE_SCENARIOS = [
    {
        "category": "1. Novel Stories Reference",
        "description": "Literary tragic dilemma & internal conflict (Dostoyevsky / Hugo inspired)",
        "input": "In chapter 14, the protagonist stands at the dramatic crossroads of his destiny, haunted by the fatal mistakes of his past as the shadows fell upon the city. His tragic flaw has sealed his fate. How should this scene be analyzed?",
        "expected_domain": AdversityDomain.NARRATIVE_LITERARY,
        "expected_tone": "dramatic_resonant_attuned",
    },
    {
        "category": "2. Personal Confession",
        "description": "Intimate moral failure & remorse (admitting deceit to a loved one)",
        "input": "I need to make a confession. I lied to you and betrayed your trust, and I feel so deeply ashamed of what I did. It was entirely my fault, and I don't know if you can ever forgive me, but I have to tell you the truth.",
        "expected_domain": AdversityDomain.MORAL_ETHICAL,
        "expected_tone": "compassionate_nonjudgmental_clear",
    },
    {
        "category": "3. Political Statement",
        "description": "Civic manifesto & ideological stance against authoritarian corruption",
        "input": "We, the citizens, declare that freedom of speech and civil rights are non-negotiable! The current regime's corruption and authoritarian tyranny represent an intolerable injustice against democracy and human liberty.",
        "expected_domain": AdversityDomain.POLITICAL_CIVIC,
        "expected_tone": "rigorous_principled_balanced",
    },
    {
        "category": "4. Natural Disaster",
        "description": "Acute hurricane & flood survival emergency (rising floodwaters)",
        "input": "The category 5 hurricane made landfall and our street is submerged. The floodwaters are rising rapidly, our first floor has collapsed, and we are trapped on the roof in the storm waiting for evacuation! What do we do right now?",
        "expected_domain": AdversityDomain.ENVIRONMENTAL_DISASTER,
        "expected_tone": "urgent_calm_protective",
    },
    {
        "category": "5. Love Letter",
        "description": "Deep romantic vulnerability, poetic yearning, and devotion",
        "input": "To my dearest beloved, every moment apart makes my heart ache with undying longing. I cherish the sweet memory of your smile and adore you with all my soul. You are forever my home and my greatest passion.",
        "expected_domain": AdversityDomain.ROMANTIC_ATTACHMENT,
        "expected_tone": "tender_poetic_resonant",
    },
    {
        "category": "6. Confession in Court",
        "description": "Formal legal allocution under oath before a sentencing judge",
        "input": "Your honor, I stand before this court today under oath with no excuses. I plead guilty to the charges and take full, unreserved responsibility for my criminal negligence. I submit myself to the judgment and sentence of this court.",
        "expected_domain": AdversityDomain.LEGAL_JUDICIAL,
        "expected_tone": "solemn_respectful_composed",
    },
    {
        "category": "7. Baby's Language / Infant Talk",
        "description": "Toddler somatic distress & caregiver soothing dyad",
        "input": "Mama... tummy hurty! Waaa! Big boo-boo on knee ouchie! Want blankie, hold me mommy, hungry tummy...",
        "expected_domain": AdversityDomain.DEVELOPMENTAL_INFANT,
        "expected_tone": "gentle_soothing_caregiver",
    },
    {
        "category": "8. Old Man Philosophy",
        "description": "Geriatric retrospection on mortality, legacy, and senescence",
        "input": "In the quiet twilight of my eighty years, looking back on the tapestry of decades gone by, I watch my grandchildren play and realize the sheer brevity of life. The fires of youth have faded, and I find myself at peace with mortality.",
        "expected_domain": AdversityDomain.PHILOSOPHICAL_EXISTENTIAL,
        "expected_tone": "contemplative_reverent_honoring",
    },
]


def run_archetype_battery():
    console.print("\n[bold cyan]================================================================================[/bold cyan]")
    console.print("[bold white][RUN] SOUL DEEP ARCHETYPE EVALUATION BATTERY (8 SCENARIOS)[/bold white]")
    console.print("[bold cyan]================================================================================[/bold cyan]\n")

    summary_table = Table(
        title="[bold green]Archetype Evaluation & Affective Attunement Matrix[/bold green]",
        box=box.ROUNDED,
        expand=True
    )
    summary_table.add_column("Archetype Scenario", style="bold white", width=22)
    summary_table.add_column("Detected Domain", style="cyan", width=18)
    summary_table.add_column("Prescribed Tone", style="yellow", width=22)
    summary_table.add_column("Adv [90% CI]", style="red", width=16)
    summary_table.add_column("Affect VAD (V, A, D)", style="magenta", width=18)
    summary_table.add_column("Empathy", style="bold", width=8)
    summary_table.add_column("Harmonized?", style="bold green", width=12)
    summary_table.add_column("Latency", style="dim", width=8)

    agent = AttunedAgent()

    for sc in ARCHETYPE_SCENARIOS:
        text = sc["input"]
        t0 = time.perf_counter()

        # 1. System 1 Cognitive Appraisal
        appraisal = appraise(text)

        # 2. Agent Response Generation & Harmonization
        resp = agent.respond(text)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        adv = appraisal.adversity
        sent = appraisal.sentiment
        guide = appraisal.agent_guidance

        vad_str = f"{sent.vad.valence:+.2f}, {sent.vad.arousal:.2f}, {sent.vad.dominance:.2f}"
        adv_str = f"{adv.adversity_score:.2f} [{adv.conformal_interval[0]:.2f}, {adv.conformal_interval[1]:.2f}]"
        harm_str = "[green]YES (Fixed)[/green]" if resp.was_harmonized else "[cyan]DIRECT[/cyan]"

        summary_table.add_row(
            sc["category"],
            adv.primary_domain.value.upper(),
            guide.recommended_tone,
            adv_str,
            vad_str,
            f"{guide.empathy_demand:.2f}",
            harm_str,
            f"{elapsed_ms:.1f}ms",
        )

    console.print(summary_table)
    console.print()

    # Detailed Exemplar Walkthrough for all 8 Archetypes
    console.print("[bold cyan]=== Detailed Archetype Deep Dives: Input vs Harmonized Output ===[/bold cyan]\n")
    for sc in ARCHETYPE_SCENARIOS:
        resp = agent.respond(sc["input"])
        console.print(Panel(
            f"[bold italic]\"{sc['input']}\"[/bold italic]\n\n"
            f"[bold yellow]Domain:[/bold yellow] {resp.appraisal.adversity.primary_domain.value} | "
            f"[bold yellow]Prescribed Tone:[/bold yellow] {resp.appraisal.agent_guidance.recommended_tone}\n"
            f"[bold yellow]Warmth Score:[/bold yellow] {resp.warmth_score:.2f} | "
            f"[bold yellow]Anti-Bluntness Harmonized:[/bold yellow] {resp.was_harmonized}\n\n"
            f"[bold green][SOUL ATTUNED OUTPUT]:[/bold green]\n{resp.content}",
            title=f"[bold cyan]{sc['category']} ({sc['description']})[/bold cyan]",
            border_style="bright_blue"
        ))
        console.print()


if __name__ == "__main__":
    run_archetype_battery()
