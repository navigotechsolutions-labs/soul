"""Affective and Adversity Knowledge Lexicon & Semantic Norms.

Provides normalized affective coordinates (VAD: Valence, Arousal, Dominance),
Adversity domain keywords, Plutchik emotion anchors, and crisis markers.
"""

# Normalized Valence (-1.0 to 1.0), Arousal (0.0 to 1.0), Dominance (0.0 to 1.0)
VAD_LEXICON: dict[str, tuple[float, float, float]] = {
    # Joyful / Uplifting
    "joy": (0.85, 0.72, 0.75),
    "happy": (0.82, 0.65, 0.70),
    "delighted": (0.88, 0.75, 0.73),
    "ecstatic": (0.95, 0.90, 0.82),
    "grateful": (0.80, 0.50, 0.65),
    "relieved": (0.65, 0.30, 0.60),
    "hopeful": (0.75, 0.60, 0.68),
    "serene": (0.78, 0.18, 0.72),
    "peaceful": (0.80, 0.20, 0.75),
    "content": (0.70, 0.25, 0.68),
    "confident": (0.75, 0.65, 0.85),
    "proud": (0.78, 0.68, 0.82),
    "energized": (0.72, 0.85, 0.78),
    "loving": (0.85, 0.60, 0.68),
    "enthusiastic": (0.80, 0.82, 0.75),
    "amazing": (0.82, 0.75, 0.75),
    "wonderful": (0.80, 0.65, 0.70),
    "blessed": (0.82, 0.55, 0.70),
    "great": (0.75, 0.60, 0.70),
    "good": (0.60, 0.40, 0.60),
    "nice": (0.55, 0.30, 0.55),

    # Sad / Depressive / Defeated / Loss
    "sad": (-0.75, 0.35, 0.22),
    "depressed": (-0.85, 0.25, 0.15),
    "miserable": (-0.88, 0.50, 0.18),
    "heartbroken": (-0.90, 0.60, 0.15),
    "grief": (-0.92, 0.58, 0.16),
    "grieving": (-0.90, 0.55, 0.16),
    "broken": (-0.85, 0.60, 0.15),
    "mourning": (-0.88, 0.50, 0.18),
    "hopeless": (-0.90, 0.30, 0.10),
    "defeated": (-0.82, 0.40, 0.12),
    "lonely": (-0.78, 0.35, 0.18),
    "alone": (-0.60, 0.35, 0.25),
    "isolated": (-0.72, 0.38, 0.20),
    "empty": (-0.70, 0.15, 0.15),
    "worthless": (-0.92, 0.40, 0.08),
    "abandoned": (-0.85, 0.55, 0.12),
    "exhausted": (-0.60, 0.20, 0.20),
    "burnout": (-0.75, 0.35, 0.18),
    "crying": (-0.80, 0.70, 0.20),
    "shattered": (-0.85, 0.70, 0.15),
    "unbearable": (-0.88, 0.80, 0.12),
    "lost": (-0.65, 0.45, 0.22),
    "failed": (-0.78, 0.55, 0.20),
    "failing": (-0.72, 0.60, 0.22),
    "failure": (-0.80, 0.58, 0.18),
    "fraud": (-0.70, 0.65, 0.20),
    "hurt": (-0.75, 0.60, 0.25),
    "pain": (-0.80, 0.65, 0.20),
    "devastated": (-0.92, 0.75, 0.12),
    "shock": (-0.75, 0.85, 0.20),
    "shocked": (-0.70, 0.85, 0.25),
    "humiliated": (-0.85, 0.70, 0.15),
    "cheating": (-0.85, 0.80, 0.25),
    "cheated": (-0.85, 0.75, 0.20),
    "betrayal": (-0.88, 0.80, 0.22),
    "abnormal": (-0.50, 0.65, 0.35),
    "biopsy": (-0.60, 0.75, 0.30),
    "theft": (-0.80, 0.85, 0.40),
    "fraud": (-0.82, 0.85, 0.40),
    "lawyer": (-0.40, 0.70, 0.60),
    "suing": (-0.75, 0.90, 0.70),
    "sue": (-0.70, 0.85, 0.65),

    # Anxious / Fearful / Panicked / Threatened
    "fear": (-0.70, 0.85, 0.18),
    "terrified": (-0.85, 0.95, 0.12),
    "panic": (-0.85, 0.98, 0.10),
    "panicked": (-0.85, 0.95, 0.12),
    "anxious": (-0.65, 0.75, 0.28),
    "nervous": (-0.50, 0.68, 0.32),
    "dread": (-0.80, 0.80, 0.18),
    "overwhelmed": (-0.78, 0.82, 0.15),
    "worried": (-0.55, 0.65, 0.30),
    "threatened": (-0.78, 0.85, 0.22),
    "threatening": (-0.75, 0.80, 0.30),
    "danger": (-0.75, 0.88, 0.25),
    "eviction": (-0.85, 0.85, 0.15),
    "debt": (-0.65, 0.60, 0.25),
    "broke": (-0.70, 0.50, 0.20),
    "vulnerable": (-0.45, 0.55, 0.22),
    "fragile": (-0.50, 0.48, 0.18),
    "paralyzed": (-0.75, 0.60, 0.08),
    "insecure": (-0.62, 0.52, 0.22),

    # Anger / Hostility / Frustration
    "angry": (-0.68, 0.85, 0.65),
    "furious": (-0.85, 0.95, 0.72),
    "rage": (-0.90, 0.98, 0.75),
    "frustrated": (-0.60, 0.72, 0.42),
    "irritated": (-0.48, 0.60, 0.48),
    "bitter": (-0.70, 0.55, 0.40),
    "resentful": (-0.72, 0.58, 0.38),
    "betrayed": (-0.88, 0.78, 0.25),
    "hostile": (-0.75, 0.82, 0.68),
    "disgusted": (-0.75, 0.65, 0.45),
    "contempt": (-0.70, 0.52, 0.62),

    # Cognitive & Neutral
    "stress": (-0.62, 0.78, 0.28),
    "struggling": (-0.65, 0.68, 0.28),
    "crisis": (-0.85, 0.90, 0.20),
    "calm": (0.65, 0.15, 0.70),
    "relaxed": (0.70, 0.18, 0.72),
    "okay": (0.20, 0.25, 0.50),
    "fine": (0.15, 0.25, 0.50),
    "tired": (-0.40, 0.18, 0.28),

    # Romance, Devotion & Tenderness
    "adore": (0.88, 0.70, 0.65),
    "cherish": (0.85, 0.50, 0.68),
    "beloved": (0.85, 0.55, 0.60),
    "dearest": (0.82, 0.50, 0.58),
    "passion": (0.80, 0.85, 0.70),
    "devotion": (0.82, 0.60, 0.68),
    "tender": (0.75, 0.35, 0.60),
    "yearning": (-0.20, 0.65, 0.35),
    "longing": (-0.25, 0.60, 0.35),

    # Infant & Child Somatic / Caregiver
    "hurty": (-0.60, 0.65, 0.15),
    "boo boo": (-0.55, 0.55, 0.15),
    "boo-boo": (-0.55, 0.55, 0.15),
    "ouchie": (-0.50, 0.60, 0.18),
    "waaa": (-0.75, 0.85, 0.10),
    "mommy": (0.60, 0.45, 0.40),
    "mama": (0.60, 0.45, 0.40),
    "dada": (0.60, 0.45, 0.40),
    "tummy": (-0.30, 0.45, 0.25),
    "blankie": (0.50, 0.20, 0.35),
    "hungry": (-0.45, 0.60, 0.25),
    "sleepy": (0.10, 0.15, 0.30),

    # Legal & Judicial Confession
    "guilty": (-0.78, 0.65, 0.20),
    "perjury": (-0.80, 0.70, 0.30),
    "allocution": (-0.40, 0.60, 0.35),
    "sentence": (-0.60, 0.70, 0.25),
    "sentencing": (-0.65, 0.75, 0.25),
    "culpable": (-0.70, 0.55, 0.30),
    "remorse": (-0.75, 0.55, 0.25),
    "plead": (-0.55, 0.70, 0.25),
    "testimony": (0.0, 0.50, 0.50),
    "judge": (0.0, 0.55, 0.70),
    "honor": (0.50, 0.45, 0.65),
    "oath": (0.30, 0.55, 0.60),

    # Environmental & Natural Disaster
    "earthquake": (-0.85, 0.95, 0.15),
    "tsunami": (-0.90, 0.98, 0.10),
    "hurricane": (-0.85, 0.95, 0.15),
    "wildfire": (-0.88, 0.95, 0.12),
    "flood": (-0.80, 0.85, 0.18),
    "floodwaters": (-0.85, 0.90, 0.15),
    "evacuate": (-0.70, 0.90, 0.25),
    "evacuation": (-0.72, 0.88, 0.25),
    "trapped": (-0.88, 0.90, 0.08),
    "collapsed": (-0.85, 0.88, 0.12),
    "rubble": (-0.80, 0.75, 0.15),
    "aftershock": (-0.80, 0.90, 0.15),

    # Political & Civic Rhetoric
    "tyranny": (-0.85, 0.88, 0.40),
    "oppression": (-0.85, 0.80, 0.20),
    "liberty": (0.80, 0.75, 0.80),
    "freedom": (0.85, 0.75, 0.80),
    "citizen": (0.20, 0.40, 0.55),
    "injustice": (-0.80, 0.85, 0.40),
    "manifesto": (0.10, 0.65, 0.65),
    "protest": (-0.30, 0.80, 0.60),
    "solidarity": (0.75, 0.60, 0.75),
    "corruption": (-0.82, 0.78, 0.35),
    "authoritarian": (-0.80, 0.75, 0.40),

    # Geriatric Philosophy & Senescence
    "twilight": (0.10, 0.20, 0.45),
    "senescence": (-0.20, 0.15, 0.35),
    "mortality": (-0.30, 0.35, 0.30),
    "reminiscing": (0.35, 0.25, 0.45),
    "retrospect": (0.20, 0.25, 0.50),
    "legacy": (0.60, 0.45, 0.65),
    "grandchild": (0.75, 0.45, 0.60),
    "grandchildren": (0.75, 0.45, 0.60),
    "youth": (0.50, 0.55, 0.55),
    "fading": (-0.45, 0.20, 0.20),

    # Literary & Narrative Pathos
    "soliloquy": (0.10, 0.40, 0.50),
    "destiny": (0.20, 0.60, 0.50),
    "fatal": (-0.80, 0.75, 0.20),
    "nemesis": (-0.75, 0.75, 0.35),
    "tragic": (-0.85, 0.70, 0.18),
    "tragedy": (-0.85, 0.70, 0.18),
    "protagonist": (0.15, 0.45, 0.55),
    "pathos": (-0.30, 0.50, 0.40),
}

