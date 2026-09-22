/**
 * Soul Engine SaaS Frontend Logic
 * Supports: Live System 1 Playground, User Authentication, Google Sign-In, and API Key Lifecycle.
 */

const API_BASE = window.location.origin;

// State
let currentUser = null;
let currentToken = localStorage.getItem("soul_access_token") || null;
let authMode = "login"; // "login" | "signup"
let lastAuditData = null;

// --- Sleek Toast Notification System ---
function showToast(message, type = "success", duration = 2800) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast-item ${type === "error" ? "toast-error" : "toast-success"}`;
  toast.innerHTML = `
    <span class="${type === "error" ? "text-rose-500" : "text-emerald-500"} font-bold">
      ${type === "error" ? "✕" : "✓"}
    </span>
    <span class="flex-1">${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.add("toast-show");
  });
  setTimeout(() => {
    toast.classList.remove("toast-show");
    toast.classList.add("toast-hide");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

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
  loadIdePreset("slop_copy");
  switchTab("ide");
  checkCurrentUser();

  const editor = document.getElementById("ide-editor");
  if (editor) {
    editor.addEventListener("input", () => {
      updateEditorStats();
      debounceIdeAudit();
    });
    editor.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        runIdeAudit();
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "H" || e.key === "h")) {
        e.preventDefault();
        sanitizeInIde();
      }
    });
  }

  // Global ESC key to dismiss modals
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAuthModal();
      closeCreateKeyModal();
    }
  });

  // Backdrop click dismissal
  ["auth-modal", "create-key-modal"].forEach(id => {
    const modal = document.getElementById(id);
    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          modal.classList.add("hidden");
        }
      });
    }
  });
});

let ideDebounceTimer = null;
function debounceIdeAudit() {
  clearTimeout(ideDebounceTimer);
  ideDebounceTimer = setTimeout(runIdeAudit, 350);
}

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
  showToast(newTheme === "dark" ? "Switched to Obsidian Night Mode" : "Switched to Daylight Mode");
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
  ["ide", "playground", "keys", "snippets"].forEach(t => {
    const sec = document.getElementById(`tab-${t}`);
    const nav = document.getElementById(`nav-${t}`);
    const mobNav = document.getElementById(`mobile-nav-${t}`);

    if (t === tabName) {
      if (sec) sec.classList.remove("hidden");
      if (nav) {
        nav.className = "nav-tab active px-3.5 py-2 rounded-xl text-sm font-semibold transition text-slate-900 dark:text-white bg-slate-100 dark:bg-dark-800 border border-slate-200 dark:border-dark-700 shadow-sm flex items-center gap-2";
      }
      if (mobNav) {
        mobNav.className = "mobile-nav-pill active flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/15 whitespace-nowrap";
      }
    } else {
      if (sec) sec.classList.add("hidden");
      if (nav) {
        nav.className = "nav-tab px-3.5 py-2 rounded-xl text-sm font-medium transition text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-dark-800/60 flex items-center gap-2";
      }
      if (mobNav) {
        mobNav.className = "mobile-nav-pill flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white whitespace-nowrap";
      }
    }
  });

  if (tabName === "keys") {
    loadUserApiKeys();
  }
  if (tabName === "ide") {
    updateEditorStats();
    runIdeAudit();
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
  if (!text) {
    showToast("Please enter text to appraise", "error");
    return;
  }

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
    if (!appraiseRes.ok) throw new Error("Appraisal request failed");
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
    showToast(`System 1 evaluated in ${appraisal.execution_time_ms.toFixed(2)}ms`);
  } catch (err) {
    console.error("Appraisal failed:", err);
    showToast("Appraisal request failed. Ensure the Soul API server is running.", "error");
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

// Interactive click simulation on Russell radar
function handleRadarClick(e) {
  const container = document.getElementById("radar-matrix-container");
  if (!container) return;
  const rect = container.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;
  
  const valence = ((clickX / rect.width) * 2 - 1);
  const arousal = (1 - (clickY / rect.height));
  
  const clampedVal = Math.max(-1, Math.min(1, valence));
  const clampedAro = Math.max(0, Math.min(1, arousal));
  
  const radarDot = document.getElementById("radar-dot");
  if (radarDot) {
    radarDot.style.left = `calc(${(clampedVal + 1) * 50}% - 8px)`;
    radarDot.style.top = `calc(${(1 - clampedAro) * 100}% - 8px)`;
  }
  
  const coordVal = document.getElementById("coord-val");
  if (coordVal) coordVal.innerText = (clampedVal >= 0 ? "+" : "") + clampedVal.toFixed(2);
  const coordAro = document.getElementById("coord-aro");
  if (coordAro) coordAro.innerText = (clampedAro >= 0 ? "+" : "") + clampedAro.toFixed(2);
  
  const barVal = document.getElementById("bar-val");
  if (barVal) barVal.style.width = `${(clampedVal + 1) * 50}%`;
  const barValText = document.getElementById("bar-val-text");
  if (barValText) barValText.innerText = clampedVal.toFixed(2);
  
  const barAro = document.getElementById("bar-aro");
  if (barAro) barAro.style.width = `${clampedAro * 100}%`;
  const barAroText = document.getElementById("bar-aro-text");
  if (barAroText) barAroText.innerText = clampedAro.toFixed(2);
  
  showToast(`Simulated: Valence ${clampedVal.toFixed(2)}, Arousal ${clampedAro.toFixed(2)}`);
}

function copyAttunedOutput() {
  const el = document.getElementById("attuned-output");
  if (!el || !el.innerText.trim()) return;
  navigator.clipboard.writeText(el.innerText);
  showToast("Copied harmonized AI response to clipboard!");
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
    showToast(`Welcome ${currentUser.full_name || currentUser.email}!`);
  } catch (err) {
    errorBox.innerText = err.message;
    errorBox.classList.remove("hidden");
  } finally {
    submitBtn.disabled = false;
  }
}

