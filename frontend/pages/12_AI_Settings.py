"""Page 12: AI API Key Settings"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from backend.services.ai_client import (
    get_gemini_api_key, get_openai_api_key,
    verify_gemini_connection, is_ai_configured
)

st.set_page_config(
    page_title="AI Settings | Placement Copilot",
    page_icon="⚙️",
    layout="wide",
)
inject_css()

# Override styling to match the premium dark gold/beige design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,0..700&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* ── Typography ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
}
p, li, label, .stMarkdown, .sidebar-logo, .sidebar-section-label {
    font-family: 'Lora', serif !important;
}

/* Exclude Material Symbols from generic overrides to prevent text rendering */
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp {
    font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Symbols Sharp' !important;
}

/* ── Layout ──────────────────────────────────────────────────────────────────── */
.stApp {
    background: radial-gradient(circle at top left, #151811 0%, #0a0c08 50%, #030403 100%) !important;
}
header {
    visibility: visible !important;
    background: transparent !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #090a07 !important;
    border-right: 1px solid rgba(212, 175, 55, 0.15) !important;
}

/* Style native Streamlit expand/collapse icons */
[data-testid="collapsedControl"] button,
button[data-testid="stSidebarCollapseButton"] {
    color: #d4af37 !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
}
[data-testid="collapsedControl"] button svg,
button[data-testid="stSidebarCollapseButton"] svg {
    fill: #d4af37 !important;
    color: #d4af37 !important;
}
[data-testid="collapsedControl"] button:hover,
button[data-testid="stSidebarCollapseButton"]:hover {
    background-color: rgba(212, 175, 55, 0.1) !important;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# Custom Sidebar
with st.sidebar:
    st.page_link("app.py", label="Home Dashboard", icon="🏠")
    st.markdown("---")
    st.markdown("### 🔌 AI Status")
    if is_ai_configured():
        st.success("🟢 Gemini Connected")
    else:
        st.warning("🔴 Running in Demo Mode")

st.markdown("""
<div class="hero-section">
    <div class="hero-title">⚙️ AI API Key Settings</div>
    <p class="hero-subtitle">Configure your API keys safely to unlock the full AI-powered functionalities</p>
</div>
""", unsafe_allow_html=True)

# Main Form
col_form, col_status = st.columns([3, 2])

# Retrieve initial keys
initial_gemini = st.session_state.get("gemini_api_key") or ""
initial_openai = st.session_state.get("openai_api_key") or ""

# If not in session state, check if available in environment/secrets (mask it)
if not initial_gemini and get_gemini_api_key():
    initial_gemini = "••••••••••••••••••••"
if not initial_openai and get_openai_api_key():
    initial_openai = "••••••••••••••••••••"

with col_form:
    st.markdown('<div class="section-header"><div class="section-icon">🔑</div><h3 class="section-title">Configure Credentials</h3></div>', unsafe_allow_html=True)

    gemini_input = st.text_input(
        "Google Gemini API Key",
        value=initial_gemini,
        type="password",
        placeholder="AIzaSy...",
        help="Required for AI-powered resume analysis, mock interviews, and roadmap generation.",
    )

    openai_input = st.text_input(
        "OpenAI API Key (Optional Fallback)",
        value=initial_openai,
        type="password",
        placeholder="sk-...",
        help="Optional fallback API key for AI features.",
    )

    remember_me = st.checkbox(
        "Remember credentials for this browser session",
        value=st.session_state.get("remember_keys", True),
        help="Keeps keys stored in memory during the active session. Keys are never saved to disk."
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        save_btn = st.button("💾 Save Credentials", use_container_width=True, type="primary")
    with col_btn2:
        test_btn = st.button("🧪 Test Gemini Connection", use_container_width=True)

    if save_btn:
        # Validate and clean keys
        clean_gemini = gemini_input.strip()
        clean_openai = openai_input.strip()

        # Handle masked indicators (don't overwrite if unchanged)
        if clean_gemini == "••••••••••••••••••••":
            clean_gemini = st.session_state.get("gemini_api_key") or get_gemini_api_key()
        if clean_openai == "••••••••••••••••••••":
            clean_openai = st.session_state.get("openai_api_key") or get_openai_api_key()

        # Check for accidental enclosing quotes
        if (clean_gemini.startswith('"') and clean_gemini.endswith('"')) or (clean_gemini.startswith("'") and clean_gemini.endswith("'")):
            clean_gemini = clean_gemini[1:-1]
        if (clean_openai.startswith('"') and clean_openai.endswith('"')) or (clean_openai.startswith("'") and clean_openai.endswith("'")):
            clean_openai = clean_openai[1:-1]

        st.session_state.gemini_api_key = clean_gemini
        st.session_state.openai_api_key = clean_openai
        st.session_state.remember_keys = remember_me
        st.success("✅ Credentials saved successfully in active session state!")
        st.rerun()

    if test_btn:
        testing_key = gemini_input.strip()
        if testing_key == "••••••••••••••••••••":
            testing_key = st.session_state.get("gemini_api_key") or get_gemini_api_key()
            
        if not testing_key:
            st.error("❌ Please provide a Gemini API key to test.")
        else:
            with st.spinner("Connecting to Google Gemini API..."):
                success, msg = verify_gemini_connection(testing_key)
                if success:
                    st.success("✅ Connection Successful! The key is valid.")
                else:
                    st.error(f"❌ Connection Failed: {msg}")

with col_status:
    st.markdown('<div class="section-header"><div class="section-icon">📡</div><h3 class="section-title">Connection Status</h3></div>', unsafe_allow_html=True)
    
    # Calculate status cards
    is_gemini_active = bool(get_gemini_api_key())
    is_openai_active = bool(get_openai_api_key())
    
    if is_gemini_active:
        st.markdown("""
        <div style="background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.15);
             border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1rem;">
            <h4 style="color:#22c55e; margin:0 0 0.5rem 0;">🟢 Gemini Connected</h4>
            <p style="color:#9898b0; font-size:0.85rem; margin:0;">
                The platform is fully active. Gemini API will be used to analyze resumes, run mocks, and answer career queries.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.15);
             border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1rem;">
            <h4 style="color:#ef4444; margin:0 0 0.5rem 0;">🔴 Gemini Disconnected</h4>
            <p style="color:#9898b0; font-size:0.85rem; margin:0;">
                Provide a Google Gemini key to enable AI-powered ranking, mock interviews, and roadmap curriculums.
            </p>
        </div>
        """, unsafe_allow_html=True)

    if is_openai_active:
        st.markdown("""
        <div style="background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.15);
             border-radius: 12px; padding: 1.5rem; text-align: center;">
            <h4 style="color:#22c55e; margin:0 0 0.5rem 0;">🟢 OpenAI Configured</h4>
            <p style="color:#9898b0; font-size:0.85rem; margin:0;">
                OpenAI key is ready and will serve as an automatic fallback if Gemini encounters rate-limiting or quota errors.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(249,115,22,0.06); border: 1px solid rgba(249,115,22,0.15);
             border-radius: 12px; padding: 1.5rem; text-align: center;">
            <h4 style="color:#f97316; margin:0 0 0.5rem 0;">🟡 OpenAI Not Configured</h4>
            <p style="color:#9898b0; font-size:0.85rem; margin:0;">
                No OpenAI key configured. Fallbacks will not be available.
            </p>
        </div>
        """, unsafe_allow_html=True)
