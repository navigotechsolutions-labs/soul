/**
 * Soul Engine SaaS Frontend Logic
 * Supports: Live System 1 Playground, User Authentication, Google Sign-In, and API Key Lifecycle.
 */

const API_BASE = window.location.origin;

// State
let currentUser = null;
let currentToken = localStorage.getItem("soul_access_token") || null;
let authMode = "login"; // "login" | "signup"

const PRESETS = {
  layoff: "I was just laid off with zero notice after 8 years at the company. I have a family to feed and I am in total shock. How do I update my LinkedIn?",
  exam_fail: "I failed my certification exam for the third time after studying for six months. I feel like an absolute fraud and have zero energy left.",
  bereavement: "My mother passed away last night and my heart is completely shattered. The grief is unbearable.",
  pharmacy_distress: "You debited $450 from my checking account by mistake today! Now my card is declined at the pharmacy for my daughter's asthma medicine. Fix this right now!",
  relationship_hurt: "You've been working late every single night this week. You missed dinner again. I feel like our life together doesn't even matter to you anymore."
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  loadPreset("layoff");
  checkCurrentUser();
});

// --- Theme Toggle (Daylight / Night) ---
function initTheme() {
  const isDark = document.documentElement.classList.contains("dark");
  updateThemeIcon(isDark ? "dark" : "light");
}

function toggleTheme() {
  const isDark = document.documentElement.classList.contains("dark");
  const newTheme = isDark ? "light" : "dark";
  if (newTheme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  localStorage.setItem("soul_theme", newTheme);
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById("theme-icon");
  const btn = document.getElementById("theme-toggle-btn");
  if (icon) {
    if (theme === "dark") {
      icon.innerHTML = `<svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" stroke-width="2"/><path stroke-linecap="round" stroke-width="2" d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>`;
    } else {
      icon.innerHTML = `<svg class="w-4 h-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>`;
    }
  }
  if (btn) {
    btn.title = theme === "dark" ? "Switch to Daylight Mode" : "Switch to Obsidian Night Mode";
  }
}

// --- Tab Navigation ---
function switchTab(tabName) {
  ["playground", "keys", "snippets", "brand"].forEach(t => {
    const sec = document.getElementById(`tab-${t}`);
    const nav = document.getElementById(`nav-${t}`);
    if (t === tabName) {
      if (sec) sec.classList.remove("hidden");
      if (nav) {
        nav.className = "nav-tab active px-3.5 py-2 rounded-xl text-sm font-medium transition text-white bg-dark-800 border border-dark-700 shadow-sm flex items-center gap-2";
      }
    } else {
      if (sec) sec.classList.add("hidden");
      if (nav) {
        nav.className = "nav-tab px-3.5 py-2 rounded-xl text-sm font-medium transition text-slate-400 hover:text-white hover:bg-dark-800/60 flex items-center gap-2";
      }
    }
  });

  if (tabName === "keys") {
    loadUserApiKeys();
  }
}

function loadPreset(key) {
  const input = document.getElementById("playground-input");
  if (PRESETS[key]) {
    input.value = PRESETS[key];
  }
}

// --- Live Playground Appraisal ---
async function runAppraisal() {
  const text = document.getElementById("playground-input").value.trim();
  if (!text) return;

  const btn = document.getElementById("btn-appraise");
  btn.disabled = true;
  btn.innerHTML = "<span>Analyzing in &lt;1ms...</span>";

  try {
    const headers = { "Content-Type": "application/json" };
    if (currentToken) {
      headers["Authorization"] = `Bearer ${currentToken}`;
    }

    // Call /v1/appraise
    const t0 = performance.now();
    const appraiseRes = await fetch(`${API_BASE}/v1/appraise`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ text: text })
    });
    const t1 = performance.now();
    const appraisal = await appraiseRes.json();

    // Call /v1/harmonize
    const harmonizeRes = await fetch(`${API_BASE}/v1/harmonize`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        user_message: text,
        draft_response: "Here are practical steps to move forward with this task:\n1. Formulate an actionable plan.\n2. Review documentation.\n3. Execute each milestone."
      })
    });
    const harmonized = await harmonizeRes.json();

    displayResults(appraisal, harmonized, t1 - t0);
  } catch (err) {
    console.error("Appraisal failed:", err);
    alert("Appraisal request failed. Ensure the Soul API server is running.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>Run System 1 Appraisal (&lt;1ms)</span>`;
  }
}

