"""Standalone Autonomous Continuous Stress Testing CLI Harness for Soul.

Usage:
    python autonomous_stress_test.py --iterations 500
    python autonomous_stress_test.py --iterations 100 --continuous
"""

import argparse
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
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich import box

from soul.engine.autonomous_tester import AutonomousStressRunner

console = Console()


def run_autonomous_cli(iterations: int = 500, continuous: bool = False):
    console.print("\n[bold cyan]================================================================================[/bold cyan]")
    console.print("[bold white][AUTONOMOUS RUNNER] SOUL CONTINUOUS STRESS & FUZZING ENGINE[/bold white]")
    console.print("[bold cyan]================================================================================[/bold cyan]\n")

    runner = AutonomousStressRunner()
    cycle = 1

    while True:
        console.print(f"[bold yellow]>>> Starting Autonomous Evaluation Cycle #{cycle} ({iterations} iterations)...[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Stress testing Soul...", total=iterations)

            def update_cb(completed, total, avg_lat, domain):
                progress.update(
                    task,
                    completed=completed,
                    description=f"[cyan]Testing {domain.upper()} (Avg Lat: {avg_lat:.2f}ms)"
                )

            report = runner.run_stress_battery(num_iterations=iterations, progress_callback=update_cb)

        # Print Cycle Summary
        results_table = Table(
            title=f"[bold green]Autonomous Cycle #{cycle} Performance & Reliability Summary[/bold green]",
            box=box.ROUNDED,
            expand=True
        )
        results_table.add_column("Metric", style="bold white", width=32)
        results_table.add_column("Observed Value", style="bold yellow", width=24)
        results_table.add_column("Target Threshold", style="green", width=24)

        results_table.add_row("Total Permutations Tested", str(report.total_iterations), "N/A")
        results_table.add_row("Successful Runs (Zero Crash)", f"[bold green]{report.successful_runs}[/bold green]", "100%")
        results_table.add_row("Fuzzing Edge Cases Tested", str(report.fuzzing_edge_cases_tested), ">= 15 Edge Cases")
        results_table.add_row("Crashes / Unhandled Exceptions", f"[bold green]{report.crash_count}[/bold green]", "0 Crashes")
        results_table.add_row("Average Latency", f"{report.avg_latency_ms:.2f} ms", "< 2.0 ms")
        results_table.add_row("P50 Latency (Median)", f"{report.p50_latency_ms:.2f} ms", "< 1.0 ms")
        results_table.add_row("P95 Latency", f"{report.p95_latency_ms:.2f} ms", "< 3.0 ms")
        results_table.add_row("P99 Latency (Tail)", f"{report.p99_latency_ms:.2f} ms", "< 5.0 ms")
        results_table.add_row("Conformal Empirical Coverage", f"[bold green]{report.conformal_coverage_rate:.1f}%[/bold green]", ">= 90.0%")
        results_table.add_row("Anti-Bluntness Success Rate", f"[bold green]{report.anti_bluntness_success_rate:.1f}%[/bold green]", ">= 95.0%")

        console.print(results_table)
        console.print()

        # Domain Distribution Breakdown
        dom_table = Table(title="[bold cyan]Domain Coverage Distribution[/bold cyan]", box=box.SIMPLE)
        dom_table.add_column("Domain", style="white")
        dom_table.add_column("Count", style="green")
        for d, count in sorted(report.domain_breakdown.items(), key=lambda x: x[1], reverse=True):
            dom_table.add_row(d.upper(), str(count))
        console.print(dom_table)
        console.print()

        if report.errors:
            console.print(Panel("\n".join(report.errors), title="[red]Sample Errors[/red]", border_style="red"))

        if not continuous:
            break

        cycle += 1
        time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous stress tester for Soul")
    parser.add_argument("--iterations", type=int, default=500, help="Number of test iterations")
    parser.add_argument("--continuous", action="store_true", help="Run indefinitely in a loop")
    args = parser.parse_args()

    run_autonomous_cli(iterations=args.iterations, continuous=args.continuous)