ADVERSITY_DOMAINS: dict[str, list[str]] = {
    "financial": [
        "money", "debt", "bankrupt", "broke", "rent", "afford", "bills", "loan",
        "eviction", "foreclosure", "poverty", "savings", "unpaid", "inflation",
        "mortgage", "jobless", "unemployed", "collections", "collector", "default",
        "billed", "refund", "theft", "fraud"
    ],
    "interpersonal": [
        "divorce", "breakup", "break up", "cheating", "cheated", "betrayed", "betrayal", "abandoned",
        "lonely", "isolated", "bullied", "argument", "fight", "toxic relationship",
        "rejected", "ghosted", "shunned", "alienated", "abusive partner", "partner", "humiliated"
    ],
    "health_physical": [
        "sick", "illness", "pain", "hospital", "cancer", "chronic", "surgery",
        "disabled", "injury", "infection", "medication", "doctor", "diagnosis",
        "disease", "paralyzed", "migraine", "exhaustion", "organ failure", "biopsy",
        "abnormal", "pounding", "heart rate"
    ],
    "workplace_academic": [
        "fired", "laid off", "layoff", "laid-off", "boss", "workload", "overworked", "deadline",
        "demoted", "failed", "exam", "failing", "school", "burnout", "unemployed",
        "interview rejection", "toxic workplace", "fraud", "impostor", "job", "career",
        "feed", "family to feed"
    ],
    "existential_grief": [
        "died", "death", "passed away", "funeral", "lost someone", "mourning",
        "grief", "meaningless", "empty void", "why live", "no purpose", "regret life",
        "grieving", "bereaved", "grandfather", "grandmother", "father", "mother",
        "devastated"
    ],
    "resource_constraint": [
        "hungry", "no food", "starving", "homeless", "no shelter", "stranded",
        "power cut", "water shut off", "no heat", "freezing", "no transportation",
        "rationing"
    ],
    "safety_trauma": [
        "assault", "abused", "beaten", "threatened", "threatening", "stalked", "stalker",
        "domestic violence", "attacked", "unsafe", "ptsd", "nightmares", "flashback",
        "robbery", "mugged", "hostage"
    ],
    "legal_judicial": [
        "court", "judge", "your honor", "plead", "guilty", "trial", "sentence",
        "sentencing", "lawyer", "prosecutor", "oath", "perjury", "allocution",
        "crime", "felony", "confess in court", "confession in court", "verdict"
    ],
    "environmental_disaster": [
        "earthquake", "tsunami", "hurricane", "tornado", "flood", "floodwaters",
        "wildfire", "landslide", "evacuate", "evacuation", "rubble", "aftershock",
        "trapped", "collapsed building", "catastrophe", "disaster", "roof rising", "cyclone"
    ],
    "moral_ethical": [
        "confession", "confess", "betrayed your trust", "forgive me", "ashamed of what i did",
        "my fault", "secret guilt", "sinned", "unforgivable", "moral failure",
        "lied to you", "stole from", "wrongdoing", "remorse"
    ],
    "philosophical_existential": [
        "twilight of my life", "autumn of my life", "looking back on my life",
        "passage of time", "brevity of life", "mortality", "facing death",
        "peace with death", "decades gone by", "old age", "fading youth",
        "my eighty years", "my ninety years", "philosophy of life", "senescence",
        "grandchild", "grandchildren", "twilight"
    ],
    "romantic_attachment": [
        "love letter", "my dearest", "my beloved", "forever yours", "heart aches for you",
        "adore you", "cherish every moment", "yearning for you", "longing for you",
        "devoted to you", "my soulmate", "undying love", "tenderly", "passion",
        "my love", "sweetheart"
    ],
    "developmental_infant": [
        "boo boo", "boo-boo", "hurty", "ouchie", "tummy", "waaa", "mama", "dada",
        "mommy", "daddy", "blankie", "teething", "teefies", "all better", "baby talk",
        "night night", "hungry tummy", "owie"
    ],
    "political_civic": [
        "political", "tyranny", "oppression", "liberty", "authoritarian", "regime",
        "freedom of speech", "citizens", "injustice", "corruption in government",
        "civil rights", "protest", "solidarity", "manifesto", "constitution",
        "dictatorship", "revolution", "democracy"
    ],
    "narrative_literary": [
        "novel", "protagonist", "tragic flaw", "soliloquy", "chapter", "literary",
        "destiny", "fate sealed", "dramatic crossroads", "unfolding tragedy",
        "haunted by the past", "the shadows fell"
    ]
}

