# 📘 Soul Engine: Complete User Guide

Welcome to the **Soul Engine User Guide**. This handbook covers everything you need to know to use Soul—from no-code web usage to integrating with AI agents, Python pipelines, and production REST APIs.

---

## 📑 Table of Contents
1. [Overview](#1-overview)
2. [Quickstart (60 Seconds)](#2-quickstart-60-seconds)
3. [Interactive Web Dashboard (No-Code)](#3-interactive-web-dashboard-no-code)
4. [Python SDK Usage](#4-python-sdk-usage)
5. [Universal Client & App Integration (Soul API Key)](#5-universal-client--app-integration-soul-api-key)
6. [Production REST API & Endpoints](#6-production-rest-api--endpoints)
7. [Self-Service API Key Management](#7-self-service-api-key-management)
8. [Command-Line Interface (CLI)](#8-command-line-interface-cli)
9. [Interpreting the Cognitive & Emotional Metrics](#9-interpreting-the-cognitive--emotional-metrics)
10. [Deploying to Production (Docker & Cloud)](#10-deploying-to-production-docker--cloud)

---

## 1. Overview

**Soul** is a fast (<1ms) "System 1" cognitive appraisal engine and anti-bluntness harmonizer. It solves the core flaw of modern AI: **answering literal words while ignoring human emotional distress.**

```
[Distressed User Message]
          │
          ▼
[Soul System 1 Perception (<1ms)] ──► Understands true feelings, stress stance & stakes
          │
          ▼
[Attuned Action / Response]       ──► Empathetic validation + Clear, actionable solutions
```

---

## 2. Quickstart (60 Seconds)

### Installation
From the repository root:
```bash
git clone https://github.com/navigotechsolutions-labs/soul.git
cd soul
pip install -e .
```

Or install directly from GitHub into any project:
```bash
pip install git+https://github.com/navigotechsolutions-labs/soul.git
```

---

## 3. Interactive Web Dashboard (No-Code)

If you prefer a visual interface without writing code:

```bash
streamlit run app.py
```

### What You Can Do in the Web Dashboard:
1. **Analyze Any Text:** Select a preset or type any message (e.g. an email from a boss, a customer ticket, or a friend's text).
2. **Side-by-Side Comparison:** See what a cold standard AI would say vs. what Soul's attuned AI says.
3. **Inspect Psychological Dimensions:** Explore Russell's 3D continuous affect, Google 27 GoEmotions, and Stoltz CORE adversity ratings.
4. **Generate API Keys:** Open the **"🔑 Self-Service API Keys"** tab to create free keys with 1 click.

---

## 4. Python SDK Usage

### A. Real-Time Cognitive Appraisal (<1ms)
```python
import soul

message = "I lost my job yesterday and can't feed my family. How do I update my resume?"
result = soul.appraise(message)

# Access psychological insights
print(f"Adversity Domain: {result.adversity.primary_domain.value}")  # workplace_academic
print(f"Cognitive Stance: {result.adversity.appraisal_stance.value}") # threat
print(f"Empathy Demand:   {result.agent_guidance.empathy_demand:.2f}") # e.g. 0.83
print(f"Recommended Tone: {result.agent_guidance.recommended_tone}")  # warm_validating_empathetic
print(f"Execution Latency: {result.execution_time_ms:.2f} ms")       # sub-millisecond!
```

### B. End-to-End Attuned Response Generation
```python
import soul

# Generates response that automatically audits and eliminates bluntness
response = soul.respond("My mother passed away last night and my heart is completely shattered.")
print(response.content)
```

### C. Anti-Bluntness Auditor & Harmonizer
```python
from soul.engine.harmonizer import BluntnessAuditor, ResponseHarmonizer

auditor = BluntnessAuditor()
harmonizer = ResponseHarmonizer(auditor=auditor)

user_msg = "The landlord slipped an eviction notice under my door today."
cold_draft = "1. Find a tenant rights lawyer. 2. Request a 30-day stay of execution."

appraisal = soul.appraise(user_msg)
harmonized_text, was_changed = harmonizer.harmonize(cold_draft, appraisal)

print(harmonized_text)
# Output:
# "Going through financial stress and dealing with bills or uncertainty is incredibly heavy and anxiety-inducing...
# 1. Find a tenant rights lawyer. 2. Request a 30-day stay of execution."
```

---

## 5. Universal Client & App Integration (Soul API Key)

Soul Engine provides standard `/v1/chat/completions` compatibility, which allows developers to connect **any terminal tool, AI IDE (Cursor, Continue), client library, or pipeline** directly to Soul Engine using your proprietary **Soul API Key (`soul_live_...`)** with zero code modifications:

### Python (Universal Client)
```python
from openai import OpenAI  # Or any standard AI client library

# Connect to your Soul Engine server using your proprietary Soul API Key
client = OpenAI(
    base_url="https://soul.navigotechsolutions.com/v1",  # Or http://localhost:8000/v1
    api_key="soul_live_eb27f2e6ff2c4156d75df99be50bc41abbe260a9"  # Issued by Soul Engine
)

# Standard chat completion call - automatically routed through Soul's System 1 appraisal & anti-bluntness filter
response = client.chat.completions.create(
    model="soul-attuned",
    messages=[
        {"role": "user", "content": "I failed my certification exam for the third time and feel like an absolute fraud."}
    ]
)

print(response.choices[0].message.content)
```

### Terminal CLI / Shell Tools
You can route terminal utilities (such as `aichat`, `tgpt`, `mods`, or custom CLI scripts) through Soul Engine simply by setting standard environment variables:

```bash
# Terminal setup:
export OPENAI_BASE_URL="https://soul.navigotechsolutions.com/v1"
export OPENAI_API_KEY="soul_live_your_soul_key_here"

# Terminal tools will now automatically use Soul Engine for cognitive appraisal and attuned responses!
```

---

## 6. Production REST API & Endpoints

### Starting the Server
```bash
python serve.py --port 8000
```
- **Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Key Endpoints:

#### 1. System 1 Cognitive Appraisal
```bash
curl -X POST "http://localhost:8000/v1/appraise" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"text": "The client director was furious with our presentation today."}'
```

#### 2. Anti-Bluntness Response Harmonization
```bash
curl -X POST "http://localhost:8000/v1/harmonize" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "I was just laid off.",
    "draft_response": "1. Update LinkedIn. 2. File for unemployment."
  }'
```

#### 3. Full Attuned Generation
```bash
curl -X POST "http://localhost:8000/v1/respond" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"message": "I am feeling completely burned out."}'
```

---

## 7. Self-Service API Key Management

Anyone can generate a personal API key to use Soul in their own software:

### Method A: Via REST API
```bash
curl -X POST "http://localhost:8000/v1/auth/keys/generate" \
  -H "Content-Type: application/json" \
  -d '{"client_name": "My App", "email": "dev@example.com"}'
```

### Method B: Via CLI
```bash
python -m soul.cli key generate --name "My Bot"
```

### Method C: Inspecting Usage & Tier
```bash
curl -X GET "http://localhost:8000/v1/auth/keys/info" \
  -H "Authorization: Bearer soul_live_<your_key>"
```

---

## 8. Command-Line Interface (CLI)

Soul provides powerful terminal utilities:

```bash
# 1. Rich Terminal Appraisal
python -m soul.cli "I failed my exams again."

# 2. Side-by-Side Comparison Demonstration
python -m soul.cli "I lost my job yesterday." --demonstrate-fix

# 3. Machine-Readable JSON for Unix Pipelines
python -m soul.cli "My mother passed away." --json | jq .adversity

# 4. API Key Commands
python -m soul.cli key generate --name "Developer"
python -m soul.cli key info soul_live_<key>

# 5. Real-World Everyday Human Communication Benchmark
python test_human_usage.py
```

---

## 9. Interpreting the Cognitive & Emotional Metrics

Soul's appraisal is grounded in validated psychological science:

| Metric | Scientific Foundation | Meaning & Values |
|---|---|---|
| **Adversity Score** | Lazarus & Folkman (1984) | Scale from `0.0` (benign) to `1.0` (catastrophic stress). |
| **Cognitive Stance** | Lazarus Transactional Model | `THREAT` (perceived impending harm), `HARM_LOSS` (damage already done), `CHALLENGE` (resilient mastery), or `BENIGN`. |
| **Valence (V)** | Russell 3D Circumplex | `-1.0` (extreme displeasure/distress) to `+1.0` (pure joy). |
| **Arousal (A)** | Russell 3D Circumplex | `0.0` (calm/sluggish) to `1.0` (highly agitated/panicked). |
| **Dominance (D)** | Russell 3D Circumplex | `0.0` (powerless/submissive) to `1.0` (in control/confident). |
| **Stoltz CORE** | Dr. Paul Stoltz (1997) | Evaluates **Control**, **Ownership**, **Reach** (catastrophizing), and **Endurance** (permanence). |
| **Empathy Demand** | Soul Calibration Model | `0.0` to `1.0`—indicates how critical emotional validation is before task solving. |
| **Prescribed Tone** | Agent Guidance Module | Prescribes communication style: `warm_validating_empathetic`, `soothing_caregiver`, `solemn_accountable`, `calm_unreactive`, or `gentle_encouraging`. |

---

## 10. Deploying to Production (Docker & Cloud)

### Docker Deployment
```bash
# Build and run container
docker build -t soul-engine .
docker run -p 8000:8000 soul-engine

# Or using Docker Compose
docker compose up -d
```

### 1-Click Cloud Deployment:
- **Render / Railway:** Connect your GitHub fork; it automatically detects the `Dockerfile` and runs `serve.py`.
- **Hugging Face Spaces:** Create a new Space, select Docker, and connect repository.
- **Google Cloud Run:**
  ```bash
  gcloud run deploy soul-engine --source . --port 8000 --allow-unauthenticated
  ```

---

## 🤝 Need Help?
- **GitHub Issues:** [https://github.com/navigotechsolutions-labs/soul/issues](https://github.com/navigotechsolutions-labs/soul/issues)
- **Repository:** [https://github.com/navigotechsolutions-labs/soul](https://github.com/navigotechsolutions-labs/soul)