// Google OAuth Login
async function handleGoogleSignIn() {
  try {
    const res = await fetch(`${API_BASE}/v1/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: "demo_google_token" })
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
    showToast("Signed in with Google identity!");
  } catch (err) {
    showToast("Google sign in: " + err.message, "error");
  }
}

// Quick 1-Click Demo Account Sign In
async function loginDemoAccount() {
  const email = `demo_dev_${Math.floor(Math.random() * 9000 + 1000)}@soul.dev`;
  const password = "demopassword123";
  try {
    const res = await fetch(`${API_BASE}/v1/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: "Demo Developer" })
    });
    const data = await res.json();
    if (res.ok && data.access_token) {
      localStorage.setItem("soul_access_token", data.access_token);
      currentToken = data.access_token;
      currentUser = data.user;
      renderAuthState();
      closeAuthModal();
      loadUserApiKeys();
      showToast("Signed in as Demo Developer! API keys unlocked.");
    } else {
      throw new Error(data.detail || "Demo sign in failed");
    }
  } catch (err) {
    showToast("Demo sign in error: " + err.message, "error");
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
    showToast("Secret Soul API Key generated!");
  } catch (err) {
    showToast("Create key error: " + err.message, "error");
  }
}

function copyRevealedKey() {
  const input = document.getElementById("revealed-key-value");
  input.select();
  navigator.clipboard.writeText(input.value);
  const btn = document.getElementById("btn-copy-revealed");
  btn.innerText = "Copied!";
  showToast("Secret API Key copied to clipboard!");
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
      showToast("API Key successfully revoked.");
    } else {
      const err = await res.json();
      showToast("Revoke failed: " + (err.detail || "Unknown error"), "error");
    }
  } catch (err) {
    showToast("Revoke failed: " + err.message, "error");
  }
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// --- Soul IDE Workbench Logic ---
const IDE_PRESETS = {
  slop_copy: "In today's fast-paced digital landscape—efficiency is paramount. 🚀 Delve into our multifaceted ecosystem to harness your true synergy. It is important to note that our revolutionary tool will elevate your workflow—effortlessly!\n\n- Step 1: Optimize your profile\n- Step 2: Implement micro-actions\n- Step 3: Unleash your potential",
  cold_support: "Here are the practical steps to resolve this task:\n1. Verify error code 503.\n2. Submit a formal ticket.\n3. The company is not liable for data loss. We will review your case within 7 business days.",
  ai_purple_css: "<div class=\"bg-[#0b0f19] text-white from-purple-600 to-indigo-600 border-[#7c3aed] backdrop-blur-md\">\n  <h2 class=\"text-[#00ff66]\">🚀 Launching Future</h2>\n  <p>In today's fast-paced world—experience true synergy.</p>\n</div>",
  high_distress: "I was just laid off with zero notice after 8 years at the company. I have two kids to feed and I am in total shock and panic. How do I even start updating my resume?"
};

