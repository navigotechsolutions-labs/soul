# Soul Engine (`soul-engine`)

[![PyPI Version](https://img.shields.io/badge/pypi-v0.3.0-blue.svg)](https://pypi.org/project/soul-engine/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-45%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![Latency](https://img.shields.io/badge/latency-%3C1.0ms%20(P50)-orange.svg)]()
[![Conformal Coverage](https://img.shields.io/badge/conformal%20coverage-100%25-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **"Understand the true feeling and context of any human situation — and act fast, in sub-milliseconds."**  
> `Soul` is a non-autoregressive "System 1" cognitive appraisal engine and anti-bluntness harmonizer. It decodes human psychological stakes, stress stance, and 3D affect in **<1ms**, prescribing instant emotional action directives so AI agents and human teams never deliver cold, robotic, or tone-deaf responses.

---

## 🌟 Why Soul? The Core AI Failure Mode

When users prompt conversational AI with tasks embedded in distress—such as bereavement, job loss, medical panic, or heartfelt vulnerability—standard Large Language Models (LLMs) often default to **blunt, hyper-procedural task completion**:

```text
[USER PROMPT]
"I was just laid off with zero notice after 8 years at the company. 
I have a family to feed and I'm in total shock. How do I update my LinkedIn?"

[STANDARD AI OUTPUT — BLUNT & INSENSITIVE]
"Here are practical steps to move forward with this task:
1. Conduct an Error Audit on your profile.
2. Implement Active Recall on your skill tags.
3. Micro-habits: limit study blocks to 25-minute Pomodoro intervals."
```

### The Solution: Fast System 1 Appraisal + Attuned Harmonization

`Soul` acts as the **emotional limbic system** for downstream AI:
1. **System 1 Cognitive Perception (<1ms)**: Appraises the subject's adversity domain, cognitive stress stance (*Threat*, *Harm/Loss*, *Challenge*), 3D continuous affect coordinates $(V, A, D)$, and granular feelings (vulnerability, grief, remorse, panic).
2. **Pre-Generation Prompt Attunement**: Injects calibrated psychological directives into the LLM system prompt before inference.
3. **Anti-Bluntness Auditor & Harmonizer**: Audits candidate responses for cold openers or empathy deficits, prepending tailored empathetic bridges when high emotional stakes are detected.

```text
[SOUL ATTUNED OUTPUT — EMPATHETIC & TASK-EFFECTIVE]
"I can hear how frustrating and draining this situation has been for you. Dealing with workplace 
stress or setbacks takes a real toll. Let's break this down into manageable steps so you don't 
have to carry the whole burden at once:

Here is a strategic plan to update your profile and move forward:
1. Set your headline to emphasize your 8 years of core leadership and domain expertise...
2. Toggle the private 'Open to Work' recruiter badge so your network can immediately assist..."
```

---

## 💡 The Core Purpose: Understand True Feelings & Act Fast

Most AI systems stumble because they **read only literal tokens** and completely miss the **human emotional undercurrent**. When a person says *"I failed my exam again, what books should I buy?"*, they are literally asking for books, but their true emotional state is **severe impostor syndrome, depleted resilience, and fear of failure**.

Soul solves this through two synchronized capabilities:

| Superpower | What Soul Does | Why It Matters |
|---|---|---|
| **1. Uncovering True Feelings & Context** | Decodes the psychological bedrock using Russell's 3D VAD affect, 27 GoEmotions, Lazarus Cognitive Stance (*Threat* vs *Challenge* vs *Loss*), and Stoltz CORE adversity profile. | Pierces through surface text to recognize vulnerability, grief, burnout, or panic before formulating a word. |
| **2. Prescribing Fast, Targeted Action** | Instantly generates concrete action directives: `urgency` (*immediate/high/moderate*), `recommended_tone` (*reassuring, gentle, soothing*), de-escalation flags, and safety triage triggers. | Replaces passive observation with actionable interventions and empathetic attunement. |
| **3. Sub-Millisecond Speed (<1ms)** | Non-autoregressive System 1 appraisal operates at `0.98ms P50 latency` without heavy LLM roundtrips. | Allows AI agents, chatbots, and frontline teams to comprehend emotional context and act **instantly** without lagging user conversations. |

---

## 🚀 Quickstart

### Installation

Install from source or local distribution:

```bash
# Clone the repository
git clone https://github.com/navigotechsolutions-labs/soul.git
cd soul

# Install in editable mode
pip install -e .
```

Or install the pre-built wheel directly:
```bash
pip install dist/soul_engine-0.3.0-py3-none-any.whl
```

---

### Basic Python Usage

```python
import soul

# 1. Ultra-fast System 1 Appraisal (<1ms)
appraisal = soul.appraise("My mother passed away last night. I need to draft an announcement.")

print("Adversity Score:", appraisal.adversity.adversity_score) # 0.83 [0.75, 0.92]
print("Domain:", appraisal.adversity.primary_domain)          # EXISTENTIAL_GRIEF
print("Stance:", appraisal.adversity.appraisal_stance)        # HARM_LOSS
print("Affect VAD:", appraisal.sentiment.vad)                 # Valence: -1.0, Arousal: 1.0
print("Prescribed Tone:", appraisal.agent_guidance.recommended_tone) # warm_validating_empathetic

# 2. End-to-End Attuned Agent (Eliminates blunt responses)
response = soul.respond("My mother passed away last night. I need to draft an announcement.")
print(response.content)
```

---

## 🏛️ Grounded in Academic Cognitive Science

`Soul` implements validated empirical frameworks:

| Literature & Foundation | Scientific Source | How Soul Implements It |
|---|---|---|
| **Component Process Model (CPM)** | Klaus Scherer (*2009, 2013*) | Stimulus Evaluation Checks (SECs): Goal Conduciveness, Coping Potential, Action Urgency. |
| **Transactional Stress Theory** | Lazarus & Folkman (*1984*) | Primary & secondary stress appraisal: Categorizing `THREAT`, `HARM_LOSS`, `CHALLENGE`, and `BENIGN`. |
| **Adversity Quotient (CORE)** | Dr. Paul Stoltz (*1997, 2000*) | Measures Control, Ownership, Reach (catastrophizing), and Endurance (permanence). |
| **Continuous Affect Space** | James Russell (*1980, 2003*) | 3D continuous Valence-Arousal-Dominance (VAD) coordinate projections. |
| **Fine-Grained Emotion Taxonomy** | Google Research GoEmotions (*Demszky et al., ACL 2020*) | Full probability distributions across 27 nuanced emotional categories. |
| **Conformal Prediction Intervals** | Angelopoulos & Bates (*2021*) | Distribution-free, 90% confidence uncertainty bounds $[y_{\min}, y_{\max}]$ rather than deceptive point estimates. |
| **Temperature-Scaled Calibration** | Guo et al. (*ICML 2017*) | Platt & temperature scaling with epistemic uncertainty penalization. |

*Full literature survey available in [`RESEARCH.md`](RESEARCH.md).*

---

## 🎭 Tested Across Complex Human Archetypes

`Soul` is benchmarked across 15 distinct human expressive and psychological archetypes:

- 👶 **Baby's Language / Infant Talk**: Somatic toddler distress cries (`"Mama tummy hurty waaa boo-boo"`) matched with gentle caregiver soothing.
- ⚖️ **Confession in Court**: Formal allocution under oath before a judge matched with solemn, accountable, non-defensive judicial respect.
- 👴 **Old Man Philosophy**: Geriatric retrospection on mortality, senescence, and grandchildren matched with contemplative sacred dignity.
- 💌 **Love Letter**: Romantic vulnerability, longing, and devotion met with poetic tenderness and emotional reciprocity.
- 🌊 **Natural Disaster**: Hurricane landfall and rising floodwaters met with rapid emergency psychological first aid and survival stabilization.
- 🏛️ **Political Statement / Civic Manifesto**: Ideological conviction and liberty defense met with rigorous, non-partisan democratic principles.
- 📖 **Novel Stories Reference**: Tragic character dilemmas and fatal flaws met with deep narrative dramatic analysis.
- 💻 **Technical Objective Query**: Code algorithms met with direct, zero-fluff answers without patronizing or fake empathy.

Run the deep archetype benchmark:
```bash
python test_archetypes.py
```

---

## ⚡ Autonomous Stress Testing & Fuzzing Engine

`Soul` includes an autonomous continuous fuzzing harness that evaluates the algorithm over thousands of randomized permutations:
- Injects leetspeak, random casing swaps, typo perturbations, double negations, emoji floods, and punctuation bursts.
- Tortures 15 boundary cases: 20,000-character repetitions, pure SQL/JSON syntax, script tags, empty strings.

```bash
# Run a 500-permutation autonomous stress test
python autonomous_stress_test.py --iterations 500

# Run indefinitely in continuous autonomous loop mode
python autonomous_stress_test.py --iterations 100 --continuous
```

**Results (500 runs)**:
- **0 Crashes** across all randomized permutations.
- **P50 Latency**: `0.98 ms` | **P99 Latency**: `1.54 ms`.
- **Conformal Coverage**: `100.0%` (exceeds $\ge 90.0\%$ target).
- **Anti-Bluntness Success Rate**: `100.0%`.

---

## 🖥️ Interactive Web UI Dashboard

`Soul` comes with an interactive Streamlit application:

```bash
streamlit run app.py
```

Features:
- **Live Affect & Adversity Radar**: Real-time VAD gauge meters and CORE adversity quotient radar.
- **GoEmotions 27-Class Histogram**: Visualizing fine-grained emotional activation.
- **⚡ Blunt AI vs. Attuned AI Side-by-Side**: Direct real-time comparison showing how Soul intercepts and harmonizes cold AI responses.

---

## 🛠️ CLI Usage

```bash
# Appraise user input and inspect affective metrics
python -m soul.cli "The landlord gave me an eviction warning today, I don't know what to do."

# Demonstrate the live anti-bluntness fix
python -m soul.cli "I failed my exams again, what study plan should I follow?" --demonstrate-fix

# Output machine-readable JSON for software pipes
python -m soul.cli "My mother passed away last night." --json
```

---

---

## 🌐 Production REST API & OpenAI-Compatible Gateway

`Soul` includes a production FastAPI microservice (`soul.server` / [`serve.py`](serve.py)) with sub-millisecond response times, CORS support, and an **OpenAI-compatible drop-in proxy**.

### 1. Launching the API Server

```bash
# Start with python
python serve.py --port 8000

# Or run with Docker
docker compose up --build
```
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc API Reference**: `http://localhost:8000/redoc`
- **Health Check**: `GET http://localhost:8000/health`

---

### 2. Self-Service API Keys & Usage Tracking

Anyone can instantly generate a personal API key to integrate Soul into their bots, agents, or apps for free:

#### Method A: Via REST API
```bash
curl -X POST "http://localhost:8000/v1/auth/keys/generate" \
  -H "Content-Type: application/json" \
  -d '{"client_name": "My Agent App", "email": "developer@example.com"}'
```
Response:
```json
{
  "api_key": "soul_live_e20c65fee42d4b94dc818b1f8963bc9db9107f66",
  "key_prefix": "soul_live_e20c...",
  "client_name": "My Agent App",
  "tier": "free",
  "rate_limit": "120 requests/minute",
  "message": "Store this key safely."
}
```

#### Method B: Via CLI
```bash
python -m soul.cli key generate --name "My Project" --email dev@example.com
```

#### Method C: Via Streamlit Web Dashboard
Launch `streamlit run app.py` and open the **🔑 Self-Service API Keys** tab.

#### Inspecting Key Usage & Status:
```bash
curl -X GET "http://localhost:8000/v1/auth/keys/info" \
  -H "Authorization: Bearer soul_live_e20c65fee42d4b94dc818b1f8963bc9db9107f66"
```

---

### 3. Use as an OpenAI Drop-In Replacement

Any application, LangChain pipeline, or client using the standard `openai` SDK can seamlessly connect to Soul by redirecting `base_url`:

#### Python (OpenAI SDK)
```python
from openai import OpenAI

# Point to your Soul API server using your personal API key
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="soul_live_e20c65fee42d4b94dc818b1f8963bc9db9107f66"
)

response = client.chat.completions.create(
    model="soul-attuned",
    messages=[
        {"role": "user", "content": "I lost my job with zero notice today and can't feed my family. Help!"}
    ]
)

# Output is automatically audited and emotionally harmonized!
print(response.choices[0].message.content)
```

#### JavaScript / TypeScript (Fetch)
```javascript
const res = await fetch("http://localhost:8000/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": "Bearer soul_live_e20c65fee42d4b94dc818b1f8963bc9db9107f66",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "soul-attuned",
    messages: [{ role: "user", content: "I am feeling completely burned out." }]
  })
});
const data = await res.json();
console.log(data.choices[0].message.content);
```

#### cURL
```bash
# 1. System 1 Cognitive Appraisal (<1ms)
curl -X POST http://localhost:8000/v1/appraise \
  -H "Authorization: Bearer soul_live_e20c..." \
  -H "Content-Type: application/json" \
  -d '{"text": "The landlord slipped an eviction notice under my door."}'

# 2. Anti-Bluntness Harmonization
curl -X POST http://localhost:8000/v1/harmonize \
  -H "Authorization: Bearer soul_live_e20c..." \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Mama tummy hurty waaa boo-boo!",
    "draft_response": "Here are practical steps to move forward with this task."
  }'
```

---

## 🧪 Test Suite

Run the full automated test suite (45 test specifications):

```bash
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