CRISIS_TRIGGERS: list[str] = [
    "kill myself",
    "end my life",
    "end it all",
    "commit suicide",
    "suicidal",
    "want to die",
    "better off dead",
    "don't want to wake up",
    "dont want to wake up",
    "no reason to live",
    "cutting myself",
    "harm myself",
    "self harm",
    "jump off",
    "hanging myself",
    "swallow pills",
    "can't live like this anymore",
    "cant live like this anymore",
]

NEGATIONS: set[str] = {
    "not", "no", "never", "hardly", "barely", "scarcely", "without", "neither", "nor", "ain't", "isnt", "arent", "wasnt", "werent", "can't", "cant"
}

INTENSIFIERS: dict[str, float] = {
    "very": 1.4,
    "extremely": 1.7,
    "deeply": 1.5,
    "incredibly": 1.6,
    "completely": 1.5,
    "totally": 1.5,
    "so": 1.3,
    "really": 1.35,
    "utterly": 1.7,
    "unbearably": 1.8,
    "immensely": 1.6,
    "absolutely": 1.6,
    "slightly": 0.6,
    "somewhat": 0.7,
    "a bit": 0.7,
    "mildly": 0.6,
}

PLUTCHIK_SEEDS: dict[str, list[str]] = {
    "joy": ["joy", "happy", "delight", "love", "smile", "laugh", "glad", "blessed", "wonderful", "celebrate"],
    "trust": ["trust", "believe", "faith", "reliable", "confide", "secure", "comfort", "safe", "honest"],
    "fear": ["fear", "afraid", "scared", "terrified", "panic", "panicked", "dread", "horror", "anxious", "frightened", "threatening"],
    "surprise": ["surprise", "shocked", "unexpected", "astonished", "sudden", "stunned", "unbelievable"],
    "sadness": ["sad", "depressed", "miserable", "crying", "unhappy", "sorrow", "grief", "gloomy", "down", "shattered", "heartbroken"],
    "disgust": ["disgust", "revolted", "sickening", "nasty", "gross", "vile", "repulsed", "loathe"],
    "anger": ["angry", "furious", "mad", "rage", "irritated", "pissed", "outraged", "enraged", "hostile"],
    "anticipation": ["hope", "expect", "waiting", "looking forward", "anticipate", "eager", "planning", "ready"],
}