let lastCleanAlternative = "";

function loadIdePreset(key) {
  const editor = document.getElementById("ide-editor");
  const sel = document.getElementById("ide-preset-select");
  if (sel && sel.value !== key) sel.value = key;
  if (editor && IDE_PRESETS[key]) {
    editor.value = IDE_PRESETS[key];
    updateEditorStats();
    runIdeAudit();
  }
}

function updateEditorStats() {
  const editor = document.getElementById("ide-editor");
  if (!editor) return;
  const text = editor.value;
  const lines = text ? text.split("\n").length : 0;
  const chars = text.length;
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  
  // Reading time at ~200 WPM
  const readingSeconds = Math.max(1, Math.round((words / 200) * 60));
  const readingTimeStr = words > 0 ? (readingSeconds < 60 ? `~${readingSeconds}s read` : `~${Math.ceil(readingSeconds / 60)}m read`) : "~0s read";

  const statsEl = document.getElementById("ide-editor-stats");
  if (statsEl) {
    statsEl.innerText = `${lines} line${lines === 1 ? '' : 's'} | ${words} word${words === 1 ? '' : 's'} | ${chars} char${chars === 1 ? '' : 's'} | ${readingTimeStr}`;
  }

  const gutterEl = document.getElementById("ide-gutter");
  if (gutterEl) {
    const lineCount = Math.max(14, lines);
    let gutterHtml = "";
    for (let i = 1; i <= lineCount; i++) {
      gutterHtml += (i < 10 ? "0" + i : i) + "<br>";
    }
    gutterEl.innerHTML = gutterHtml;
  }
}

async function runIdeAudit() {
  const editor = document.getElementById("ide-editor");
  if (!editor) return;
  const content = editor.value.trim();
  if (!content) return;

  const statusEl = document.getElementById("ide-audit-status");
  if (statusEl) statusEl.innerText = "Auditing...";

  try {
    const res = await fetch(`${API_BASE}/v1/audit/human-pov`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, include_aesthetics: true })
    });

    if (!res.ok) throw new Error("Audit failed");
    const data = await res.json();
    lastAuditData = data;
    renderIdeScorecard(data);
    if (statusEl) statusEl.innerText = "Live Synchronized";
  } catch (err) {
    console.error(err);
    if (statusEl) statusEl.innerText = "Audit ready";
  }
}

