"""Page 10: Analytics Dashboard"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import (
    ats_gauge, readiness_gauge, skill_radar,
    ats_breakdown_bar, readiness_components_bar, skill_coverage_bar
)
from backend.services.skill_analyzer import get_role_info

st.set_page_config(page_title="Analytics | Placement Copilot", page_icon="📈", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">📈 Analytics Dashboard</div>
    <p class="hero-subtitle">Complete overview of your placement readiness with interactive charts</p>
</div>
""", unsafe_allow_html=True)

profile = st.session_state.get("profile")
ats = st.session_state.get("ats_score")
gap = st.session_state.get("skill_gap")
readiness = st.session_state.get("readiness_score")
target_role = st.session_state.get("target_role", "Software Engineer")

if not profile:
    st.markdown("""
    <div style="text-align:center;padding:4rem;">
        <div style="font-size:4rem;margin-bottom:1rem;">📈</div>
        <h3 style="color:#f0f0f5;">No data yet</h3>
        <p style="color:#9898b0;">Upload your resume and complete the analysis to see your full dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Header Stats ────────────────────────────────────────────────────────────────
name = profile.get("name", "Candidate")
st.markdown(f"""
<div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
     border-radius:16px;padding:1.5rem;margin-bottom:2rem;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div style="font-size:1.4rem;font-weight:800;color:#f0f0f5;">{name}</div>
            <div style="color:#9898b0;font-size:0.875rem;">Target: <strong style="color:#a78bfa;">{target_role}</strong></div>
        </div>
        <div style="display:flex;gap:2rem;text-align:center;">
            <div>
                <div style="font-size:1.8rem;font-weight:800;color:#8b5cf6;">{len(profile.get('skills',[]))}</div>
                <div style="color:#5a5a72;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;">Skills</div>
            </div>
            <div>
                <div style="font-size:1.8rem;font-weight:800;color:#3b82f6;">{len(profile.get('projects',[]))}</div>
                <div style="color:#5a5a72;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;">Projects</div>
            </div>
            <div>
                <div style="font-size:1.8rem;font-weight:800;color:#06b6d4;">{len(profile.get('experience',[]))}</div>
                <div style="color:#5a5a72;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;">Experience</div>
            </div>
            <div>
                <div style="font-size:1.8rem;font-weight:800;color:#22c55e;">{len(profile.get('certifications',[]))}</div>
                <div style="color:#5a5a72;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;">Certs</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Row 1: Main Gauges ──────────────────────────────────────────────────────────
st.markdown("### 🎯 Core Scores")
col1, col2, col3 = st.columns(3)

with col1:
    if ats:
        st.plotly_chart(ats_gauge(ats["overall_score"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"<div style='text-align:center;color:#9898b0;font-size:0.8rem;'>Rating: <strong style='color:#f0f0f5;'>{ats.get('rating','—')}</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem;">
            <div style="color:#5a5a72;font-size:0.875rem;">ATS score not calculated yet<br>
            Go to Resume Analysis</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if readiness:
        st.plotly_chart(
            readiness_gauge(readiness["overall_score"], readiness["level"]),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown(f"<div style='text-align:center;color:#9898b0;font-size:0.8rem;'>Level: <strong style='color:{readiness.get('level_color','#8b5cf6')};'>{readiness['level']}</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem;">
            <div style="color:#5a5a72;font-size:0.875rem;">Readiness score not calculated yet<br>
            Go to Readiness Score</div>
        </div>
        """, unsafe_allow_html=True)

with col3:
    if gap:
        coverage = gap.get("coverage", {}).get("overall", 0)
        fig_cov = ats_gauge(coverage, "Skill Coverage")
        st.plotly_chart(fig_cov, use_container_width=True, config={"displayModeBar": False})
        strength = gap.get("skill_strength", {})
        color = {"Strong": "#22c55e", "Good": "#3b82f6", "Developing": "#f97316", "Beginner": "#ef4444"}.get(strength.get("level",""), "#8b5cf6")
        st.markdown(f"<div style='text-align:center;color:#9898b0;font-size:0.8rem;'>Skill Level: <strong style='color:{color};'>{strength.get('level','—')}</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem;">
            <div style="color:#5a5a72;font-size:0.875rem;">Skill gap not analyzed yet<br>
            Go to Skill Gap</div>
        </div>
        """, unsafe_allow_html=True)

# ── Row 2: Breakdown Charts ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Detailed Breakdowns")
col_left, col_right = st.columns(2)

with col_left:
    if ats:
        st.markdown("#### ATS Score Breakdown")
        st.plotly_chart(
            ats_breakdown_bar(ats["weighted_scores"], ats["weights"]),
            use_container_width=True, config={"displayModeBar": False}
        )

with col_right:
    if readiness:
        st.markdown("#### Readiness Components")
        st.plotly_chart(
            readiness_components_bar(readiness["components"]),
            use_container_width=True, config={"displayModeBar": False}
        )

# ── Row 3: Radar Chart ──────────────────────────────────────────────────────────
if gap:
    st.markdown("---")
    st.markdown("### 🕸️ Skills Radar")
    role_data = get_role_info(target_role) or {}
    required = role_data.get("required_skills", [])[:8]
    st.plotly_chart(
        skill_radar(profile.get("skills", []), required, target_role),
        use_container_width=True, config={"displayModeBar": False}
    )

# ── Skill Coverage ──────────────────────────────────────────────────────────────
if gap:
    st.markdown("---")
    col_coverage, col_action = st.columns([1, 2])
    with col_coverage:
        st.markdown("### Skills Coverage")
        st.plotly_chart(
            skill_coverage_bar(gap.get("matched_skills", []), gap.get("missing_skills", [])),
            use_container_width=True, config={"displayModeBar": False}
        )
    with col_action:
        st.markdown("### 🎯 Recommended Actions")
        all_recs = []
        if readiness: all_recs.extend(readiness.get("recommendations", []))
        if ats: all_recs.extend(ats.get("suggestions", [])[:3])

        for rec in all_recs[:6]:
            st.markdown(f"""
            <div class="question-card" style="margin-bottom:0.5rem;">
                <div style="color:#f0f0f5;font-size:0.85rem;">{rec}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Missing Data Prompts ──────────────────────────────────────────────────────────
missing_sections = []
if not ats: missing_sections.append("ATS Score — go to Resume Analysis")
if not gap: missing_sections.append("Skill Gap — go to Skill Gap Analysis")
if not readiness: missing_sections.append("Readiness Score — go to Readiness Score")

if missing_sections:
    st.markdown("---")
    st.markdown("""
    <div class="alert-warning">
        ⚠️ <strong>Complete your dashboard:</strong><br>
    """ + "<br>".join(f"• {s}" for s in missing_sections) + "</div>", unsafe_allow_html=True)