function displayResults(appraisal, harmonized, networkLatency) {
  const container = document.getElementById("results-container");
  container.classList.remove("hidden");

  // KPIs
  document.getElementById("kpi-latency").innerText = `${appraisal.execution_time_ms.toFixed(2)} ms`;
  document.getElementById("kpi-adversity").innerText = appraisal.adversity.adversity_score.toFixed(2);
  document.getElementById("kpi-stance").innerText = `${appraisal.adversity.appraisal_stance.toUpperCase()} STANCE`;
  document.getElementById("kpi-domain").innerText = appraisal.adversity.primary_domain.toUpperCase();
  document.getElementById("kpi-valence").innerText = appraisal.sentiment.vad.valence.toFixed(2);
  document.getElementById("kpi-polarity").innerText = appraisal.sentiment.polarity.replace("_", " ").toUpperCase();
  document.getElementById("kpi-empathy").innerText = `${appraisal.agent_guidance.empathy_demand.toFixed(2)} / 1.0`;

  // Cold vs Attuned
  document.getElementById("cold-output").innerText = "Here are practical steps to move forward with this task:\n1. Formulate an actionable plan.\n2. Review documentation.\n3. Execute each milestone.";
  document.getElementById("attuned-output").innerText = harmonized.harmonized_content;

  // Affect Gauges
  const vad = appraisal.sentiment.vad;
  const valPct = Math.max(0, Math.min(100, (vad.valence + 1.0) * 50));
  const aroPct = Math.max(0, Math.min(100, vad.arousal * 100));
  const domPct = Math.max(0, Math.min(100, vad.dominance * 100));

  document.getElementById("bar-val").style.width = `${valPct}%`;
  document.getElementById("bar-val-text").innerText = vad.valence.toFixed(2);
  document.getElementById("bar-aro").style.width = `${aroPct}%`;
  document.getElementById("bar-aro-text").innerText = vad.arousal.toFixed(2);
  document.getElementById("bar-dom").style.width = `${domPct}%`;
  document.getElementById("bar-dom-text").innerText = vad.dominance.toFixed(2);

  // Dynamic 2D Radar Matrix Positioning
  const radarDot = document.getElementById("radar-dot");
  if (radarDot) {
    const radarX = Math.max(5, Math.min(95, (vad.valence + 1.0) * 50));
    const radarY = Math.max(5, Math.min(95, (1.0 - vad.arousal) * 100));
    radarDot.style.left = `calc(${radarX}% - 8px)`;
    radarDot.style.top = `calc(${radarY}% - 8px)`;
  }
  const coordVal = document.getElementById("coord-val");
  if (coordVal) coordVal.innerText = (vad.valence >= 0 ? "+" : "") + vad.valence.toFixed(2);
  const coordAro = document.getElementById("coord-aro");
  if (coordAro) coordAro.innerText = (vad.arousal >= 0 ? "+" : "") + vad.arousal.toFixed(2);
  const coordDom = document.getElementById("coord-dom");
  if (coordDom) coordDom.innerText = vad.dominance.toFixed(2);

  // CORE Gauges
  const core = appraisal.adversity.core;
  document.getElementById("bar-core-c-fill").style.width = `${core.control * 100}%`;
  document.getElementById("bar-core-c").innerText = core.control.toFixed(2);
  document.getElementById("bar-core-r-fill").style.width = `${core.reach * 100}%`;
  document.getElementById("bar-core-r").innerText = core.reach.toFixed(2);
  document.getElementById("bar-core-e-fill").style.width = `${core.endurance * 100}%`;
  document.getElementById("bar-core-e").innerText = core.endurance.toFixed(2);

  container.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// --- Authentication (Email & Google) ---
function openAuthModal(mode = "login") {
  authMode = mode;
  setAuthMode(mode);
  document.getElementById("auth-error-msg").classList.add("hidden");
  document.getElementById("auth-modal").classList.remove("hidden");
}

function closeAuthModal() {
  document.getElementById("auth-modal").classList.add("hidden");
}

function setAuthMode(mode) {
  authMode = mode;
  const tabLogin = document.getElementById("tab-btn-login");
  const tabSignup = document.getElementById("tab-btn-signup");
  const nameField = document.getElementById("field-fullname");
  const submitBtn = document.getElementById("btn-auth-submit");
  const title = document.getElementById("modal-title");

  if (mode === "login") {
    tabLogin.className = "flex-1 pb-2 border-b-2 border-emerald-500 text-white font-bold";
    tabSignup.className = "flex-1 pb-2 border-b-2 border-transparent text-slate-400 hover:text-slate-200";
    nameField.classList.add("hidden");
    submitBtn.innerText = "Sign In";
    title.innerText = "Sign In to Soul Engine";
  } else {
    tabSignup.className = "flex-1 pb-2 border-b-2 border-emerald-500 text-white font-bold";
    tabLogin.className = "flex-1 pb-2 border-b-2 border-transparent text-slate-400 hover:text-slate-200";
    nameField.classList.remove("hidden");
    submitBtn.innerText = "Create Account";
    title.innerText = "Create Your Soul Account";
  }
}

async function submitAuthForm(e) {
  e.preventDefault();
  const email = document.getElementById("input-email").value.trim();
  const password = document.getElementById("input-password").value;
  const fullName = document.getElementById("input-fullname").value.trim();
  const errorBox = document.getElementById("auth-error-msg");
  const submitBtn = document.getElementById("btn-auth-submit");

  errorBox.classList.add("hidden");
  submitBtn.disabled = true;

  try {
    const endpoint = authMode === "login" ? "/v1/auth/login" : "/v1/auth/signup";
    const payload = authMode === "login" 
      ? { email, password } 
      : { email, password, full_name: fullName };

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Authentication failed.");
    }

    // Save token & user
    localStorage.setItem("soul_access_token", data.access_token);
    currentToken = data.access_token;
    currentUser = data.user;

    renderAuthState();
    closeAuthModal();
    loadUserApiKeys();
  } catch (err) {
    errorBox.innerText = err.message;
    errorBox.classList.remove("hidden");
  } finally {
    submitBtn.disabled = false;
  }
}

