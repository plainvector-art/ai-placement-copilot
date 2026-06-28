"""
AI Interview & Placement Copilot
Main Streamlit Application Entry Point
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from frontend.components.styles import inject_css
from backend.services.skill_analyzer import get_available_roles

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Placement Copilot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Override styling to match the premium gold and deep emerald bento design
st.markdown("""
<style>
/* ── Typography ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
}
p, li, label, .stMarkdown, .premium-card-title, .premium-card-desc, .sidebar-logo, .sidebar-section-label {
    font-family: 'Inter', sans-serif !important;
}

/* Exclude Material Symbols from generic overrides to prevent text rendering */
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp {
    font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Symbols Sharp' !important;
}

/* ── Layout ──────────────────────────────────────────────────────────────────── */
header {
    visibility: visible !important;
    background: transparent !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0e0e0e !important;
    border-right: 1px solid rgba(233, 193, 118, 0.1) !important;
}

/* ── Cards ───────────────────────────────────────────────────────────────────── */
.premium-card {
    background: rgba(27, 48, 34, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 1.5rem 1rem !important;
    text-align: center !important;
    margin-bottom: 1rem !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    cursor: pointer !important;
    height: 180px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 0.5rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
}
.premium-card:hover {
    border-color: rgba(233, 193, 118, 0.25) !important;
    transform: translateY(-4px) !important;
    background: rgba(27, 48, 34, 0.4) !important;
    box-shadow: 0 8px 24px rgba(233, 193, 118, 0.15) !important;
}
.premium-card-icon-container {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(233,193,118,0.08) 0%, rgba(233,193,118,0) 70%);
    border: 1px solid rgba(233,193,118,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.25rem;
}
.premium-card-icon-inner {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 1px solid rgba(233,193,118,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
    color: #e9c176;
}
.premium-card-title {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #e5e2e1 !important;
    letter-spacing: 0.01em !important;
}
.premium-card-desc {
    font-size: 0.72rem !important;
    color: #8d928c !important;
    line-height: 1.45 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State Initialization ──────────────────────────────────────────────
if "db_initialized" not in st.session_state:
    from backend.database.db import init_db
    init_db()
    st.session_state.db_initialized = True

if "discovered_gemini_models" not in st.session_state:
    from backend.services.ai_client import discover_gemini_models, get_best_available_model
    discovered = discover_gemini_models()
    st.session_state.discovered_gemini_models = discovered
    st.session_state.gemini_model = get_best_available_model(discovered)

if "profile" not in st.session_state:
    st.session_state.profile = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "ats_score" not in st.session_state:
    st.session_state.ats_score = None
if "skill_gap" not in st.session_state:
    st.session_state.skill_gap = None
if "target_role" not in st.session_state:
    st.session_state.target_role = "Software Engineer"
if "readiness_score" not in st.session_state:
    st.session_state.readiness_score = None
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None
if "mock_session" not in st.session_state:
    st.session_state.mock_session = None
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">🎯 Placement Copilot</div>',
        unsafe_allow_html=True,
    )

    # Profile Status
    if st.session_state.profile:
        name = st.session_state.profile.get("name", "Candidate")
        st.markdown(f"""
        <div style="background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.15);
             border-radius: 10px; padding: 0.875rem; margin-bottom: 1rem;">
            <div style="font-size:0.75rem;color:#8c8577;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.25rem;">
                Active Profile
            </div>
            <div style="font-size:1rem;font-weight:700;color:#e6dfd3;">{name}</div>
            <div style="font-size:0.8rem;color:#8c8577;margin-top:0.15rem;">
                {len(st.session_state.profile.get('skills', []))} skills · 
                {len(st.session_state.profile.get('projects', []))} projects
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Target Role Selector
    st.markdown('<div class="sidebar-section-label">Target Role</div>', unsafe_allow_html=True)
    try:
        roles = get_available_roles()
    except Exception:
        roles = ["Software Engineer", "Data Analyst", "Data Scientist", "AI Engineer", "ML Engineer"]

    selected_role = st.selectbox(
        "Target Role",
        options=roles,
        index=roles.index(st.session_state.target_role) if st.session_state.target_role in roles else 0,
        label_visibility="collapsed",
    )
    if selected_role != st.session_state.target_role:
        st.session_state.target_role = selected_role
        # Reset dependent state
        st.session_state.skill_gap = None
        st.session_state.readiness_score = None

    st.markdown("---")

    # Quick Stats
    if st.session_state.ats_score:
        ats = st.session_state.ats_score.get("overall_score", 0)
        st.markdown('<div class="sidebar-section-label">Quick Stats</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("ATS", f"{ats:.0f}")
        with col2:
            if st.session_state.readiness_score:
                rs = st.session_state.readiness_score.get("overall_score", 0)
                st.metric("Readiness", f"{rs:.0f}%")

        if st.session_state.skill_gap:
            coverage = st.session_state.skill_gap.get("coverage", {}).get("overall", 0)
            st.metric("Skill Coverage", f"{coverage:.0f}%")

    st.markdown("---")

    # AI Connection Status inside sidebar
    st.markdown('<div class="sidebar-section-label">AI Connection</div>', unsafe_allow_html=True)
    from backend.services.ai_client import is_ai_configured
    if is_ai_configured():
        st.markdown("""
        <div style="background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.15);
             border-radius: 8px; padding: 0.6rem; margin-bottom: 0.5rem; text-align: center;">
            <span style="color:#22c55e; font-size:0.82rem; font-weight:600;">🟢 Gemini Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.15);
             border-radius: 8px; padding: 0.6rem; margin-bottom: 0.5rem; text-align: center;">
            <span style="color:#ef4444; font-size:0.82rem; font-weight:600;">🔴 No API Key (Demo)</span>
        </div>
        """, unsafe_allow_html=True)
    st.page_link("pages/12_AI_Settings.py", label="🔑 AI API Settings", use_container_width=True)

    st.markdown("---")

    # Navigation Info
    st.markdown("""
    <div style="font-size:0.75rem;color:#5c564c;line-height:1.8;">
        <b style="color:#8c8577;">Navigation</b><br>
        Use the sidebar pages above to navigate.<br><br>
        Start with <b style="color:#d4af37;">Resume Analysis</b> to upload your resume.
    </div>
    """, unsafe_allow_html=True)


# ── Main Content ───────────────────────────────────────────────────────────────

# Homepage Banner warning if API keys are missing
from backend.services.ai_client import has_api_key
if not has_api_key():
    if st.session_state.get("dismiss_api_warning") is not True:
        col_warn_text, col_warn_btn1, col_warn_btn2 = st.columns([6, 2, 2])
        with col_warn_text:
            st.warning("⚠️ **AI features require a Gemini API key.** Running in Demo Mode with limited mock outputs.")
        with col_warn_btn1:
            if st.button("Configure API", use_container_width=True, key="banner_cfg_btn"):
                st.switch_page("pages/12_AI_Settings.py")
        with col_warn_btn2:
            if st.button("Dismiss", use_container_width=True, key="banner_dismiss_btn"):
                st.session_state.dismiss_api_warning = True
                st.rerun()


# Calculate values dynamically
profile = st.session_state.get("profile")
ats = st.session_state.get("ats_score")
readiness = st.session_state.get("readiness_score")
target_role = st.session_state.get("target_role", "Software Engineer")

name = "Alexander"
if profile and profile.get("name"):
    name = profile.get("name")
skills_count = len(profile.get("skills", [])) if profile else 0
projects_count = len(profile.get("projects", [])) if profile else 0

# Calculate score
score_value = 0.0
score_label = "N/A"
if readiness:
    score_value = readiness.get("overall_score", 0.0)
    score_label = f"{score_value:.0f}%"
elif ats:
    score_value = ats.get("overall_score", 0.0)
    score_label = f"{score_value:.0f}%"
else:
    score_value = 88.0 # Default mockup value
    score_label = "88%"

# Calculate offset for SVG gauge (circumference = 314.16 for r=50)
stroke_offset = 314.16
if score_value > 0:
    stroke_offset = 314.16 * (1 - score_value / 100.0)

# Render Custom CSS Grid styled Bento Cards
st.markdown(f"""
<div class="bento-grid" style="display: grid; grid-template-columns: repeat(12, 1fr); gap: 20px; margin-top: 1rem; margin-bottom: 2rem;">
    <!-- Hello Card (col-span-8) -->
    <div class="glass-module rounded-3xl p-8 bento-card animate-delay-1 flex flex-col justify-between" style="grid-column: span 8; min-height: 280px; position: relative; display: flex; flex-direction: column; justify-content: space-between; border-radius: 24px; padding: 2rem;">
        <div style="z-index: 10;">
            <h2 style="font-size: 2.2rem; font-weight: 800; color: #e5e2e1; margin: 0 0 0.5rem 0; font-family: 'Inter', sans-serif;">Hello, {name}.</h2>
            <p style="color: #c3c8c1; font-size: 1.05rem; margin: 0 0 1.5rem 0; max-width: 480px; line-height: 1.6; font-family: 'Inter', sans-serif;">
                Your Cognitive Agent has analyzed <span style="color: #e9c176; font-weight: 600;">{skills_count if profile else 14} skills</span> and <span style="color: #e9c176; font-weight: 600;">{projects_count if profile else 3} matches</span>. 
                {"Your profile is active and optimized." if profile else "Your deep tech profile has analyzed 14 new openings today."}
            </p>
        </div>
        <div style="display: flex; gap: 12px; z-index: 10;">
            <a href="/Resume_Analysis" target="_self" style="text-decoration: none;">
                <button class="breathing-button" style="background: #e9c176; color: #1b3022; border: none; border-radius: 12px; font-weight: 700; padding: 0.75rem 1.5rem; cursor: pointer; transition: all 0.3s; font-family: 'Inter', sans-serif;">
                    Review Match
                </button>
            </a>
            <a href="/Resume_Analysis" target="_self" style="text-decoration: none;">
                <button style="background: rgba(255,255,255,0.05); color: #e5e2e1; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; font-weight: 600; padding: 0.75rem 1.5rem; cursor: pointer; transition: all 0.3s; font-family: 'Inter', sans-serif;">
                    Dismiss
                </button>
            </a>
        </div>
        <div style="position: absolute; right: 0; top: 0; bottom: 0; width: 35%; opacity: 0.25; pointer-events: none; display: flex; align-items: center; justify-content: center;">
            <svg viewBox="0 0 100 100" style="width: 100%; height: 100%;">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e9c176" stroke-width="0.75" stroke-dasharray="2 4"></circle>
                <circle cx="50" cy="50" r="30" fill="none" stroke="#b4cdb8" stroke-width="0.5"></circle>
                <path d="M 50 10 L 50 90 M 10 50 L 90 50" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"></path>
            </svg>
        </div>
    </div>

    <!-- Success Ratio Card (col-span-4) -->
    <div class="glass-module rounded-3xl p-8 bento-card animate-delay-2 flex flex-col items-center justify-center text-center" style="grid-column: span 4; min-height: 280px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-radius: 24px; padding: 2rem;">
        <div style="position: relative; width: 120px; height: 120px; margin-bottom: 1rem;">
            <svg style="width: 100%; height: 100%; transform: rotate(-90deg);">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="8"></circle>
                <circle class="circular-gauge" cx="60" cy="60" r="50" fill="none" stroke="#e9c176" stroke-width="8" 
                        stroke-dasharray="314.16" stroke-dashoffset="{stroke_offset}" stroke-linecap="round"></circle>
            </svg>
            <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1.8rem; font-weight: 900; color: #e5e2e1; font-family: 'Inter', sans-serif;">{score_label}</span>
            </div>
        </div>
        <h3 style="font-size: 1.15rem; color: #e9c176; margin: 0 0 0.25rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">Success Ratio</h3>
        <p style="color: #8d928c; font-size: 0.85rem; margin: 0; font-family: 'Inter', sans-serif;">Trending up 4% this week</p>
    </div>

    <!-- Shadow Profiles Card (col-span-5) -->
    <div class="glass-module rounded-3xl p-8 bento-card animate-delay-3" style="grid-column: span 5; min-height: 320px; border-radius: 24px; padding: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.15rem; color: #FAF9F6; margin: 0; font-family: 'Inter', sans-serif; font-weight: 700;">Shadow Profiles</h3>
            <span class="material-symbols-outlined" style="color: #e9c176; font-size: 20px;">diversity_3</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <!-- Active role -->
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; background: rgba(27, 48, 34, 0.2); border-radius: 16px; border: 1px solid rgba(233, 193, 118, 0.15);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="material-symbols-outlined" style="color: #e9c176; font-size: 18px;">code</span>
                    <div>
                        <p style="font-weight: 700; color: #e5e2e1; margin: 0; font-size: 0.9rem; font-family: 'Inter', sans-serif;">{target_role}</p>
                        <p style="font-size: 0.75rem; color: #8d928c; margin: 0; font-family: 'Inter', sans-serif;">Active Agent</p>
                    </div>
                </div>
                <span style="font-size: 9px; font-weight: bold; color: #e9c176; background: rgba(27, 48, 34, 0.6); padding: 0.25rem 0.5rem; border-radius: 99px; border: 1px solid rgba(233, 193, 118, 0.25); text-transform: uppercase; font-family: 'Inter', sans-serif;">Optimized</span>
            </div>
            
            <!-- Dormant role -->
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; background: rgba(255,255,255,0.02); border-radius: 16px; border: 1px solid rgba(255,255,255,0.04); opacity: 0.6;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="material-symbols-outlined" style="color: #8d928c; font-size: 18px;">payments</span>
                    <div>
                        <p style="font-weight: 700; color: #e5e2e1; margin: 0; font-size: 0.9rem; font-family: 'Inter', sans-serif;">FinTech Pro</p>
                        <p style="font-size: 0.75rem; color: #8d928c; margin: 0; font-family: 'Inter', sans-serif;">Dormant Agent</p>
                    </div>
                </div>
                <span style="font-size: 9px; font-weight: bold; color: #c3c8c1; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 99px; text-transform: uppercase; font-family: 'Inter', sans-serif;">Draft</span>
            </div>

            <!-- Third role -->
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; background: rgba(27, 48, 34, 0.2); border-radius: 16px; border: 1px solid rgba(233, 193, 118, 0.15);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="material-symbols-outlined" style="color: #e9c176; font-size: 18px;">palette</span>
                    <div>
                        <p style="font-weight: 700; color: #e5e2e1; margin: 0; font-size: 0.9rem; font-family: 'Inter', sans-serif;">Creative UI</p>
                        <p style="font-size: 0.75rem; color: #8d928c; margin: 0; font-family: 'Inter', sans-serif;">Scanning Mode</p>
                    </div>
                </div>
                <span style="font-size: 9px; font-weight: bold; color: #e9c176; background: rgba(27, 48, 34, 0.6); padding: 0.25rem 0.5rem; border-radius: 99px; border: 1px solid rgba(233, 193, 118, 0.25); text-transform: uppercase; font-family: 'Inter', sans-serif;">Processing</span>
            </div>
        </div>
    </div>

    <!-- Mock Interviews Card (col-span-7) -->
    <div class="glass-module rounded-3xl p-8 bento-card animate-delay-4" style="grid-column: span 7; min-height: 320px; border-radius: 24px; padding: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <div>
                <h3 style="font-size: 1.15rem; color: #FAF9F6; margin: 0; font-family: 'Inter', sans-serif; font-weight: 700;">Mock Interviews</h3>
                <p style="color: #8d928c; font-size: 0.8rem; margin: 0.2rem 0 0 0; font-family: 'Inter', sans-serif;">Practice makes permanent.</p>
            </div>
            <a href="/Mock_Interview" target="_self" style="text-decoration: none;">
                <span class="material-symbols-outlined" style="color: #e9c176; font-size: 20px; cursor: pointer; padding: 8px; background: rgba(233, 193, 118, 0.1); border-radius: 12px;">calendar_month</span>
            </a>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <!-- Sim 1 -->
            <div style="display: flex; flex-direction: column; justify-content: space-between; padding: 1.25rem; background: rgba(27, 48, 34, 0.2); border-radius: 20px; border: 1px solid rgba(233, 193, 118, 0.15);">
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span style="font-size: 9px; font-weight: bold; background: rgba(233, 193, 118, 0.2); color: #e9c176; padding: 2px 6px; border-radius: 4px; font-family: 'Inter', sans-serif;">System Design</span>
                        <span style="font-size: 0.7rem; color: #8d928c; font-family: 'Inter', sans-serif;">Today, 2:00 PM</span>
                    </div>
                    <h4 style="font-weight: 700; color: #e5e2e1; margin: 0 0 0.25rem 0; font-size: 0.95rem; font-family: 'Inter', sans-serif;">Google Simulation</h4>
                    <p style="font-size: 0.75rem; color: #8d928c; line-height: 1.4; margin-bottom: 1.5rem; font-family: 'Inter', sans-serif;">L6 Backend infrastructure architecture review.</p>
                </div>
                <a href="/Mock_Interview" target="_self" style="text-decoration: none; width: 100%;">
                    <button class="breathing-button" style="width: 100%; border: none; background: #e9c176; color: #1b3022; font-weight: 700; font-size: 0.8rem; border-radius: 10px; padding: 0.5rem 0; cursor: pointer; font-family: 'Inter', sans-serif;">Join Now</button>
                </a>
            </div>
            
            <!-- Sim 2 -->
            <div style="display: flex; flex-direction: column; justify-content: space-between; padding: 1.25rem; background: rgba(255,255,255,0.02); border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);">
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                        <span style="font-size: 9px; font-weight: bold; background: rgba(255,255,255,0.05); color: #c3c8c1; padding: 2px 6px; border-radius: 4px; font-family: 'Inter', sans-serif;">Behavioral</span>
                        <span style="font-size: 0.7rem; color: #8d928c; font-family: 'Inter', sans-serif;">Tomorrow</span>
                    </div>
                    <h4 style="font-weight: 700; color: #e5e2e1; margin: 0 0 0.25rem 0; font-size: 0.95rem; font-family: 'Inter', sans-serif;">Culture Fit A.I</h4>
                    <p style="font-size: 0.75rem; color: #8d928c; line-height: 1.4; margin-bottom: 1.5rem; font-family: 'Inter', sans-serif;">Situational analysis for fast-paced growth environments.</p>
                </div>
                <a href="/Mock_Interview" target="_self" style="text-decoration: none; width: 100%;">
                    <button style="width: 100%; border: 1px solid rgba(255,255,255,0.1); background: transparent; color: #c3c8c1; font-weight: 700; font-size: 0.8rem; border-radius: 10px; padding: 0.5rem 0; cursor: pointer; font-family: 'Inter', sans-serif;">Prepare</button>
                </a>
            </div>
        </div>
    </div>

    <!-- Resume Optimization Card (col-span-12) -->
    <div class="glass-module rounded-3xl p-8 bento-card animate-delay-5 flex flex-col md:flex-row items-center gap-6" style="grid-column: span 12; border-color: rgba(233, 193, 118, 0.2) !important; border-radius: 24px; padding: 2rem; display: flex; align-items: center;">
        <div style="background: rgba(233, 193, 118, 0.1); padding: 1.25rem; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin-right: 1.5rem;">
            <span class="material-symbols-outlined" style="color: #e9c176; font-size: 36px;">auto_fix_high</span>
        </div>
        <div style="flex: 1;">
            <h3 style="font-size: 1.15rem; color: #FAF9F6; margin: 0 0 0.5rem 0; font-family: 'Inter', sans-serif; font-weight: 700;">Resume Optimization</h3>
            <p style="color: #c3c8c1; font-size: 0.85rem; line-height: 1.5; margin: 0 0 1rem 0; font-family: 'Inter', sans-serif;">
                {"Your resume is parsed. Our AI has detected new ATS keyword shifts in the cloud architecture domain. Let's realign your bullet points." if profile else "No resume uploaded yet. Upload your resume to optimize ATS keyword match rates dynamically."}
            </p>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span style="font-size: 9px; font-weight: bold; color: #e9c176; background: rgba(233, 193, 118, 0.1); padding: 2px 8px; border-radius: 6px; border: 1px solid rgba(233, 193, 118, 0.15); font-family: 'Inter', sans-serif;">#KUBERNETES</span>
                <span style="font-size: 9px; font-weight: bold; color: #e9c176; background: rgba(233, 193, 118, 0.1); padding: 2px 8px; border-radius: 6px; border: 1px solid rgba(233, 193, 118, 0.15); font-family: 'Inter', sans-serif;">#GOLANG</span>
                <span style="font-size: 9px; font-weight: bold; color: #e9c176; background: rgba(233, 193, 118, 0.1); padding: 2px 8px; border-radius: 6px; border: 1px solid rgba(233, 193, 118, 0.15); font-family: 'Inter', sans-serif;">#DISTRIBUTEDSYSTEMS</span>
            </div>
        </div>
        <a href="/Resume_Analysis" target="_self" style="text-decoration: none;">
            <button class="breathing-button" style="background: #e9c176; color: #1b3022; border: none; border-radius: 12px; font-weight: 800; padding: 0.9rem 2rem; cursor: pointer; transition: all 0.3s; white-space: nowrap; font-family: 'Inter', sans-serif;">
                Auto-Optimize
            </button>
        </a>
    </div>
</div>

<div style="margin-top: 3rem; margin-bottom: 1.5rem;">
    <h3 style="font-family: 'Inter', sans-serif; font-size: 1.5rem; font-weight: 700; color: #FAF9F6; margin-bottom: 0.5rem;">Copilot Features</h3>
    <p style="color: #8d928c; font-size: 0.875rem; margin: 0 0 1.5rem 0;">Launch other career readiness engines</p>
</div>
""", unsafe_allow_html=True)

# Feature Sub-Grid
features = [
    ("📄", "Resume Analysis", "ATS scoring, keyword optimization, and improvement tips", "/Resume_Analysis"),
    ("🎯", "Skill Gap Analysis", "Compare your skills against role requirements visually", "/Skill_Gap"),
    ("📊", "Readiness Score", "Composite placement readiness with detailed breakdown", "/Readiness_Score"),
    ("❓", "Interview Questions", "40 AI-generated questions tailored to your profile", "/Interview_Prep"),
    ("🤖", "Mock Interview", "Chat-based AI interview simulator with scoring", "/Mock_Interview"),
    ("🗺️", "Learning Roadmap", "30/60/90 day personalized learning plan", "/Learning_Roadmap"),
    ("📋", "JD Matcher", "Match your resume to any job description", "/JD_Matcher"),
    ("💬", "Career Coach", "AI chatbot with personalized career guidance", "/Career_Coach"),
    ("🚀", "Project Ideas", "Role-specific project recommendations", "/Projects"),
    ("📈", "Analytics", "Full dashboard with interactive charts", "/Analytics"),
    ("🏆", "Candidate Ranker", "Rank multiple resumes against a JD with AI scoring", "/Candidate_Ranker"),
]

cols = st.columns(4)
for i, (icon, title, desc, url) in enumerate(features):
    with cols[i % 4]:
        st.markdown(f"""
        <a href="{url}" target="_self" style="text-decoration:none;">
            <div class="premium-card">
                <div class="premium-card-icon-container">
                    <div class="premium-card-icon-inner">
                        {icon}
                    </div>
                </div>
                <div class="premium-card-title">{title}</div>
                <div class="premium-card-desc">{desc}</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

# Quick Start CTA
if not st.session_state.profile:
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(27, 48, 34, 0.15); border: 1px solid rgba(233, 193, 118, 0.15); border-radius:16px; padding:2rem; text-align:center; margin-top:1rem;">
        <h3 style="color:#e5e2e1; font-family:'Inter', serif; margin:0 0 0.5rem 0; font-weight:700; font-size: 1.4rem;">🚀 Get Started in 30 Seconds</h3>
        <p style="color:#c3c8c1; font-family:'Inter', serif; margin:0 0 1.5rem 0; font-style:italic;">
            Navigate to <strong style="color:#e9c176; font-weight:500;">Resume Analysis</strong> in the sidebar to upload your resume.
        </p>
        <p style="color:#8d928c; font-family:'Inter', serif; font-size:0.8rem; margin:0;">
            Supports PDF and DOCX • Secure • AI-Powered • Free to use
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(f"✅ Resume loaded for **{st.session_state.profile.get('name', 'you')}**. Navigate to any feature using the bento modules or the sidebar!")

