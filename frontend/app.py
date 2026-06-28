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

# Override styling to match the premium dark gold/beige design from the screenshot
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,0..700&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* ── Typography ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
}
p, li, label, .stMarkdown, .premium-card-title, .premium-card-desc, .sidebar-logo, .sidebar-section-label {
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

/* ── Cards ───────────────────────────────────────────────────────────────────── */
.premium-card {
    background: rgba(18, 20, 16, 0.65) !important;
    border: 1px solid rgba(212, 175, 55, 0.12) !important;
    border-radius: 12px !important;
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
    box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
}
.premium-card:hover {
    border-color: rgba(212, 175, 55, 0.45) !important;
    transform: translateY(-4px) !important;
    background: rgba(24, 26, 20, 0.8) !important;
    box-shadow: 0 8px 24px rgba(212, 175, 55, 0.12), 0 0 15px rgba(212, 175, 55, 0.04) !important;
}
.premium-card-icon-container {
    width: 54px;
    height: 54px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(212,175,55,0.08) 0%, rgba(212,175,55,0) 70%);
    border: 1px solid rgba(212,175,55,0.22);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.25rem;
}
.premium-card-icon-inner {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 1px solid rgba(212,175,55,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
}
.premium-card-title {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #e6dfd3 !important;
    letter-spacing: 0.01em !important;
}
.premium-card-desc {
    font-size: 0.72rem !important;
    color: #8c8577 !important;
    line-height: 1.45 !important;
    font-style: italic !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State Initialization ──────────────────────────────────────────────
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


# Logo circular containers, main title, ornament and description
st.markdown("""
<div style="display:flex; justify-content:center; margin-top:2rem; margin-bottom:1.25rem;">
    <div style="width: 86px; height: 86px; border-radius: 50%; 
                background: radial-gradient(circle, rgba(212,175,55,0.15) 0%, rgba(212,175,55,0) 70%);
                border: 1px solid rgba(212,175,55,0.35);
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 0 30px rgba(212,175,55,0.08);">
        <div style="width: 70px; height: 70px; border-radius: 50%;
                    border: 1px solid rgba(212,175,55,0.18);
                    display: flex; align-items: center; justify-content: center;
                    font-size: 2.3rem; color: #d4af37;">
            🎯
        </div>
    </div>
</div>
<h1 style="font-family:'Playfair Display', serif !important; font-size:3.1rem; font-weight:400; text-align:center; margin-bottom:0.75rem; letter-spacing:0.02em; line-height:1.2;">
    <span style="color:#e6dfd3;">AI Interview &</span> 
    <span style="color:#d4af37; font-weight:500;">Placement Copilot</span>
</h1>
<div style="display:flex; align-items:center; justify-content:center; margin: 1.25rem auto; max-width: 400px; gap: 15px;">
    <div style="flex:1; height:1px; background:linear-gradient(90deg, transparent, rgba(212,175,55,0.25));"></div>
    <div style="color:rgba(212,175,55,0.5); font-size:0.7rem; letter-spacing:0.1em;">❖</div>
    <div style="flex:1; height:1px; background:linear-gradient(270deg, transparent, rgba(212,175,55,0.25));"></div>
</div>
<p style="font-family:'Lora', serif; font-size:1.02rem; color:#a29c90; text-align:center; max-width:700px; margin: 0 auto 3rem auto; line-height:1.75; font-style:italic;">
    Your AI-powered career coach. Upload your resume and get personalized insights, 
    skill gap analysis, mock interviews, and learning roadmaps.
</p>
""", unsafe_allow_html=True)

# Feature Grid
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

cols = st.columns(5)
for i, (icon, title, desc, url) in enumerate(features):
    with cols[i % 5]:
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
    <div style="background: linear-gradient(135deg, rgba(212,175,55,0.04), rgba(212,175,55,0.01));
         border: 1px solid rgba(212,175,55,0.15); border-radius:16px; padding:2rem; text-align:center; margin-top:1rem;">
        <h3 style="color:#e6dfd3; font-family:'Playfair Display', serif; margin:0 0 0.5rem 0; font-weight:400; font-size: 1.4rem;">🚀 Get Started in 30 Seconds</h3>
        <p style="color:#8c8577; font-family:'Lora', serif; margin:0 0 1.5rem 0; font-style:italic;">
            Navigate to <strong style="color:#d4af37; font-weight:500;">Resume Analysis</strong> in the sidebar to upload your resume.
        </p>
        <p style="color:#5c564c; font-family:'Lora', serif; font-size:0.8rem; margin:0;">
            Supports PDF and DOCX • Secure • AI-Powered • Free to use
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(f"✅ Resume loaded for **{st.session_state.profile.get('name', 'you')}**. Navigate to any feature using the sidebar!")