// Google OAuth Login
async function handleGoogleSignIn() {
  const simulatedGoogleToken = prompt(
    "Enter Google OAuth ID Token (or leave blank to test with demo identity):",
    "demo_google_token"
  );
  if (simulatedGoogleToken === null) return;

  try {
    const res = await fetch(`${API_BASE}/v1/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: simulatedGoogleToken || "demo_google_token" })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Google authentication failed.");
    }

    localStorage.setItem("soul_access_token", data.access_token);
    currentToken = data.access_token;
    currentUser = data.user;

    renderAuthState();
    closeAuthModal();
    loadUserApiKeys();
  } catch (err) {
    alert("Google sign in: " + err.message);
  }
}

async function checkCurrentUser() {
  if (!currentToken) {
    renderAuthState();
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/v1/auth/me`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });

    if (res.ok) {
      currentUser = await res.json();
    } else {
      logout();
    }
  } catch (err) {
    console.error("Failed to verify current user:", err);
  } finally {
    renderAuthState();
  }
}

function logout() {
  localStorage.removeItem("soul_access_token");
  currentToken = null;
  currentUser = null;
  renderAuthState();
  loadUserApiKeys();
}

function renderAuthState() {
  const unauthBlock = document.getElementById("unauthenticated-block");
  const authBlock = document.getElementById("authenticated-block");

  if (currentUser) {
    unauthBlock.classList.add("hidden");
    authBlock.classList.remove("hidden");
    document.getElementById("user-name").innerText = currentUser.full_name || currentUser.email;
    document.getElementById("user-avatar").innerText = (currentUser.full_name || currentUser.email)[0].toUpperCase();
  } else {
    unauthBlock.classList.remove("hidden");
    authBlock.classList.add("hidden");
  }
}

