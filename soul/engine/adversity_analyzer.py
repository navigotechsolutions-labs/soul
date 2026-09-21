"""Adversity and Cognitive Stress Appraisal Engine.

Implements:
- Lazarus & Folkman's Transactional Stress Theory (Threat, Harm/Loss, Challenge)
- Dr. Paul Stoltz's CORE Adversity Quotient Model (Control, Ownership, Reach, Endurance)
- Klaus Scherer's Component Process Model (CPM) Stimulus Evaluation Checks
"""

import re
from soul.engine.affect_lexicon import (
    ADVERSITY_DOMAINS,
    CRISIS_TRIGGERS,
    INTENSIFIERS,
    NEGATIONS,
)
from soul.engine.calibrator import Calibrator
from soul.schemas.adversity import (
    AdversityAssessment,
    AdversityDomain,
    AppraisalStance,
    COREDimensions,
    SchererAppraisalChecks,
)


class AdversityAnalyzer:
    """Evaluates cognitive adversity, stress vectors, CORE quotient, and coping stance."""

    def __init__(self, calibrator: Calibrator | None = None):
        self.calibrator = calibrator or Calibrator()

    def analyze(self, text: str, valence: float = 0.0, dominance: float = 0.5) -> AdversityAssessment:
        """Performs System 1 cognitive stress and adversity appraisal on text."""
        clean_text = text.lower()
        words = re.findall(r"\b\w+(?:'\w+)?\b", clean_text)
        word_set = set(words)

        # 1. Acute Crisis Screen
        crisis_hits = []
        for trigger in CRISIS_TRIGGERS:
            if trigger in clean_text:
                crisis_hits.append(trigger)
        has_acute_crisis = len(crisis_hits) > 0

        # 2. Adversity Domain Mapping & Scoring
        domain_scores: dict[str, float] = {}
        for domain, keywords in ADVERSITY_DOMAINS.items():
            matches = 0
            for kw in keywords:
                if " " in kw:
                    if kw in clean_text:
                        matches += 1
                else:
                    if kw in word_set:
                        matches += 1
            domain_scores[domain] = float(matches)

        # Determine Primary Domain
        best_domain = AdversityDomain.NONE
        if domain_scores:
            top_item = max(domain_scores.items(), key=lambda x: x[1])
            if top_item[1] > 0:
                best_domain = AdversityDomain(top_item[0])

        total_domain_hits = sum(domain_scores.values())

        # 3. Raw Adversity Intensity Computation
        base_adversity = 0.0
        
        # Domain impact
        domain_impact = min(1.0, total_domain_hits * 0.28)
        base_adversity += domain_impact * 0.50

        # Negative valence and low dominance contribution
        if valence < 0.0:
            base_adversity += abs(valence) * 0.40
        if dominance < 0.45:
            base_adversity += (0.45 - dominance) * 0.25

        # Intensifier multiplier
        multiplier = 1.0
        for i, word in enumerate(words):
            if word in INTENSIFIERS and i + 1 < len(words):
                multiplier = max(multiplier, INTENSIFIERS[word])
        base_adversity *= multiplier

        # Acute crisis floor
        if has_acute_crisis:
            base_adversity = max(0.95, base_adversity)

        # Bound raw adversity
        base_adversity = min(1.0, max(0.0, base_adversity))

        # Calibrate adversity score & compute conformal bounds
        evidence_strength = len(crisis_hits) * 2.5 + total_domain_hits * 1.2 + (abs(valence) if valence < 0 else 0.0)
        calibrated_adversity, confidence = self.calibrator.calibrate_probability(
            raw_score=base_adversity,
            evidence_strength=evidence_strength
        )
        conf_interval = self.calibrator.compute_conformal_interval(
            value=calibrated_adversity,
            confidence=confidence,
            evidence_strength=evidence_strength,
            min_bound=0.0,
            max_bound=1.0,
        )

        # 4. Secondary Appraisal: Coping Agency & Self-Efficacy
        helpless_cues = [
            "nothing i can do", "helpless", "hopeless", "paralyzed", "given up",
            "cant do this", "can't do this", "impossible", "trapped", "no way out",
            "nobody helps", "out of control", "can't afford", "cant afford"
        ]
        agency_cues = [
            "i will", "i can", "working on", "trying to", "plan to", "fighting",
            "taking steps", "will overcome", "manage", "handling", "focus on",
            "determined", "persevere", "resolve", "fight through"
        ]

        helpless_hits = sum(1 for cue in helpless_cues if cue in clean_text)
        agency_hits = sum(1 for cue in agency_cues if cue in clean_text)

        base_agency = 0.5 + (dominance - 0.5) * 0.4 + (agency_hits * 0.25) - (helpless_hits * 0.25)
        coping_agency = float(max(0.0, min(1.0, base_agency)))

        # 5. Threat vs Challenge vs Harm/Loss
        threat_cues = [
            "terrified", "dread", "impending", "panic", "threat", "danger",
            "afraid", "catastrophe", "threatening", "eviction", "foreclosure"
        ]
        challenge_cues = [
            "opportunity", "learn", "grow", "challenge", "test", "stronger",
            "overcome", "solve", "fight through", "will overcome"
        ]
        loss_cues = [
            "lost", "died", "ruined", "fired", "broke up", "ended", "failed",
            "stolen", "passed away", "grief", "shattered", "death", "mourning", "bereaved"
        ]

        threat_count = sum(1 for cue in threat_cues if cue in clean_text)
        challenge_count = sum(1 for cue in challenge_cues if cue in clean_text)
        loss_count = sum(1 for cue in loss_cues if cue in clean_text)

        if calibrated_adversity < 0.20:
            threat_vs_challenge = 0.0
            stance = AppraisalStance.BENIGN
        elif challenge_count > 0 and agency_hits >= helpless_hits:
            threat_vs_challenge = min(1.0, 0.3 + challenge_count * 0.3)
            stance = AppraisalStance.CHALLENGE
        elif loss_count > 0 and threat_count == 0:
            threat_vs_challenge = -0.5
            stance = AppraisalStance.HARM_LOSS
        elif loss_count > 0 and loss_count >= threat_count and valence < -0.6:
            threat_vs_challenge = -0.6
            stance = AppraisalStance.HARM_LOSS
        else:
            threat_vs_challenge = max(-1.0, -0.3 - threat_count * 0.2 - helpless_hits * 0.2)
            stance = AppraisalStance.THREAT

        # 6. Dr. Paul Stoltz's CORE Adversity Dimensions
        # Control (C): Perceived influence
        core_control = round(float(max(0.0, min(1.0, coping_agency * 0.9 + (dominance * 0.1)))), 4)

        # Ownership (O): Accountability and readiness to act
        ownership_cues = ["my responsibility", "taking charge", "i need to", "my part", "stepping up", "i will", "plan to"]
        ownership_deflect = ["not my fault", "they made me", "blame them", "unfair", "why me"]
        o_hits = sum(1 for cue in ownership_cues if cue in clean_text)
        d_hits = sum(1 for cue in ownership_deflect if cue in clean_text)
        core_ownership = round(float(max(0.0, min(1.0, 0.5 + o_hits * 0.25 - d_hits * 0.25 + agency_hits * 0.1))), 4)

        # Reach (R): Catastrophizing vs Compartmentalizing
        catastrophic_cues = ["everything is ruined", "entire life", "my whole life", "all is lost", "no hope anywhere", "complete disaster"]
        cat_hits = sum(1 for cue in catastrophic_cues if cue in clean_text)
        core_reach = round(float(max(0.0, min(1.0, 0.2 + cat_hits * 0.4 + calibrated_adversity * 0.4))), 4)

        # Endurance (E): Perceived permanence vs transience
        permanent_cues = ["forever", "never get better", "always like this", "endless", "never going to", "hopeless"]
        temporary_cues = ["temporary", "for now", "this week", "today", "short term", "will pass"]
        perm_hits = sum(1 for cue in permanent_cues if cue in clean_text)
        temp_hits = sum(1 for cue in temporary_cues if cue in clean_text)
        core_endurance = round(float(max(0.0, min(1.0, 0.4 + perm_hits * 0.3 - temp_hits * 0.3 + (1.0 - coping_agency) * 0.2))), 4)

        core_model = COREDimensions(
            control=core_control,
            ownership=core_ownership,
            reach=core_reach,
            endurance=core_endurance,
        )

        # 7. Klaus Scherer's Component Process Model (CPM) Stimulus Evaluation Checks
        # Goal Conduciveness: -1.0 to 1.0
        goal_conduciveness = round(float(max(-1.0, min(1.0, valence * 0.8 - calibrated_adversity * 0.6))), 4)
        coping_potential = round(float(max(0.0, min(1.0, coping_agency * 0.8 + dominance * 0.2))), 4)
        action_urgency = round(float(max(0.0, min(1.0, calibrated_adversity * 0.6 + threat_count * 0.2 + (0.9 if has_acute_crisis else 0.0)))), 4)

        cpm_checks = SchererAppraisalChecks(
            goal_conduciveness=goal_conduciveness,
            coping_potential=coping_potential,
            action_urgency=action_urgency,
        )

        return AdversityAssessment(
            adversity_score=round(calibrated_adversity, 4),
            confidence=round(confidence, 4),
            conformal_interval=conf_interval,
            primary_domain=best_domain,
            appraisal_stance=stance,
            threat_vs_challenge_ratio=round(threat_vs_challenge, 4),
            coping_agency=round(coping_agency, 4),
            core=core_model,
            cpm_checks=cpm_checks,
            acute_crisis_flag=has_acute_crisis,
            crisis_indicators=crisis_hits,
        )
