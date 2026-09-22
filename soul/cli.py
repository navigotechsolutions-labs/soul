"""Command-Line Interface for Soul System 1 Appraisal Engine."""

import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from soul import appraise
from soul.schemas.appraisal import SubjectAppraisalResult


console = Console()


def render_bar(value: float, max_val: float = 1.0, width: int = 15, color: str = "cyan") -> str:
    """Renders a progress bar."""
    ratio = max(0.0, min(1.0, value / max_val))
    filled = int(round(ratio * width))
    bar = "=" * filled + "-" * (width - filled)
    return f"[{color}][{bar}][/{color}] {value:0.2f}"


def display_appraisal(result: SubjectAppraisalResult, original_text: str):
    """Renders a rich terminal summary of the appraisal."""
    console.print()
    console.print(Panel(
        f"[bold italic]\"{original_text}\"[/bold italic]",
        title=f"[bold cyan]Input State[/bold cyan] ({result.text_length} chars | {result.execution_time_ms} ms | System 1)",
        border_style="cyan"
    ))

    # 1. Adversity Table
    adv = result.adversity
    adv_table = Table(title="[bold red]Adversity & Cognitive Stress Appraisal (Lazarus + Stoltz CORE + Scherer CPM)[/bold red]", box=box.ROUNDED, expand=True)
    adv_table.add_column("Metric", style="bold white", width=22)
    adv_table.add_column("Assessment", style="bold")
    adv_table.add_column("Scientific Framework", style="dim")

    color_adv = "red" if adv.adversity_score > 0.65 else ("yellow" if adv.adversity_score > 0.35 else "green")
    adv_table.add_row(
        "Adversity Intensity",
        f"{render_bar(adv.adversity_score, color=color_adv)} (90% Conformal: [{adv.conformal_interval[0]:.2f}, {adv.conformal_interval[1]:.2f}])",
        f"Conf: {adv.confidence:.2f} (Angelopoulos 2021)"
    )
    adv_table.add_row("Primary Domain", f"[magenta]{adv.primary_domain.value.upper()}[/magenta]", "")
    adv_table.add_row("Cognitive Stance", f"[yellow]{adv.appraisal_stance.value.upper()}[/yellow]", "Lazarus Transactional Stress")
    adv_table.add_row("Threat vs Challenge", f"{adv.threat_vs_challenge_ratio:+.2f} ([-1 threat, +1 challenge])", "Lazarus Cognitive Stance")
    adv_table.add_row("Coping Agency", render_bar(adv.coping_agency, color="blue"), "Bandura Self-Efficacy")
    
    # Stoltz CORE
    core = adv.core
    core_desc = f"C: {core.control:.2f} | O: {core.ownership:.2f} | R: {core.reach:.2f} | E: {core.endurance:.2f}"
    adv_table.add_row("Stoltz CORE Index", f"[cyan]{core_desc}[/cyan]", "Control, Ownership, Reach, Endurance")

    # Scherer CPM
    cpm = adv.cpm_checks
    cpm_desc = f"Goal Conduciveness: {cpm.goal_conduciveness:+.2f} | Coping Potential: {cpm.coping_potential:.2f}"
    adv_table.add_row("Scherer CPM Checks", f"[italic]{cpm_desc}[/italic]", "Stimulus Evaluation Checks (Scherer 2009)")

    crisis_text = "[bold white on red] CRITICAL CRISIS DETECTED [/bold white on red]" if adv.acute_crisis_flag else "[green]No acute crisis flags[/green]"
    adv_table.add_row("Crisis Triage", crisis_text, ", ".join(adv.crisis_indicators) if adv.crisis_indicators else "Nominal")

    console.print(adv_table)

    # 2. Sentiment & Affect Table
    sent = result.sentiment
    sent_table = Table(title="[bold blue]Affect, Sentiment & GoEmotions (Russell VAD + Google 27 GoEmotions)[/bold blue]", box=box.ROUNDED, expand=True)
    sent_table.add_column("Dimension", style="bold white", width=22)
    sent_table.add_column("Score / Vector", style="bold")
    sent_table.add_column("Psychological Meaning", style="dim")

    pol_color = "red" if "negative" in sent.polarity.value else ("green" if "positive" in sent.polarity.value else "yellow")
    sent_table.add_row(
        "Polarity",
        f"[{pol_color}]{sent.polarity.value.upper()}[/{pol_color}] ({sent.sentiment_score:+.2f})",
        f"90% Conformal: [{sent.conformal_valence_interval[0]:.2f}, {sent.conformal_valence_interval[1]:.2f}]"
    )
    sent_table.add_row("Valence (V)", f"{sent.vad.valence:+.2f}", "Pleasure (+1) to Displeasure (-1)")
    sent_table.add_row("Arousal (A)", render_bar(sent.vad.arousal, color="magenta"), "Calm (0) to Agitated (1)")
    sent_table.add_row("Dominance (D)", render_bar(sent.vad.dominance, color="cyan"), "Submissive/Helpless (0) to In Control (1)")

    # Top GoEmotions
    ge_dict = sent.go_emotions.model_dump()
    top_ge = sorted([(k, v) for k, v in ge_dict.items() if v > 0.05], key=lambda x: x[1], reverse=True)[:4]
    top_ge_desc = ", ".join(f"{k} ({v:.2f})" for k, v in top_ge) if top_ge else "neutral"
    sent_table.add_row("Google GoEmotions", f"[bold green]{top_ge_desc}[/bold green]", "27 Fine-Grained Classes (ACL 2020)")

    feelings_desc = " | ".join(f"{f.feeling} ({f.intensity:.2f})" for f in sent.top_feelings) if sent.top_feelings else "None prominent"
    sent_table.add_row("Nuanced Feelings", f"[bold yellow]{feelings_desc}[/bold yellow]", "Granular psychological states")

    console.print(sent_table)

    # 3. Agent Guidance Panel
    guide = result.agent_guidance
    guide_panel = Panel(
        f"[bold]Empathy Demand:[/bold] {render_bar(guide.empathy_demand, color='purple')}\n"
        f"[bold]Action Urgency:[/bold] [bold red]{guide.urgency.value.upper()}[/bold red]\n"
        f"[bold]Prescribed Tone:[/bold] [bold cyan]{guide.recommended_tone}[/bold cyan]\n"
        f"[bold]De-escalation Needed:[/bold] {'[bold red]YES[/bold red]' if guide.de_escalation_needed else '[green]NO[/green]'}\n"
        f"[bold]Triggers:[/bold] {', '.join(guide.action_triggers) if guide.action_triggers else 'Standard workflow'}",
        title="[bold green]Agent System 1 Guidance & Dispatch[/bold green]",
        border_style="green"
    )
    console.print(guide_panel)
    console.print()