// --- API Key Management ---
async function loadUserApiKeys() {
  const tbody = document.getElementById("api-keys-table-body");
  const countBadge = document.getElementById("keys-count-badge");

  if (!currentToken) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="p-8 text-center text-slate-400 font-sans text-sm">
          <p class="mb-3">Please sign in to view and manage your API keys.</p>
          <button onclick="openAuthModal('login')" class="px-4 py-2 rounded-lg bg-emerald-500 text-dark-900 font-bold text-xs hover:bg-emerald-400 transition">Sign In</button>
        </td>
      </tr>
    `;
    countBadge.innerText = "Sign in required";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/v1/keys`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    const keys = await res.json();

    countBadge.innerText = `${keys.length} Key${keys.length === 1 ? '' : 's'}`;

    if (keys.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="p-8 text-center text-slate-500 font-sans text-sm">
            No API keys found. Click "+ Create New Key" above to generate your first key.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = keys.map(k => `
      <tr class="hover:bg-dark-800/40 transition">
        <td class="p-4 text-slate-200 font-sans font-semibold">${escapeHtml(k.name)}</td>
        <td class="p-4 text-emerald-400 font-mono">${escapeHtml(k.key_prefix)}</td>
        <td class="p-4"><span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase text-[11px] font-sans">${escapeHtml(k.tier)}</span></td>
        <td class="p-4 text-slate-300 font-mono">${k.request_count} reqs</td>
        <td class="p-4 text-slate-400 font-sans">${escapeHtml(k.rate_limit)}</td>
        <td class="p-4 text-right">
          <button onclick="revokeKey('${k.id}')" class="text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 px-2 py-1 rounded transition font-sans">Revoke</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Failed to fetch keys:", err);
  }
}

function openCreateKeyModal() {
  if (!currentToken) {
    openAuthModal('login');
    return;
  }
  document.getElementById("create-key-modal").classList.remove("hidden");
}

function closeCreateKeyModal() {
  document.getElementById("create-key-modal").classList.add("hidden");
}

async function submitCreateKey() {
  const name = document.getElementById("new-key-name").value.trim() || "My API Key";
  try {
    const res = await fetch(`${API_BASE}/v1/keys`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${currentToken}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to create key.");

    closeCreateKeyModal();
    document.getElementById("new-key-name").value = "";

    // Show revealed secret
    document.getElementById("revealed-key-value").value = data.api_key;
    document.getElementById("key-revealed-banner").classList.remove("hidden");

    loadUserApiKeys();
  } catch (err) {
    alert("Create key: " + err.message);
  }
}

function copyRevealedKey() {
  const input = document.getElementById("revealed-key-value");
  input.select();
  navigator.clipboard.writeText(input.value);
  const btn = document.getElementById("btn-copy-revealed");
  btn.innerText = "Copied!";
  setTimeout(() => { btn.innerText = "Copy"; }, 2000);
}

function dismissKeyBanner() {
  document.getElementById("key-revealed-banner").classList.add("hidden");
}

async function revokeKey(keyId) {
  if (!confirm("Are you sure you want to revoke this API key? This action is permanent.")) return;

  try {
    const res = await fetch(`${API_BASE}/v1/keys/${keyId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${currentToken}` }
    });

    if (res.ok) {
      loadUserApiKeys();
    } else {
      const err = await res.json();
      alert("Revoke failed: " + (err.detail || "Unknown error"));
    }
  } catch (err) {
    alert("Revoke failed: " + err.message);
  }
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
