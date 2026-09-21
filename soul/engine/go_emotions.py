"""Google Research 27 GoEmotions Classifier & Feature Space.

Based on Demszky et al. (ACL 2020), 'GoEmotions: A Dataset of Fine-Grained Emotions'.
Implements fine-grained multi-label emotion distribution estimation.
"""

import math
import re
from soul.schemas.sentiment import GoEmotionsDistribution

GO_EMOTIONS_SEEDS: dict[str, list[str]] = {
    "admiration": ["admire", "legend", "brilliant", "genius", "incredible", "hero", "respect", "inspirational"],
    "amusement": ["haha", "funny", "hilarious", "laugh", "cracking up", "lol", "humor", "joke"],
    "anger": ["angry", "rage", "furious", "mad", "pissed", "outrage", "hate", "fuming"],
    "annoyance": ["annoyed", "irritated", "bothered", "aggravating", "nuisance", "sick of", "pesky"],
    "approval": ["agree", "good idea", "well done", "support", "approve", "solid", "kudos", "fair enough"],
    "caring": ["take care", "worried for you", "stay safe", "hugs", "sympathy", "thinking of you", "comfort"],
    "confusion": ["confused", "don't understand", "what do you mean", "lost", "perplexed", "makes no sense"],
    "curiosity": ["curious", "wonder", "why is", "how does", "interested to know", "intrigued"],
    "desire": ["want", "wish", "crave", "long for", "need", "yearn", "dream of", "hope to have"],
    "disappointment": ["disappointed", "let down", "bummer", "what a shame", "expected better", "underwhelming"],
    "disapproval": ["disapprove", "wrong", "should not", "terrible idea", "disagree", "unacceptable"],
    "disgust": ["disgusting", "gross", "nasty", "revolting", "vile", "repulsive", "sickening"],
    "embarrassment": ["embarrassed", "cringe", "awkward", "mortified", "humiliated", "blushing"],
    "excitement": ["excited", "can't wait", "hyped", "thrilled", "pumped", "looking forward", "stoked"],
    "fear": ["afraid", "scared", "terrified", "panic", "panicked", "dread", "frightened", "horror", "threatening"],
    "gratitude": ["thank you", "thanks", "grateful", "appreciate", "thankful", "indebted", "blessed"],
    "grief": ["grief", "mourning", "loss", "passed away", "died", "bereaved", "heartbroken", "rest in peace"],
    "joy": ["joy", "happy", "delight", "wonderful", "smile", "glad", "bliss", "overjoyed"],
    "love": ["love", "adore", "sweetheart", "cherish", "beloved", "affection", "in love"],
    "nervousness": ["nervous", "anxious", "jittery", "butterflies", "on edge", "uneasy", "tense"],
    "optimism": ["optimistic", "hopeful", "better days", "bright side", "silver lining", "positive outlook"],
    "pride": ["proud", "accomplished", "achievement", "honor", "pride", "did it", "nailed it"],
    "realization": ["realized", "just hit me", "turns out", "now i see", "eureka", "discovered", "clarity"],
    "relief": ["relieved", "relief", "weight off", "breathe again", "finally over", "dodged a bullet"],
    "remorse": ["sorry", "regret", "apologize", "my fault", "remorse", "forgive me", "guilty"],
    "sadness": ["sad", "depressed", "crying", "miserable", "sorrow", "gloomy", "unhappy", "down"],
    "surprise": ["surprised", "shocked", "unexpected", "astonished", "wow", "didn't expect", "stunned"],
}


class GoEmotionsAnalyzer:
    """Projects text into the 27 GoEmotions distribution space."""

    def analyze(self, text: str, valence: float = 0.0, arousal: float = 0.3) -> GoEmotionsDistribution:
        clean_text = text.lower()
        raw_scores: dict[str, float] = {}

        for emotion, seeds in GO_EMOTIONS_SEEDS.items():
            score = 0.0
            for seed in seeds:
                if " " in seed:
                    if seed in clean_text:
                        score += 1.5
                else:
                    if re.search(rf"\b{re.escape(seed)}\b", clean_text):
                        score += 1.2
            raw_scores[emotion] = score

        # Cross-modal heuristic adjustments based on Russell's VAD
        if valence < -0.4:
            raw_scores["sadness"] += abs(valence) * 1.0
            if arousal > 0.6:
                raw_scores["fear"] += abs(valence) * 1.2
                raw_scores["anger"] += abs(valence) * 0.8
        elif valence > 0.4:
            raw_scores["joy"] += valence * 1.0
            if arousal > 0.5:
                raw_scores["excitement"] += valence * 0.8

        # Softmax-like calibrated probabilities
        max_score = max(raw_scores.values()) if raw_scores else 0.0
        calibrated: dict[str, float] = {}

        if max_score > 0.0:
            # Temperature scaled exponential (sharp contrast for active emotions)
            exp_scores = {k: math.exp(v / 1.0) for k, v in raw_scores.items()}
            sum_exp = sum(exp_scores.values())
            for k in raw_scores:
                p = exp_scores[k] / sum_exp
                scaled_p = p * min(1.0, max_score * 0.8)
                calibrated[k] = round(float(min(1.0, max(0.0, scaled_p))), 4)
        else:
            for k in raw_scores:
                calibrated[k] = 0.0

        return GoEmotionsDistribution(**calibrated)