function renderIdeScorecard(data) {
  lastAuditData = data;

  // Score gauge
  const scoreVal = document.getElementById("ide-score-val");
  const scoreBar = document.getElementById("ide-score-bar");
  const scoreBadge = document.getElementById("ide-score-badge");
  
  if (scoreVal) scoreVal.innerText = `${data.overall_human_score}`;
  if (scoreBar) scoreBar.style.width = `${data.overall_human_score}%`;
  
  if (scoreBadge) {
    scoreBadge.innerText = data.status;
    if (data.status === "AUTHENTIC_HUMAN_CRAFT") {
      scoreBadge.className = "text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/30";
      if (scoreBar) scoreBar.className = "h-full bg-emerald-500 rounded-full transition-all duration-500";
    } else if (data.status === "STERILE_ROBOTIC") {
      scoreBadge.className = "text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-500 border border-amber-500/30";
      if (scoreBar) scoreBar.className = "h-full bg-amber-500 rounded-full transition-all duration-500";
    } else {
      scoreBadge.className = "text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-500 border border-rose-500/30";
      if (scoreBar) scoreBar.className = "h-full bg-rose-500 rounded-full transition-all duration-500";
    }
  }

  // Emoji count
  const emojiEl = document.getElementById("ide-emoji-val");
  const slop = data.slop_audit;
  if (emojiEl) {
    if (slop.emoji_icon_count > 0) {
      emojiEl.innerHTML = `<span class="text-rose-500 font-bold">${slop.emoji_icon_count} detected</span> <span class="text-xs text-slate-500">(${slop.emojis_found.join(" ")})</span>`;
    } else {
      emojiEl.innerHTML = `<span class="text-emerald-500 font-bold">0</span> <span class="text-xs text-slate-500">(Clean)</span>`;
    }
  }

  // Em-dashes
  const dashEl = document.getElementById("ide-dash-val");
  if (dashEl) {
    if (slop.em_dash_count >= 2) {
      dashEl.innerHTML = `<span class="text-rose-500 font-bold">${slop.em_dash_count}</span> <span class="text-xs text-rose-400 font-medium">(Dense)</span>`;
    } else {
      dashEl.innerHTML = `<span class="text-emerald-500 font-bold">${slop.em_dash_count}</span> <span class="text-xs text-slate-500">(Natural)</span>`;
    }
  }

  // AI Cliches
  const clichesEl = document.getElementById("ide-cliches-val");
  if (clichesEl) {
    if (slop.ai_cliches_found && slop.ai_cliches_found.length > 0) {
      clichesEl.innerHTML = slop.ai_cliches_found.map(c => `<span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-mono slop-tag">${c}</span>`).join(" ");
    } else {
      clichesEl.innerHTML = `<span class="text-xs text-emerald-500 font-medium">None detected (Human voice)</span>`;
    }
  }

  // Cognitive Breathing Room
  const breathEl = document.getElementById("ide-breathing-val");
  if (breathEl) {
    const isSuffocating = data.cognitive_friction_score > 0.5;
    breathEl.innerHTML = `<span class="${isSuffocating ? 'text-rose-500' : 'text-emerald-500'} font-bold">${data.sensory_breathing_room.split('(')[0]}</span> <span class="text-xs text-slate-500">(Friction: ${data.cognitive_friction_score})</span>`;
  }

  // Criticisms & Prescriptions
  const critList = document.getElementById("ide-crit-list");
  if (critList) {
    if (data.key_criticisms && data.key_criticisms.length > 0) {
      critList.innerHTML = data.key_criticisms.map(c => `<li class="text-xs text-rose-600 dark:text-rose-400 flex items-start gap-1.5"><span class="text-rose-500 font-bold">•</span><span>${escapeHtml(c)}</span></li>`).join("");
    } else {
      critList.innerHTML = `<li class="text-xs text-emerald-600 dark:text-emerald-400">✓ No sensory disconnects detected.</li>`;
    }
  }

  const prescList = document.getElementById("ide-presc-list");
  if (prescList) {
    if (data.actionable_prescriptions && data.actionable_prescriptions.length > 0) {
      prescList.innerHTML = data.actionable_prescriptions.map(p => `<li class="text-xs text-emerald-600 dark:text-emerald-400 flex items-start gap-1.5"><span class="text-emerald-500 font-bold">✓</span><span>${escapeHtml(p)}</span></li>`).join("");
    } else {
      prescList.innerHTML = `<li class="text-xs text-slate-500">Ready for production.</li>`;
    }
  }

  // Aesthetics / Palette check
  const paletteBox = document.getElementById("ide-palette-box");
  if (paletteBox) {
    if (data.aesthetic_audit && data.aesthetic_audit.has_generic_ai_purple) {
      paletteBox.classList.remove("hidden");
      const rec = data.aesthetic_audit.recommended_palette;
      const descEl = document.getElementById("ide-palette-desc");
      if (descEl) descEl.innerText = `Detected AI Purple/Neon. Recommended: ${rec.name} (${rec.description})`;
    } else {
      paletteBox.classList.add("hidden");
    }
  }

  // Harmonized Alternative
  lastCleanAlternative = data.humanized_alternative || "";
  const altBox = document.getElementById("ide-alternative-box");
  const altText = document.getElementById("ide-alternative-text");
  const editor = document.getElementById("ide-editor");
  if (altBox && altText && editor) {
    if (data.humanized_alternative && data.humanized_alternative.trim() !== editor.value.trim()) {
      altBox.classList.remove("hidden");
      altText.innerText = data.humanized_alternative;
    } else {
      altBox.classList.add("hidden");
    }
  }
}

