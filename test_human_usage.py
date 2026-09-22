"""Demonstration of how Everyday Humans use Soul for sensitive communications."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import soul
from soul.agent.attuned_agent import AttunedAgent
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer

console = Console()

HUMAN_SCENARIOS = [
    {
        "title": "Scenario 1: Workplace Crisis (Making a severe error before a furious boss)",
        "incoming_message": "The client presentation you delivered today had glaring calculation errors. The account director was furious. We need to talk first thing tomorrow morning.",
        "blunt_draft": "I will review the spreadsheet formulas and have the corrected numbers ready before 9 AM.",
        "context_explanation": "When an executive is furious, responding with mere mechanical task compliance sounds indifferent and dismissive. They need to hear accountability, composure, and emotional recognition of the client risk."
    },
    {
        "title": "Scenario 2: Personal Relationship / Vulnerability (Hurt partner)",
        "incoming_message": "You've been working late every single night this week. You missed dinner again. I feel like our life together doesn't even matter to you anymore.",
        "blunt_draft": "I have an important product deadline to hit this week. I will be home earlier next week.",
        "context_explanation": "The partner is not complaining about logistics; they are feeling lonely, abandoned, and invisible. Rationalizing with deadlines makes them feel secondary and unheard."
    },
    {
        "title": "Scenario 3: Urgent Customer Support (Mother in distress at pharmacy)",
        "incoming_message": "You debited $450 from my checking account by mistake today! Now my card is declined at the pharmacy for my daughter's asthma medicine. Fix this right now!",
        "blunt_draft": "Billing errors are investigated within 3 to 5 business days per Section 4 of our User Terms of Service.",
        "context_explanation": "Quoting policy terms to a parent trying to buy medicine for a sick child triggers rage. They need immediate human validation, priority urgency, and emergency resolution."
    },
    {
        "title": "Scenario 4: Bereavement & Deep Grief (Friend mourning their mother)",
        "incoming_message": "I walked into my mom's room today and caught the scent of her perfume. It hit me that I will never hear her voice again and I broke down in tears.",
        "blunt_draft": "Time heals all wounds. You should try to stay busy and remember the happy memories.",
        "context_explanation": "Generic clichés invalidate acute bereavement. Grieving people don't need solutions or pep talks; they need someone to sit with their pain and honor their loss."
    }
]


def test_human_scenarios():
    auditor = BluntnessAuditor()
    harmonizer = ResponseHarmonizer(auditor=auditor)

    console.print(Panel(
        "[bold cyan]SOUL ENGINE: REAL-WORLD HUMAN COMMUNICATION TEST[/bold cyan]\n"
        "[italic]Testing how a human uses Soul to understand deep feelings and write empathetic, effective responses.[/italic]",
        border_style="cyan"
    ))

    for idx, item in enumerate(HUMAN_SCENARIOS, 1):
        console.print(f"\n[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]")
        console.print(f"[bold yellow]👉 {item['title']}[/bold yellow]")
        console.print(f"[dim]{item['context_explanation']}[/dim]\n")

        # 1. Decode Situation with Soul
        appraisal = soul.appraise(item["incoming_message"])

        # Display Emotional Analysis Table
        table = Table(title="🧠 What the Person is TRULY Feeling (Decoded by Soul in <1ms)", box=box.ROUNDED)
        table.add_column("Psychological Dimension", style="bold white", width=26)
        table.add_column("Soul Diagnostic", style="bold green")
        table.add_column("Human Impact", style="dim")

        table.add_row(
            "Primary Stress Domain",
            appraisal.adversity.primary_domain.value.upper(),
            f"Adversity Score: {appraisal.adversity.adversity_score:.2f} / 1.0"
        )
        table.add_row(
            "Cognitive Stance",
            appraisal.adversity.appraisal_stance.value.upper(),
            "Lazarus Stress Model"
        )
        table.add_row(
            "Emotional Valence & Arousal",
            f"Valence: {appraisal.sentiment.vad.valence:+.2f} | Arousal: {appraisal.sentiment.vad.arousal:.2f}",
            "Affective state intensity"
        )
        feelings = ", ".join(f"{f.feeling.title()} ({f.intensity:.2f})" for f in appraisal.sentiment.top_feelings) or "Distress"
        table.add_row("Deep Feelings", feelings, "Subconscious emotional drivers")
        table.add_row(
            "Required Human Response Tone",
            f"[bold magenta]{appraisal.agent_guidance.recommended_tone.replace('_', ' ').title()}[/bold magenta]",
            f"Empathy Demand: {appraisal.agent_guidance.empathy_demand:.2f} / 1.0"
        )
        console.print(table)

        # 2. Harmonize the Human Response
        audit = auditor.audit(item["blunt_draft"], appraisal)
        harmonized_text, was_harmonized = harmonizer.harmonize(
            raw_response=item["blunt_draft"],
            appraisal=appraisal
        )

        console.print()
        console.print(Panel(
            f"[bold red]❌ The Cold / Blunt Mistake Most People Make:[/bold red]\n"
            f"[dim]\"{item['blunt_draft']}\"[/dim]\n\n"
            f"[red]⚠️ Why it fails: Measured Warmth Score = {audit['warmth_score']:.2f}. "
            f"It ignores emotional stakes and triggers defensive backlash.[/red]",
            border_style="red"
        ))

        console.print(Panel(
            f"[bold green]✅ What to Send Instead (Soul Attuned Response):[/bold green]\n\n"
            f"[bold white]{harmonized_text}[/bold white]\n\n"
            f"[green]✨ Impact: Validates the human emotion first, defuses anxiety/anger, and provides clear action.[/green]",
            border_style="green"
        ))


if __name__ == "__main__":
    test_human_scenarios()
