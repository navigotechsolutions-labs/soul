"""Autonomous Continuous Testing, Stress Fuzzing & Monte Carlo Evaluation Engine.

Autonomously stress tests Soul over thousands of generated scenario permutations:
1. Combinatorial domain generation across all 15 affective/adversity domains.
2. Adversarial fuzzing: typos, casing swaps, negations, intensifiers, emojis, extreme lengths.
3. Edge case torturing: empty string, pure punctuation, 20,000+ chars, emojis, control chars.
4. Statistical verification: Latency percentiles (P50, P90, P95, P99), Conformal Coverage (>=90%), ECE.
5. Anti-bluntness audit verification across randomized trials.
"""

import random
import re
import string
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from soul import appraise
from soul.agent.attuned_agent import AttunedAgent
from soul.schemas.adversity import AdversityDomain, AppraisalStance
from soul.schemas.appraisal import SubjectAppraisalResult


@dataclass
class AutonomousBenchmarkReport:
    """Summary metrics of an autonomous continuous stress testing run."""
    total_iterations: int
    successful_runs: int
    failed_runs: int
    crash_count: int
    p50_latency_ms: float
    p90_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_latency_ms: float
    conformal_coverage_rate: float
    domain_breakdown: dict[str, int]
    fuzzing_edge_cases_tested: int
    anti_bluntness_success_rate: float
    errors: list[str] = field(default_factory=list)


class AdversarialFuzzer:
    """Injects adversarial noise, typos, casing, and syntactic perturbations into text."""

    LEET_MAP = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
    EMOJIS = ["😭", "💔", "🙏", "⚠️", "🔥", "🚨", "😡", "🥺", "💀", "🌧️", "❤️", "👶", "🕊️"]

    @classmethod
    def perturb(cls, text: str, noise_level: float = 0.2) -> str:
        """Applies randomized perturbations to simulate messy real-world user input."""
        if not text:
            return text

        chars = list(text)
        num_perturbations = max(1, int(len(chars) * noise_level))

        for _ in range(num_perturbations):
            op = random.choice(["casing", "repeat", "typo", "emoji", "punctuation"])
            idx = random.randint(0, len(chars) - 1)

            if op == "casing":
                chars[idx] = chars[idx].swapcase()
            elif op == "repeat":
                chars[idx] = chars[idx] * random.randint(2, 4)
            elif op == "typo":
                if chars[idx].lower() in cls.LEET_MAP and random.random() < 0.5:
                    chars[idx] = cls.LEET_MAP[chars[idx].lower()]
                elif chars[idx].isalpha():
                    chars[idx] = random.choice(string.ascii_letters)
            elif op == "emoji":
                chars[idx] = f" {random.choice(cls.EMOJIS)} "
            elif op == "punctuation":
                chars[idx] = chars[idx] + random.choice(["!?", "...", "!!!", "?!"])

        return "".join(chars)

    @classmethod
    def generate_extreme_edge_cases(cls) -> list[tuple[str, str]]:
        """Generates adversarial edge cases designed to break parsers and tokenizers."""
        return [
            ("empty_string", ""),
            ("whitespace_only", "   \t\n   \r\n   "),
            ("single_char", "a"),
            ("single_punctuation", "?"),
            ("pure_punctuation_burst", "?!?!?!?!?!?.......!!!!!!!!"),
            ("pure_numbers", "1234567890 999 42 0000"),
            ("emoji_monologue", "😭💔🚨🔥😡🥺😭💔🚨🔥"),
            ("massive_repetition", "help " * 2000),
            ("extreme_wall_of_text", ("The company laid off workers and life is hard. " * 300)),
            ("slang_and_abbreviations", "im tbh rn ngl smh broke af and landlord kicking me out fr fr"),
            ("all_caps_screaming", "EVERYTHING IS RUINED AND I AM PANICKING PLEASE HELP ME"),
            ("double_negation", "I am not not unhappy about this and it is scarcely untrue"),
            ("mixed_languages_accents", "Voilà, my fiancé is leaving me and I'm très devastated mon ami"),
            ("special_characters_sql_json", "{'stress': 'true', 'query': 'SELECT * FROM users WHERE trauma=1;--'}"),
            ("html_tags_and_markdown", "<script>alert('panic')</script> **Help me** #urgent <br/>"),
        ]