async function sanitizeInIde() {
  const editor = document.getElementById("ide-editor");
  if (!editor) return;
  const text = editor.value.trim();
  if (!text) {
    showToast("Editor is empty", "error");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/v1/sanitize/anti-slop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (res.ok) {
      const data = await res.json();
      editor.value = data.sanitized;
      updateEditorStats();
      runIdeAudit();
      showToast("Slop eradicated and sanitized cleanly!");
    } else {
      showToast("Sanitization failed", "error");
    }
  } catch (err) {
    console.error(err);
    showToast("Sanitization error: " + err.message, "error");
  }
}

function replaceEditorWithClean() {
  const editor = document.getElementById("ide-editor");
  if (editor && lastCleanAlternative) {
    editor.value = lastCleanAlternative;
    updateEditorStats();
    runIdeAudit();
    showToast("Harmonized alternative applied to editor!");
  }
}

function copyCleanAlternative() {
  if (!lastCleanAlternative) return;
  navigator.clipboard.writeText(lastCleanAlternative);
  showToast("Clean alternative copied to clipboard!");
}

function copyEditorContent() {
  const editor = document.getElementById("ide-editor");
  if (!editor || !editor.value.trim()) {
    showToast("Editor is empty", "error");
    return;
  }
  navigator.clipboard.writeText(editor.value);
  showToast("Editor content copied to clipboard!");
}

function resetIdeEditor() {
  const editor = document.getElementById("ide-editor");
  if (!editor) return;
  editor.value = "";
  updateEditorStats();
  const altBox = document.getElementById("ide-alternative-box");
  if (altBox) altBox.classList.add("hidden");
  const paletteBox = document.getElementById("ide-palette-box");
  if (paletteBox) paletteBox.classList.add("hidden");
  const scoreVal = document.getElementById("ide-score-val");
  if (scoreVal) scoreVal.innerText = "--";
  const scoreBar = document.getElementById("ide-score-bar");
  if (scoreBar) scoreBar.style.width = "0%";
  const scoreBadge = document.getElementById("ide-score-badge");
  if (scoreBadge) {
    scoreBadge.innerText = "Awaiting Content";
    scoreBadge.className = "text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-dark-800 text-slate-500";
  }
  showToast("Editor cleared.");
}

function exportIdeAuditJson() {
  if (!lastAuditData) {
    showToast("Run an audit first to generate report", "error");
    return;
  }
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(lastAuditData, null, 2));
  const downloadAnchor = document.createElement("a");
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `soul_human_feel_audit_${Date.now()}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
  showToast("Diagnostic report downloaded (.json)");
}

function copyCodeSnippet(btn) {
  const codeBlock = btn.closest(".code-box-wrapper")?.querySelector("code");
  if (!codeBlock) return;
  navigator.clipboard.writeText(codeBlock.innerText);
  const span = btn.querySelector("span");
  const prev = span ? span.innerText : "Copy";
  if (span) span.innerText = "Copied!";
  showToast("Code copied to clipboard!");
  setTimeout(() => {
    if (span) span.innerText = prev;
  }, 2000);
}

function copyHexCode(hex, name) {
  navigator.clipboard.writeText(hex);
  showToast(`Copied ${name} (${hex}) to clipboard!`);
}