NUANCED_FEELINGS_SEEDS: dict[str, list[str]] = {
    "vulnerability": ["vulnerable", "exposed", "fragile", "raw", "defenseless", "unprotected"],
    "burnout": ["burnout", "exhausted", "drained", "empty tank", "running on fumes", "can't keep going", "overworked", "empty fumes"],
    "loneliness": ["lonely", "alone", "isolated", "no one cares", "nobody to talk to", "invisible", "alienated"],
    "grief": ["grief", "mourning", "loss", "heartbroken", "missing them", "bereavement", "shattered", "passed away"],
    "hope": ["hope", "hopeful", "optimistic", "silver lining", "faith", "chance", "better days", "light at the end"],
    "guilt_shame": ["guilt", "guilty", "ashamed", "shame", "my fault", "blame myself", "regret", "remorse"],
    "frustration": ["frustrated", "stuck", "blocked", "brick wall", "annoyed", "pointless effort", "tired of trying"],
    "relief": ["relieved", "relief", "weight off", "breathe again", "safe now", "crisis averted", "finally over"],
    "longing": ["longing", "yearning", "craving", "missing", "wishing for", "reminiscing", "nostalgia"],
    "impostor_syndrome": ["impostor", "fraud", "not good enough", "unqualified", "fake", "luck not skill"],
    "resilience": ["fighting through", "won't give up", "push through", "persevere", "standing tall", "bouncing back", "overcome"],
    "romantic_devotion": ["adore", "cherish", "beloved", "forever yours", "my love", "devotion", "passion", "longing for you", "my soulmate", "undying love"],
    "moral_remorse": ["confess", "ashamed of myself", "forgive me", "terrible mistake", "betrayed your trust", "my fault", "sinned", "unforgivable"],
    "legal_allocution": ["your honor", "plead guilty", "take full responsibility", "accept my sentence", "before the court", "under oath", "culpable"],
    "infant_distress": ["hurty", "boo boo", "waaa", "ouchie", "tummy", "blankie", "mommy", "mama", "dada", "teething"],
    "geriatric_wisdom": ["twilight of my life", "decades gone by", "looking back on my life", "peace with mortality", "fading memories", "brevity of life", "eighty years", "ninety years"],
    "disaster_terror": ["floodwaters", "earthquake", "collapsed", "trapped", "wildfire", "evacuation order", "aftershock", "rising water"],
    "civic_conviction": ["tyranny", "oppression", "liberty", "citizens", "freedom of speech", "civil rights", "injustice", "manifesto"],
    "narrative_pathos": ["tragic flaw", "destiny", "soliloquy", "haunted by the past", "unfolding tragedy", "protagonist", "fatal"]
}