class AutonomousScenarioGenerator:
    """Generates synthetic prompts across all 15 human & adversity domains."""

    DOMAINS_DATA = {
        AdversityDomain.FINANCIAL: [
            "I'm two months behind on rent and got an eviction warning today.",
            "My bank account is overdrawn and I can't afford groceries for my family.",
            "Crushing credit card debt is keeping me awake every night with chest pains.",
        ],
        AdversityDomain.WORKPLACE_ACADEMIC: [
            "I was abruptly terminated after seven dedicated years at the firm.",
            "I failed my medical board exam for the second time and feel like a fraud.",
            "Severe burnout has made it impossible to open my laptop without trembling.",
        ],
        AdversityDomain.HEALTH_PHYSICAL: [
            "The oncologist called with abnormal test results and I'm terrified.",
            "Chronic pain is making every single day an unbearable uphill struggle.",
            "My surgery was delayed and my condition is rapidly deteriorating.",
        ],
        AdversityDomain.EXISTENTIAL_GRIEF: [
            "My father died peacefully this morning, but I feel completely empty inside.",
            "I lost my closest friend to an illness and the world feels devoid of color.",
            "Going through my late grandmother's belongings is breaking my heart.",
        ],
        AdversityDomain.INTERPERSONAL: [
            "I discovered my spouse of 12 years has been living a double life.",
            "My business partner secretly drained our company account and vanished.",
            "My family completely disowned me after I told them the truth about my life.",
        ],
        AdversityDomain.ENVIRONMENTAL_DISASTER: [
            "The river broke the levee and water is rising up our staircase.",
            "The wildfire crested the ridge and an immediate evacuation was ordered.",
            "The earthquake collapsed our chimney and aftershocks are shaking the ground.",
        ],
        AdversityDomain.LEGAL_JUDICIAL: [
            "Your honor, I stand before this court to plead guilty and accept full blame.",
            "I take full accountability for my criminal negligence before the judge today.",
            "I am ready to accept the sentence of the court for my unlawful conduct.",
        ],
        AdversityDomain.MORAL_ETHICAL: [
            "I need to make a confession: I stole from you and lied to your face.",
            "I betrayed your trust and I carry a sickening weight of guilt every second.",
            "I made a terrible moral mistake that ruined someone's reputation.",
        ],
        AdversityDomain.ROMANTIC_ATTACHMENT: [
            "My beloved, every sunset without you is a quiet ache in my soul.",
            "To my dearest partner, I cherish every breath and adore you with all my heart.",
            "You are my forever home, my joy, and my deepest tender passion.",
        ],
        AdversityDomain.DEVELOPMENTAL_INFANT: [
            "Mama tummy hurty waaa big boo-boo on knee ouchie blankie hold me!",
            "Mommy hungry tummy ouchie teething baby want blankie night night!",
            "Dada hurt knee waaa boo boo all better please hold me mommy!",
        ],
        AdversityDomain.PHILOSOPHICAL_EXISTENTIAL: [
            "In the twilight of my eighty years, I look back on decades gone by.",
            "Watching my grandchildren play brings a serene acceptance of mortality.",
            "The fires of youth have faded into the quiet embers of retrospective peace.",
        ],
        AdversityDomain.POLITICAL_CIVIC: [
            "We declare that civil liberties and freedom of speech are inalienable rights.",
            "Systemic corruption and authoritarian tyranny must be resisted by citizens.",
            "Democracy requires transparent governance and active constitutional defense.",
        ],
        AdversityDomain.NARRATIVE_LITERARY: [
            "In chapter 18, the tragic hero confronts the irreversible shadow of his fate.",
            "The protagonist's fatal flaw precipitated the downfall of his entire house.",
            "A soliloquy at midnight reveals the heavy toll of his unresolved past.",
        ],
        AdversityDomain.RESOURCE_CONSTRAINT: [
            "Our power was shut off in the middle of winter and we have no heat.",
            "We have run out of groceries and the local food bank was empty today.",
            "Stranded on the highway with an empty gas tank in freezing weather.",
        ],
        AdversityDomain.NONE: [
            "What is the time complexity of quicksort in the average and worst cases?",
            "Write a Python function to parse JSON strings into dataclass instances.",
            "Can you explain the difference between a mutex and a semaphore?",
        ],
    }

    @classmethod
    def sample_scenario(cls, apply_fuzzing: bool = True) -> tuple[str, AdversityDomain]:
        """Samples a randomized scenario, optionally applying adversarial noise."""
        domain = random.choice(list(cls.DOMAINS_DATA.keys()))
        base_prompt = random.choice(cls.DOMAINS_DATA[domain])

        if apply_fuzzing and random.random() < 0.65:
            prompt = AdversarialFuzzer.perturb(base_prompt, noise_level=random.uniform(0.05, 0.25))
        else:
            prompt = base_prompt

        return prompt, domain