def demonstrate_fix(user_text: str):
    """Shows side-by-side comparison of Default Blunt AI vs Soul Attuned AI."""
    from soul.agent.attuned_agent import AttunedAgent
    
    agent = AttunedAgent()
    resp = agent.respond(user_text)

    console.print()
    console.print(Panel(
        f"[bold italic]\"{user_text}\"[/bold italic]",
        title="[bold yellow]User Problem / Task (With Emotional Context)[/bold yellow]",
        border_style="yellow"
    ))

    # Raw / Blunt
    console.print(Panel(
        f"[dim]{resp.raw_draft}[/dim]",
        title="[bold red]❌ Standard AI (Blunt, Ignored Feelings)[/bold red]",
        border_style="red"
    ))

    # Soul Attuned
    badge = "[bold green]HARMONIZED[/bold green]" if resp.was_harmonized else "[bold cyan]ATTUNED[/bold cyan]"
    console.print(Panel(
        f"[bold white]{resp.content}[/bold white]",
        title=f"[bold green]✅ Soul Attuned AI ({badge} | Warmth: {resp.warmth_score:.2f})[/bold green]",
        border_style="green"
    ))
    console.print()


def handle_audit_command(args: list[str]):
    """Handles 'soul audit' command to evaluate text or files from Human POV."""
    from soul import audit_human_feel

    if len(args) < 2 or args[1] in ("--help", "-h"):
        console.print("[bold yellow]Usage:[/bold yellow]")
        console.print("  soul audit \"<text or UI copy to audit>\" [--context \"<user prompt>\"] [--fail-on-slop]")
        console.print("  soul audit --file <path/to/file.txt> [--fail-on-slop]")
        return

    content = ""
    user_context = None
    fail_on_slop = "--fail-on-slop" in args
    is_json = "--json" in args

    for i, arg in enumerate(args):
        if arg == "--file" and i + 1 < len(args):
            try:
                with open(args[i + 1], "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                console.print(f"[red]Failed to read file: {e}[/red]")
                sys.exit(1)
        elif arg == "--context" and i + 1 < len(args):
            user_context = args[i + 1]

    if not content:
        # Collect non-flag arguments
        non_flags = [a for a in args[1:] if not a.startswith("--") and a != user_context]
        if non_flags:
            content = " ".join(non_flags)

    if not content:
        console.print("[red]Error: Please provide text or a file to audit.[/red]")
        return

    report = audit_human_feel(content, user_context=user_context)

    if is_json:
        print(report.model_dump_json(indent=2))
        if fail_on_slop and report.status != "AUTHENTIC_HUMAN_CRAFT":
            sys.exit(1)
        return

    # Rich Terminal Output
    console.print()
    border_color = "green" if report.status == "AUTHENTIC_HUMAN_CRAFT" else ("yellow" if report.status == "STERILE_ROBOTIC" else "red")
    console.print(Panel(
        f"[bold italic]\"{content[:300]}{'...' if len(content) > 300 else ''}\"[/bold italic]",
        title=f"[bold {border_color}]Human Sensation & Anti-Slop Audit[/bold {border_color}] ({len(content)} chars)",
        border_style=border_color
    ))

    audit_table = Table(title="[bold]Human Experience Scorecard[/bold]", box=box.ROUNDED, expand=True)
    audit_table.add_column("Pillar", style="bold white", width=25)
    audit_table.add_column("Score / Reading", style="bold")
    audit_table.add_column("Verdict / Details", style="dim")

    # Score row
    status_style = "bold green" if report.status == "AUTHENTIC_HUMAN_CRAFT" else ("bold yellow" if report.status == "STERILE_ROBOTIC" else "bold red")
    audit_table.add_row(
        "Overall Human Presence",
        f"[{status_style}]{report.overall_human_score} / 100[/{status_style}]",
        f"[{status_style}]{report.status}[/{status_style}]"
    )

    # Slop details
    slop = report.slop_audit
    emoji_desc = f"[red]{slop.emoji_icon_count} emoji(s)[/red] ({', '.join(slop.emojis_found)})" if slop.emoji_icon_count else "[green]Zero emoji crutches[/green]"
    audit_table.add_row("Emoji-as-Icon Usage", emoji_desc, "Substituted for real UI icons")

    dash_desc = f"[red]{slop.em_dash_count} em-dashes[/red]" if slop.em_dash_count >= 2 else f"[green]{slop.em_dash_count} em-dashes[/green]"
    audit_table.add_row("Em-Dash Saturation", dash_desc, "AI clause-stitching crutch")

    cliche_desc = f"[red]{', '.join(slop.ai_cliches_found)}[/red]" if slop.ai_cliches_found else "[green]None detected[/green]"
    audit_table.add_row("AI Buzzwords & Clichés", cliche_desc, "ChatGPT hallmark lexicon ('delve', 'testament')")

    audit_table.add_row(
        "Cognitive Breathing Room",
        f"{report.sensory_breathing_room.split('(')[0].strip()}",
        f"Friction: {report.cognitive_friction_score:.2f} | Warmth: {report.empathy_warmth_score:.2f}"
    )

    # Aesthetic details (if any)
    if report.aesthetic_audit and report.aesthetic_audit.detected_ai_colors:
        audit_table.add_row(
            "AI Palette Trope",
            f"[red]{', '.join(report.aesthetic_audit.detected_ai_colors[:2])}[/red]",
            "Generic AI Purple / Radioactive Neon"
        )

    console.print(audit_table)

    if report.key_criticisms:
        crit_text = "\n".join(f"[bold red]•[/bold red] {c}" for c in report.key_criticisms)
        console.print(Panel(crit_text, title="[bold red]Human Disconnect Criticisms[/bold red]", border_style="red"))

    if report.actionable_prescriptions:
        presc_text = "\n".join(f"[bold green]✓[/bold green] {p}" for p in report.actionable_prescriptions)
        console.print(Panel(presc_text, title="[bold green]Actionable Human Prescriptions[/bold green]", border_style="green"))

    if report.humanized_alternative and report.humanized_alternative != content:
        console.print(Panel(
            f"[bold white]{report.humanized_alternative}[/bold white]",
            title="[bold cyan]✨ Harmonized Human Version (Slop Eradicated)[/bold cyan]",
            border_style="cyan"
        ))
    console.print()

    if fail_on_slop and report.status != "AUTHENTIC_HUMAN_CRAFT":
        console.print("[bold red]Failed CI Check: Content did not meet authentic human standards.[/bold red]")
        sys.exit(1)


def handle_sanitize_command(args: list[str]):
    """Handles 'soul sanitize' command to instantly humanize text."""
    from soul import sanitize_slop

    if len(args) < 2 or args[1] in ("--help", "-h"):
        console.print("[bold yellow]Usage:[/bold yellow]")
        console.print("  soul sanitize \"<text with AI slop>\"")
        return

    text = " ".join(args[1:])
    sanitized = sanitize_slop(text)

    console.print()
    console.print(Panel(
        f"[dim]{text}[/dim]",
        title="[bold red]Original AI Output[/bold red]",
        border_style="red"
    ))
    console.print(Panel(
        f"[bold green]{sanitized}[/bold green]",
        title="[bold green]Humanized (Slop Eradicated)[/bold green]",
        border_style="green"
    ))
    console.print()


def handle_key_command(args: list[str]):
    """Handles 'soul key generate' and 'soul key info' commands."""
    from soul.engine.api_key_manager import APIKeyManager
    mgr = APIKeyManager()

    if len(args) < 2 or args[1] in ("--help", "-h"):
        console.print("[bold yellow]Usage:[/bold yellow]")
        console.print("  soul key generate --name <client_name> [--email <email>]")
        console.print("  soul key info <api_key>")
        return

    subcmd = args[1]
    if subcmd == "generate":
        client_name = "Developer"
        email = ""
        for i, arg in enumerate(args):
            if arg == "--name" and i + 1 < len(args):
                client_name = args[i + 1]
            elif arg == "--email" and i + 1 < len(args):
                email = args[i + 1]

        res = mgr.generate_key(client_name=client_name, email=email)
        console.print()
        console.print(Panel(
            f"[bold green]API Key Generated Successfully![/bold green]\n\n"
            f"[bold cyan]API Key:[/bold cyan] [bold white on blue] {res['api_key']} [/bold white on blue]\n"
            f"[bold cyan]Key Prefix:[/bold cyan] {res['key_prefix']}\n"
            f"[bold cyan]Client Name:[/bold cyan] {res['client_name']}\n"
            f"[bold cyan]Tier:[/bold cyan] {res['tier']} ({res['rate_limit']})\n\n"
            f"[dim]Store this key securely. Pass it as header: Authorization: Bearer {res['api_key']}[/dim]",
            title="[bold green]🔑 Soul Self-Service API Key[/bold green]",
            border_style="green"
        ))
        console.print()
    elif subcmd == "info":
        if len(args) < 3:
            console.print("[red]Error: Please specify the API key to inspect.[/red]")
            return
        key = args[2]
        info = mgr.get_key_info(key)
        if not info:
            console.print("[bold red]❌ Key not found or revoked.[/bold red]")
            return
        console.print()
        console.print(Panel(
            f"[bold]Client Name:[/bold] {info['client_name']}\n"
            f"[bold]Key Prefix:[/bold] {info['key_prefix']}\n"
            f"[bold]Tier:[/bold] {info['tier']}\n"
            f"[bold]Total Requests Used:[/bold] {info['request_count']}\n"
            f"[bold]Active Status:[/bold] {'[green]Active[/green]' if info['is_active'] else '[red]Revoked[/red]'}",
            title="[bold cyan]API Key Info[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
    else:
        console.print(f"[red]Unknown key command: {subcmd}[/red]")


def handle_ide_command(args: list[str]):
    """Launches the standalone Soul IDE workbench in the browser."""
    import uvicorn
    import webbrowser
    import threading

    port = 8000
    host = "127.0.0.1"
    no_browser = "--no-browser" in args

    for i, arg in enumerate(args):
        if arg == "--port" and i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                pass
        elif arg == "--host" and i + 1 < len(args):
            host = args[i + 1]

    url = f"http://{host}:{port}/ide"

    console.print()
    console.print(Panel(
        f"[bold green]Starting Standalone Soul IDE Workbench...[/bold green]\n\n"
        f"[bold cyan]Local Workspace:[/bold cyan]    [bold white on blue] {url} [/bold white on blue]\n"
        f"[bold cyan]Universal Gateway:[/bold cyan]  http://{host}:{port}/v1/chat/completions\n"
        f"[bold cyan]Swagger API Docs:[/bold cyan]   http://{host}:{port}/docs\n\n"
        f"[dim]Press Ctrl+C to stop the Soul IDE server.[/dim]",
        title="[bold green]💻 Soul IDE — Human-POV Integrated Development Environment[/bold green]",
        border_style="green"
    ))
    console.print()

    if not no_browser:
        def open_browser():
            import time
            time.sleep(1.2)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("soul.server:app", host=host, port=port, log_level="info")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        console.print("[bold yellow]Usage:[/bold yellow]")
        console.print("  soul ide [--port 8000] [--no-browser]")
        console.print("  soul audit \"<text or UI copy>\" [--context \"<user prompt>\"] [--fail-on-slop]")
        console.print("  soul sanitize \"<text with AI slop>\"")
        console.print("  soul \"<sentence to appraise>\" [--json | --demonstrate-fix]")
        console.print("  soul key generate --name \"My Project\" [--email dev@example.com]")
        console.print("  soul key info soul_live_<token>")
        console.print("\nExamples:")
        console.print("  soul ide                                                                    # Launch Standalone IDE in browser")
        console.print("  soul audit \"In today's fast-paced world—efficiency is crucial. 🚀 Delve!\"  # Audit copy for AI slop")
        console.print("  soul sanitize \"In today's fast-paced world—efficiency is crucial. 🚀\"      # Instantly humanize")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd in ("ide", "studio", "ui"):
        handle_ide_command(sys.argv[1:])
        return

    if cmd == "key":
        handle_key_command(sys.argv[1:])
        return

    if cmd == "audit":
        handle_audit_command(sys.argv[1:])
        return

    if cmd == "sanitize":
        handle_sanitize_command(sys.argv[1:])
        return

    text = sys.argv[1]
    is_json = "--json" in sys.argv
    is_fix = "--demonstrate-fix" in sys.argv or "--compare" in sys.argv

    if is_fix:
        demonstrate_fix(text)
        return

    result = appraise(text)

    if is_json:
        print(result.model_dump_json(indent=2))
    else:
        display_appraisal(result, text)


if __name__ == "__main__":
    main()



