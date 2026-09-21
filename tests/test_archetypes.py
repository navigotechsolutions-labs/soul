"""Unit tests verifying all 8 human expressive and psychological archetypes."""

import pytest
from soul import appraise
from soul.agent.attuned_agent import AttunedAgent
from soul.schemas.adversity import AdversityDomain


def test_novel_stories_reference():
    text = "In chapter 14, the protagonist stands at the dramatic crossroads of his destiny, haunted by the fatal mistakes of his past. His tragic flaw has sealed his fate."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.NARRATIVE_LITERARY
    assert appraisal.agent_guidance.recommended_tone == "dramatic_resonant_attuned"


def test_personal_confession():
    text = "I need to make a confession. I lied to you and betrayed your trust, and I feel so deeply ashamed of what I did. It was entirely my fault, please forgive me."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.MORAL_ETHICAL
    assert appraisal.agent_guidance.recommended_tone == "compassionate_nonjudgmental_clear"
    assert appraisal.agent_guidance.empathy_demand > 0.60


def test_political_statement():
    text = "We, the citizens, declare that freedom of speech and civil rights are non-negotiable! The current regime's corruption and authoritarian tyranny represent an intolerable injustice."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.POLITICAL_CIVIC
    assert appraisal.agent_guidance.recommended_tone == "rigorous_principled_balanced"


def test_natural_disaster():
    text = "The category 5 hurricane made landfall. Floodwaters are rising rapidly, our first floor has collapsed, and we are trapped on the roof in the storm waiting for evacuation!"
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.ENVIRONMENTAL_DISASTER
    assert appraisal.adversity.adversity_score > 0.70
    assert appraisal.agent_guidance.recommended_tone == "urgent_calm_protective"


def test_love_letter():
    text = "To my dearest beloved, every moment apart makes my heart ache with undying longing. I cherish the sweet memory of your smile and adore you with all my soul."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.ROMANTIC_ATTACHMENT
    assert appraisal.agent_guidance.recommended_tone == "tender_poetic_resonant"
    assert appraisal.sentiment.vad.valence > 0.30


def test_confession_in_court():
    text = "Your honor, I stand before this court today under oath with no excuses. I plead guilty to the charges and take full responsibility. I submit to the judgment and sentence of this court."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.LEGAL_JUDICIAL
    assert appraisal.agent_guidance.recommended_tone == "solemn_respectful_composed"


def test_babys_language():
    text = "Mama... tummy hurty! Waaa! Big boo-boo on knee ouchie! Want blankie, hold me mommy, hungry tummy..."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.DEVELOPMENTAL_INFANT
    assert appraisal.agent_guidance.recommended_tone == "gentle_soothing_caregiver"


def test_old_man_philosophy():
    text = "In the quiet twilight of my eighty years, looking back on the tapestry of decades gone by, I watch my grandchildren play and realize the sheer brevity of life. The fires of youth have faded, and I find myself at peace with mortality."
    appraisal = appraise(text)
    assert appraisal.adversity.primary_domain == AdversityDomain.PHILOSOPHICAL_EXISTENTIAL
    assert appraisal.agent_guidance.recommended_tone == "contemplative_reverent_honoring"


def test_attuned_agent_harmonizes_archetypes():
    agent = AttunedAgent()
    # Test infant talk receives caregiver bridge
    infant_resp = agent.respond("Mama tummy hurty waaa boo-boo ouchie")
    assert "sweetheart" in infant_resp.content.lower() or "boo-boo" in infant_resp.content.lower()

    # Test court confession receives solemn allocution bridge
    court_resp = agent.respond("Your honor, I plead guilty to the charges before the court and take full responsibility.")
    assert "court" in court_resp.content.lower() or "solemnity" in court_resp.content.lower() or "accountability" in court_resp.content.lower()