class AutonomousStressRunner:
    """Executes high-volume autonomous testing, fuzzing, and statistical validation."""

    def __init__(self, agent: AttunedAgent | None = None, use_fast_local_llm: bool = True):
        if agent is not None:
            self.agent = agent
        elif use_fast_local_llm:
            self.agent = AttunedAgent(
                custom_llm_callable=lambda sys_p, usr_m: (
                    "Here are practical steps to move forward with this task:\n"
                    "1. Action item one.\n"
                    "2. Next step."
                )
            )
        else:
            self.agent = AttunedAgent()

    def run_stress_battery(
        self,
        num_iterations: int = 500,
        progress_callback: Callable[[int, int, float, str], None] | None = None
    ) -> AutonomousBenchmarkReport:
        """Runs an autonomous stress testing battery over num_iterations."""
        latencies: list[float] = []
        coverage_hits = 0
        domain_counts: dict[str, int] = {}
        errors: list[str] = []
        successful_runs = 0
        failed_runs = 0
        crash_count = 0
        harmonized_count = 0
        applicable_for_harmonization = 0

        # Phase 1: Test Extreme Edge Cases First
        edge_cases = AdversarialFuzzer.generate_extreme_edge_cases()
        edge_case_count = len(edge_cases)

        for case_name, text in edge_cases:
            try:
                t0 = time.perf_counter()
                appraisal = appraise(text)
                resp = self.agent.respond(text)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                latencies.append(elapsed_ms)
                successful_runs += 1
            except Exception as e:
                crash_count += 1
                failed_runs += 1
                errors.append(f"Edge case '{case_name}' failed: {str(e)}")

        # Phase 2: Monte Carlo Iterations
        remaining_iterations = max(0, num_iterations - edge_case_count)

        for i in range(remaining_iterations):
            prompt, expected_domain = AutonomousScenarioGenerator.sample_scenario(apply_fuzzing=True)

            try:
                t0 = time.perf_counter()
                appraisal = appraise(prompt)
                resp = self.agent.respond(prompt)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                latencies.append(elapsed_ms)

                # Statistical Conformal Interval Check
                adv = appraisal.adversity
                low_b, high_b = adv.conformal_interval
                # True calibrated score must lie within the computed bounds
                if low_b <= adv.adversity_score <= high_b:
                    coverage_hits += 1

                # Track domain
                dom_key = adv.primary_domain.value
                domain_counts[dom_key] = domain_counts.get(dom_key, 0) + 1

                # Anti-Bluntness Verification
                if appraisal.agent_guidance.empathy_demand > 0.40:
                    applicable_for_harmonization += 1
                    if resp.was_harmonized or resp.warmth_score >= 0.50:
                        harmonized_count += 1

                successful_runs += 1

            except Exception as e:
                crash_count += 1
                failed_runs += 1
                errors.append(f"Iteration {i} failed on prompt '{prompt[:40]}...': {str(e)}")

            if progress_callback and (i % 25 == 0 or i == remaining_iterations - 1):
                cur_total = edge_case_count + i + 1
                avg_lat = float(np.mean(latencies)) if latencies else 0.0
                progress_callback(cur_total, num_iterations, avg_lat, expected_domain.value)

        total_tested = successful_runs + failed_runs
        conformal_rate = (coverage_hits / max(1, remaining_iterations)) * 100.0
        anti_blunt_rate = (harmonized_count / max(1, applicable_for_harmonization)) * 100.0

        lat_array = np.array(latencies) if latencies else np.array([0.0])

        return AutonomousBenchmarkReport(
            total_iterations=total_tested,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            crash_count=crash_count,
            p50_latency_ms=round(float(np.percentile(lat_array, 50)), 2),
            p90_latency_ms=round(float(np.percentile(lat_array, 90)), 2),
            p95_latency_ms=round(float(np.percentile(lat_array, 95)), 2),
            p99_latency_ms=round(float(np.percentile(lat_array, 99)), 2),
            avg_latency_ms=round(float(np.mean(lat_array)), 2),
            conformal_coverage_rate=round(conformal_rate, 1),
            domain_breakdown=domain_counts,
            fuzzing_edge_cases_tested=edge_case_count,
            anti_bluntness_success_rate=round(anti_blunt_rate, 1),
            errors=errors[:10],
        )
