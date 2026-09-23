# Soul Engine & Soul IDE (`soul-engine`)

[![PyPI Version](https://img.shields.io/badge/pypi-v0.4.0-blue.svg)](https://pypi.org/project/soul-engine/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Live Production Demo](https://img.shields.io/badge/live%20demo-soul.navigotechsolutions.com-emerald.svg)](https://soul.navigotechsolutions.com/dashboard)
[![Soul IDE](https://img.shields.io/badge/Soul%20IDE-standalone%20workbench-purple.svg)](https://soul.navigotechsolutions.com/ide)
[![Anti-Slop Linter](https://img.shields.io/badge/Anti--Slop%20Linter-live%20audit-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **"A lightweight text appraisal and response harmonization toolkit."**
> `Soul` uses lexicons and phrase-matching rules to estimate emotional signals, flag selected crisis-related phrases, inspect writing style, and provide response guidance. These estimates are heuristic and are not clinical assessments or validated safety decisions. Optional LLM-backed responses require a configured provider key.

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

### The Approach: Fast Heuristic Appraisal + Response Harmonization

`Soul` provides optional text signals and response transformations for downstream AI:
1. **Rule-based appraisal**: Estimates adversity domain, stress stance, affect coordinates $(V, A, D)$, and selected feelings from text matches.
2. **Prompt guidance**: Adds heuristic tone and empathy suggestions to an LLM system prompt before inference.
3. **Response harmonization**: Audits a candidate response and may prepend a rule-selected bridge when text matches indicate distress.

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

| Capability | What Soul Does | Intended Use |
|---|---|---|
| **1. Heuristic text signals** | Estimates sentiment, domain, and selected emotion labels using lexical rules. | A low-cost hint for downstream systems; validate before using in decisions. |
| **2. Response guidance** | Produces suggested tone and urgency fields, including a possible crisis phrase-match flag. | Treat as advisory metadata; crisis matches require human review and are not safety triage. |
| **3. Local processing speed** | The local rule-based appraisal avoids an LLM call; timing depends on input size and hardware. | Useful where a fast preliminary signal is helpful. |

---

## 🎯 Enterprise Use Cases & Practical Applications

The API can be integrated into applications that use language models. The examples below are possible integration areas, not validated outcomes or safety assurances. The engine does not provide clinical, legal, financial, or emergency decisions.

### 1. High-Stakes Customer Support & Churn Prevention
* **The Problem**: Standard AI agents respond to furious or panicking customers with rigid, robotic template answers (*"I understand your frustration. Please refer to section 4.2 of our FAQ"*), driving viral social outrage, ticket escalations, and customer churn.
* **Soul Engine Solution**: Evaluates user distress and hostility **before** the LLM generates tokens. Injects dynamic calming directives and flags high-adversity users (`threat > 0.70`) for immediate human supervisor handoff.
* **Impact**: Decreased churn, reduced customer escalations, and higher CSAT scores.

### 2. FinTech, Banking & Fraud Incident Escalation
* **The Problem**: When a card is blocked overseas or unauthorized transactions occur, customers enter acute **Panic/Threat states**. Cold multi-step verification flows exacerbate anxiety and permanently damage institutional trust.
* **Soul Engine Solution**: Pinpoints the 2D Affect coordinate (high arousal, negative valence), enforcing grounded, de-escalating assurance (*"Your remaining funds are secure, and I am putting a freeze on this specific card immediately"*) before requesting account details.

### 3. DevOps, SRE & On-Call Emergency Triage
* **The Problem**: An engineer paged at 3:00 AM during a massive production outage is under severe cognitive load. Verbose, conversational AI explanations waste critical incident response minutes.
* **Soul Engine Solution**: Detects urgency and panic in Slack on-call channels or terminal inputs. Forces the AI into an **Executive Incident Commander posture**: ultra-succinct, bulleted remediation steps with zero conversational filler.

### 4. Telehealth & Wellness Conversational Gateways
* **The Problem**: Patients messaging portals with post-operative distress or health anxiety receive overly clinical, detached, or accidentally dismissive responses.
* **Soul Engine Solution**: Continuously evaluates emotional vulnerability signals, calibrating empathy coefficients (`0.0` to `1.0`) so the assistant communicates with genuine warmth and clarity without providing unauthorized medical diagnoses. Acts as an emotional circuit breaker if crisis thresholds are breached.

### 5. Autonomous Sales Agents & Trust Building
* **The Problem**: Aggressive sales bots push hard closes when prospects exhibit price hesitation or skepticism, killing deals.
* **Soul Engine Solution**: Detects nuanced buyer skepticism and shifts the conversation from hard-pitching to consultative social proof and transparent FAQ resolution.

### 6. Dynamic Gaming NPCs & Virtual Companions
* **The Problem**: Game NPCs feel scripted, predictable, and emotionally deaf to player sarcasm, anger, or loyalty.
* **Possible integration**: A game could use heuristic text signals as one input to dialogue or animation selection, after testing against its own content and players.

### Industry Value Matrix

| Industry | Primary Risk Prevented | Soul Engine Value | Deployment Model |
| :--- | :--- | :--- | :--- |
| **Enterprise SaaS** | Customer churn & viral social outrage | Auto-de-escalates angry support tickets | Drop-in OpenAI Proxy |
| **FinTech & Crypto** | Brand panic during downtime/fraud | Calms anxious users during asset disputes | Direct `/v1/appraise` API |
| **DevOps & Cloud** | SRE cognitive overload during outages | Strips AI fluff, delivers concise commands | Terminal CLI / Slack Bot |
| **Healthcare** | Patient distress & clinical detachment | Optional tone guidance, subject to independent clinical, privacy, and regulatory review | API integration |
| **Gaming & Metaverse** | Flat, immersion-breaking NPCs | NPCs react dynamically to player emotions | High-speed REST API / C++ |
| **E-Commerce & Sales** | High drop-off at checkout & buyer friction | Senses hesitation and builds authentic trust | Webhook / API Middleware |

---

## 🚀 Quickstart

> 📖 **Looking for the complete manual?** Check out the full [**User Guide (`USER_GUIDE.md`)**](USER_GUIDE.md) for detailed Python, REST API, Universal SDKs, Web UI, and Docker tutorials.

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

For the HTTP API and browser demo, install the optional runtime dependencies:

```bash
pip install -e ".[server,demo]"
```

The API requires an API key by default (`SOUL_REQUIRE_AUTH=1`). Create an account at `/` and issue a key, or set `SOUL_REQUIRE_AUTH=0` only for a trusted local development instance. API mutations are limited to 120 requests per minute per bearer identity (or client IP when unauthenticated); auth endpoints allow 20/minute and public key generation 10/minute per identity. Limits use the configured SQLite database and apply per server database. Set a random `SOUL_JWT_SECRET` of at least 32 bytes before starting the service so sessions remain valid across restarts. Set `SOUL_CORS_ORIGINS` to a comma-separated list of trusted browser origins when hosting the UI separately.

---

### 💻 Launch the Standalone Soul IDE

Start the local desktop development environment and anti-slop workbench in your browser:

```bash
soul ide
```
*Opens `http://localhost:8000/ide` featuring a split-pane editor, real-time AI slop linter, and 1-click humanization.*

---

### 🛡️ Anti-AI-Slop Linter (Terminal & CI/CD)

```bash
# 1. Audit text, UI copy, or landing page text
soul audit "In today's fast-paced world—efficiency is crucial. 🚀 Delve into our tool!"

# 2. Instant 1-click humanization
soul sanitize "In today's fast-paced world—efficiency is crucial. 🚀 Delve into our tool!"

# 3. Add to pre-commit or CI/CD to prevent shipping synthetic AI slop
soul audit --file ./copy.txt --fail-on-slop
```

---

### Basic Python Usage


```python
import soul

# 1. Local heuristic appraisal
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

## 🏛️ Inspired by Cognitive Science Frameworks

`Soul` borrows concepts from the following frameworks. The implementation is heuristic and has not been validated as a psychological instrument:

| Literature & Foundation | Scientific Source | How Soul Implements It |
|---|---|---|
| **Component Process Model (CPM)** | Klaus Scherer (*2009, 2013*) | Rule-based fields use selected appraisal concepts; they do not implement or validate the full model. |
| **Transactional Stress Theory** | Lazarus & Folkman (*1984*) | Phrase rules map selected text to stress stances; this is not a validated psychological measure. |
| **Adversity Quotient (CORE)** | Dr. Paul Stoltz (*1997, 2000*) | Heuristic fields use CORE labels; they are not validated measurements. |
| **Continuous Affect Space** | James Russell (*1980, 2003*) | Lexicon-derived VAD estimates; context and sarcasm can produce errors. |
| **Fine-Grained Emotion Taxonomy** | Google Research GoEmotions (*Demszky et al., ACL 2020*) | Rule-based estimates mapped to selected labels; not the GoEmotions trained classifier. |
| **Uncertainty intervals** | — | Intervals are implementation estimates and should not be interpreted as calibrated coverage without independent evaluation. |
| **Temperature scaling** | Guo et al. (*ICML 2017*) | A related calibration technique; implementation outputs require empirical validation before calibration claims. |

*These are conceptual inspirations, not evidence that this implementation reproduces or validates the cited models. See [`RESEARCH.md`](RESEARCH.md) for background.*

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

The harness checks implementation behavior against synthetic scenarios. Its self-generated cases are not an independent accuracy, calibration, safety, or performance evaluation; passing them does not establish real-world coverage.

---

## 🖥️ Interactive Web UI Dashboard

`Soul` comes with an interactive Streamlit application:

```bash
streamlit run app.py
```

Features:
- Heuristic affect and adversity estimates from lexicon matches.
- Rule-based emotion label summaries.
- A demonstration of draft-response harmonization; outputs may be inaccurate.

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

## 🌐 Production REST API & Universal Chat Gateway
 
`Soul` includes a FastAPI service (`soul.server` / [`serve.py`](serve.py)) with configurable CORS and an OpenAI-compatible chat endpoint. Appraisal is local; response generation uses a configured provider or a local fallback.

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

### 3. Connect Any Client, Terminal CLI, or SDK (Using Soul API Keys)

Any application, terminal tool (like `aichat` or `tgpt`), LangChain pipeline, or client using standard chat completions can seamlessly connect to Soul Engine using your proprietary **Soul API Key (`soul_live_...`)**.

#### OpenAI-Compatible Chat Endpoint
Use the OpenAI SDK with a Soul API key. Set `OPENAI_API_KEY` or `DEEPSEEK_API_KEY` on the Soul server for provider-backed generation. Stream mode returns the completed response in SSE format; it does not stream live provider tokens.

```python
from openai import OpenAI

# 1. Point to Soul Engine (Cloud Production or Local Server):
client = OpenAI(
    base_url="https://soul.navigotechsolutions.com/v1",  # or "http://localhost:8000/v1"
    api_key="soul_live_<your_key>"
)

# Soul appraises locally, requests a provider completion, then harmonizes the result:
stream = client.chat.completions.create(
    model="soul-attuned",  # or deepseek-chat, gpt-4o, claude-3-5-sonnet
    messages=[
        {"role": "user", "content": "I lost my job with zero notice today and can't feed my family. Help!"}
    ],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content or ""
    print(content, end="", flush=True)
```

#### 🪄 Anti-Slop Sanitizer (Eradicate Emojis-as-Icons, Em-Dashes & ChatGPT Clichés)
```bash
# REST API (in-process rule-based sanitization):
curl -X POST https://soul.navigotechsolutions.com/v1/sanitize/anti-slop \
  -H "Authorization: Bearer soul_live_..." \
  -H "Content-Type: application/json" \
  -d '{"text": "In today'\''s fast-paced world—efficiency is crucial. 🚀 Delve into our tool!"}'

# Output:
# {"original": "...", "sanitized": "Today, efficiency is essential. Explore our tool!"}
```

#### JavaScript / TypeScript (Native Fetch)
```javascript
const res = await fetch("https://soul.navigotechsolutions.com/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": "Bearer soul_live_your_key_here",
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

#### Direct cURL Endpoints
```bash
# 1. Heuristic text appraisal
curl -X POST https://soul.navigotechsolutions.com/v1/appraise \
  -H "Authorization: Bearer soul_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"text": "The landlord slipped an eviction notice under my door."}'

# 2. Anti-Bluntness Harmonization (user_message optional in v0.4.0)
curl -X POST https://soul.navigotechsolutions.com/v1/harmonize \
  -H "Authorization: Bearer soul_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_response": "Here are practical steps to move forward with this task: 1. Error audit. 2. Pomodoro."
  }'
```

---

## 🏷️ GitHub Topics & Keywords

`anti-ai-slop` • `openai-proxy` • `cognitive-appraisal` • `affective-computing` • `emotional-intelligence` • `system-1-thinking` • `anti-bluntness` • `llm-middleware` • `chatgpt-linter` • `sentiment-analysis` • `russell-vad` • `fastapi` • `python` • `developer-tools`

---

## 🧪 Test Suite

Run the full automated test suite (45 test specifications):

```bash
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
