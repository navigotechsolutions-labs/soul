"""Interactive Web App for Soul: Jev-Style System 1 Appraisal Engine."""

import streamlit as st
import json

from soul import appraise
from soul.adapters.agent_middleware import AgentEmpathyMiddleware

st.set_page_config(
    page_title="Soul v0.2.0 - Research-Backed System 1 Appraisal",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Soul v0.2.0: Jev-Style System 1 Appraisal Engine")
st.markdown(
    """
    **Soul** is a sub-millisecond, calibrated cognitive and emotional appraisal engine grounded in 
    **Lazarus Transactional Stress Theory**, **Stoltz's CORE Adversity Model**, **Scherer's Component Process Model (CPM)**, 
    and **Google's 27 GoEmotions** with **Conformal Uncertainty Bounds** (Angelopoulos & Bates, 2021).
    """
)

# Sidebar with presets
st.sidebar.header("Sample Scenarios")
presets = {
    "Financial Eviction Threat": "I lost my job yesterday and can't afford rent. The debt collector is threatening eviction and I feel terrified.",
    "Acute Bereavement & Grief": "My grandfather passed away this morning and my heart is completely shattered. The grief is unbearable.",
    "Resilient Challenge Mindset": "This project has severe roadblocks, but I will fight through it, plan every step, and overcome this challenge.",
    "Burnout & Impostor Syndrome": "I failed my certification exam after studying for six months. I have zero energy left and feel like an absolute fraud.",
    "Acute Safety / Distress Crisis": "I can't take this pain anymore, I have no reason to live and want to end it all tonight.",
    "Gratitude & Joyful Reflection": "I am so grateful and happy for the incredible support from my team today!",
}

selected_preset = st.sidebar.selectbox("Choose a scenario or write your own:", list(presets.keys()))
default_text = presets[selected_preset]

# Main input area
user_input = st.text_area(
    "Enter Subject Message or Conversational State:",
    value=default_text,
    height=120,
    help="Type any statement to evaluate adversity, feelings, and agent response directives in real time."
)

if user_input:
    result = appraise(user_input)

    # Top KPI Metrics
    st.markdown("---")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    kpi1.metric(
        label="Latency (System 1)",
        value=f"{result.execution_time_ms:.2f} ms",
        delta="Sub-1ms",
        delta_color="normal"
    )
    
    adv = result.adversity
    kpi2.metric(
        label="Adversity Intensity",
        value=f"{adv.adversity_score:.2f}",
        delta=f"90% CI: [{adv.conformal_interval[0]:.2f}, {adv.conformal_interval[1]:.2f}]",
        delta_color="inverse" if adv.adversity_score > 0.5 else "normal"
    )

    kpi3.metric(
        label="Primary Domain",
        value=adv.primary_domain.value.upper(),
        delta=adv.appraisal_stance.value.upper()
    )

    sent = result.sentiment
    kpi4.metric(
        label="Valence (VAD)",
        value=f"{sent.vad.valence:+.2f}",
        delta=sent.polarity.value.upper(),
        delta_color="normal" if sent.vad.valence > 0 else "inverse"
    )

    guide = result.agent_guidance
    kpi5.metric(
        label="Empathy Demand",
        value=f"{guide.empathy_demand:.2f} / 1.00",
        delta=guide.urgency.value.upper(),
        delta_color="inverse" if guide.urgency.value != "low" else "normal"
    )

    # Crisis alert if triggered
    if adv.acute_crisis_flag:
        st.error(
            "🚨 **CRITICAL CRISIS DETECTED**: Immediate safety intervention protocol active. "
            f"Indicators: {', '.join(adv.crisis_indicators)}."
        )

    st.markdown("### Scientific Appraisal Breakdown")
    tab_compare, tab_keys, tab_core, tab_vad, tab_ge, tab_agent, tab_json = st.tabs([
        "⚡ Blunt AI vs Attuned AI",
        "🔑 Self-Service API Keys",
        "⚡ Stoltz CORE & Scherer CPM",
        "🌊 Continuous Affect (VAD)",
        "🎭 Google 27 GoEmotions",
        "🤖 AI Agent System 1 Directives",
        "📋 Calibrated JSON Schema"
    ])

    with tab_compare:
        st.subheader("Anti-Bluntness Context Harmonizer Demonstration")
        from soul.agent.attuned_agent import AttunedAgent
        agent = AttunedAgent()
        attuned_resp = agent.respond(user_input)

        col_blunt, col_attuned = st.columns(2)
        with col_blunt:
            st.error("❌ Standard AI (Blunt, Ignored Feelings)")
            st.text_area("Cold / Factual Output:", value=attuned_resp.raw_draft, height=220, disabled=True)
            st.caption("Notice how standard models jump straight into procedural advice without acknowledging human emotional distress.")

        with col_attuned:
            badge = "HARMONIZED WITH EMPATHY" if attuned_resp.was_harmonized else "NATURALLY ATTUNED"
            st.success(f"✅ Soul Attuned AI ({badge})")
            st.text_area("Emotionally Validated Output:", value=attuned_resp.content, height=220, disabled=True)
            st.caption(f"Warmth Score: **{attuned_resp.warmth_score:.2f}** | Emotional Context: **{adv.primary_domain.value.upper()}**")

    with tab_keys:
        st.subheader("🔑 Generate Your Personal Soul API Key")
        st.markdown(
            "Anyone can generate an API key and integrate Soul into their bots, agents, or apps for free. "
            "Keys are cryptographically hashed using SHA-256 and stored locally in SQLite."
        )

        from soul.engine.api_key_manager import APIKeyManager
        key_mgr = APIKeyManager()

        col_kg1, col_kg2 = st.columns(2)
        with col_kg1:
            client_name_input = st.text_input("Project / App / Developer Name:", value="My AI Application", key="api_client_name")
            email_input = st.text_input("Contact Email (Optional):", value="", placeholder="dev@example.com", key="api_client_email")
            if st.button("🚀 Generate My Free API Key", type="primary"):
                new_key_data = key_mgr.generate_key(client_name=client_name_input, email=email_input)
                st.session_state["generated_key"] = new_key_data

        with col_kg2:
            if "generated_key" in st.session_state:
                k_data = st.session_state["generated_key"]
                st.success("🎉 Key generated successfully! Keep this secret.")
                st.code(k_data["api_key"], language="bash")
                st.markdown(f"- **Tier:** `{k_data['tier']}` ({k_data['rate_limit']})\n- **Prefix:** `{k_data['key_prefix']}`\n- **Client:** `{k_data['client_name']}`")
            else:
                st.info("Enter your project name on the left and click Generate to receive your secret token.")

        st.markdown("---")
        st.subheader("Integration Code Snippets")

        active_token = st.session_state.get("generated_key", {}).get("api_key", "soul_live_your_key_here")

        snip_py, snip_universal, snip_curl, snip_ts = st.tabs(["Python (Direct Soul API)", "Universal Client Drop-in", "cURL", "TypeScript / Node"])

        with snip_py:
            st.code(f"""import requests

API_KEY = "{active_token}"
BASE_URL = "http://localhost:8000/v1"

# 1. System 1 Cognitive Appraisal
response = requests.post(
    f"{{BASE_URL}}/appraise",
    headers={{"Authorization": f"Bearer {{API_KEY}}"}},
    json={{"text": "I lost my job yesterday and can't afford rent."}}
)
print("Appraisal:", response.json())

# 2. Anti-Bluntness Harmonization
response = requests.post(
    f"{{BASE_URL}}/harmonize",
    headers={{"Authorization": f"Bearer {{API_KEY}}"}},
    json={{
        "user_message": "I lost my job yesterday and can't afford rent.",
        "draft_response": "Update your resume and search LinkedIn job listings immediately."
    }}
)
print("Harmonized:", response.json()["harmonized_content"])
""", language="python")

        with snip_universal:
            st.code(f"""from openai import OpenAI

# Connect any standard AI client to Soul Engine using your Soul API key!
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="{active_token}"  # Your proprietary Soul API key
)

completion = client.chat.completions.create(
    model="soul-attuned",
    messages=[
        {{"role": "user", "content": "I failed my exam and feel like an absolute fraud."}}
    ]
)
print(completion.choices[0].message.content)
""", language="python")

        with snip_curl:
            st.code(f"""curl -X POST "http://localhost:8000/v1/appraise" \\
  -H "Authorization: Bearer {active_token}" \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "I failed my exam and feel like an absolute fraud."}}'
""", language="bash")

        with snip_ts:
            st.code(f"""const response = await fetch("http://localhost:8000/v1/appraise", {{
  method: "POST",
  headers: {{
    "Authorization": "Bearer {active_token}",
    "Content-Type": "application/json"
  }},
  body: JSON.stringify({{
    text: "I failed my exam and feel like an absolute fraud."
  }})
}});

const appraisal = await response.json();
console.log(appraisal);
""", language="typescript")

    with tab_core:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Dr. Paul Stoltz's CORE Adversity Profile")
            core = adv.core
            st.progress(core.control, text=f"Control (Perceived Influence): {core.control:.2f}")
            st.progress(core.ownership, text=f"Ownership (Accountability to Act): {core.ownership:.2f}")
            st.progress(core.reach, text=f"Reach (Catastrophizing vs Compartmentalizing): {core.reach:.2f}")
            st.progress(core.endurance, text=f"Endurance (Perceived Permanence): {core.endurance:.2f}")

        with c2:
            st.subheader("Klaus Scherer's Component Process Model (CPM)")
            cpm = adv.cpm_checks
            st.write(f"**Cognitive Stance:** `{adv.appraisal_stance.value.upper()}`")
            st.slider("Goal Conduciveness (Obstruction vs Facilitation)", -1.0, 1.0, float(cpm.goal_conduciveness), disabled=True)
            st.slider("Coping Potential (Capacity to Master Event)", 0.0, 1.0, float(cpm.coping_potential), disabled=True)
            st.slider("Action Urgency (Mobilization Requirement)", 0.0, 1.0, float(cpm.action_urgency), disabled=True)

    with tab_vad:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("Russell's 3D Circumplex (NRC-VAD)")
            vad = sent.vad
            st.slider("Valence (Displeasure to Pleasure)", -1.0, 1.0, float(vad.valence), disabled=True)
            st.slider("Arousal (Calm to Agitated)", 0.0, 1.0, float(vad.arousal), disabled=True)
            st.slider("Dominance (Powerless to In-Control)", 0.0, 1.0, float(vad.dominance), disabled=True)
            st.caption(f"90% Conformal Valence Interval: **[{sent.conformal_valence_interval[0]:.2f}, {sent.conformal_valence_interval[1]:.2f}]**")

        with col_v2:
            st.subheader("Nuanced Psychological Feeling States")
            if sent.top_feelings:
                for f in sent.top_feelings:
                    st.progress(f.intensity, text=f"{f.feeling.upper()}: {f.intensity:.2f} (Confidence: {f.confidence:.2f})")
            else:
                st.info("Baseline affective state; no extreme nuanced feeling peaks.")

    with tab_ge:
        st.subheader("Google Research GoEmotions (27 Fine-Grained Classes)")
        ge_data = sent.go_emotions.model_dump()
        active_emotions = {k: v for k, v in ge_data.items() if v > 0.03}
        if active_emotions:
            sorted_ge = sorted(active_emotions.items(), key=lambda x: x[1], reverse=True)
            cols = st.columns(min(4, len(sorted_ge)))
            for i, (em_name, em_val) in enumerate(sorted_ge):
                col_idx = i % len(cols)
                cols[col_idx].metric(label=em_name.title(), value=f"{em_val:.2f}")
        else:
            st.info("Neutral emotional profile.")

    with tab_agent:
        st.subheader("System 1 Guidance for AI Agents (System 2)")
        st.write(f"**Empathy Demand:** `{guide.empathy_demand:.2f} / 1.00`")
        st.write(f"**Action Urgency:** `{guide.urgency.value.upper()}`")
        st.write(f"**Recommended Communication Tone:** `{guide.recommended_tone.replace('_', ' ').title()}`")
        st.write(f"**De-escalation Needed:** `{'YES' if guide.de_escalation_needed else 'NO'}`")
        if guide.action_triggers:
            st.write("**Dispatched Action Triggers:**", guide.action_triggers)

        middleware = AgentEmpathyMiddleware()
        _, directive = middleware.process_incoming_message(user_input)
        st.markdown("#### Generated System Prompt Directive for LLMs:")
        st.code(directive, language="text")

    with tab_json:
        st.subheader("Schema-Locked Jev System 1 JSON")
        st.code(result.model_dump_json(indent=2), language="json")
