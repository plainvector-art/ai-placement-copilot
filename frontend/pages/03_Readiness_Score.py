"""Page 3: Placement Readiness Score"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import readiness_gauge, readiness_components_bar
from backend.services.readiness_scorer import calculate_readiness_score
from backend.services.ats_scorer import calculate_ats_score
from backend.services.skill_analyzer import analyze_skill_gap

st.set_page_config(page_title="Readiness Score | Placement Copilot", page_icon="📊", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">📊 Placement Readiness Score</div>
    <p class="hero-subtitle">Your composite placement readiness score across 4 key dimensions</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("profile"):
    st.warning("⚠️ Please upload your resume first.")
    st.stop()

profile = st.session_state.profile
target_role = st.session_state.get("target_role", "Software Engineer")

if st.button("🔄 Calculate Readiness Score", use_container_width=False):
    with st.spinner("Calculating your placement readiness..."):
        ats = st.session_state.get("ats_score") or calculate_ats_score(profile)
        st.session_state.ats_score = ats

        gap = st.session_state.get("skill_gap") or analyze_skill_gap(profile.get("skills", []), target_role)
        st.session_state.skill_gap = gap

        readiness = calculate_readiness_score(
            ats.get("overall_score", 50),
            gap,
            profile,
        )
        st.session_state.readiness_score = readiness
        st.rerun()

readiness = st.session_state.get("readiness_score")

if readiness:
    score = readiness["overall_score"]
    level = readiness["level"]
    color = readiness["level_color"]
    emoji = readiness["level_emoji"]
    message = readiness["level_message"]

    # ── Hero Score Display ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(22,22,31,0.9),rgba(26,16,40,0.9));
         border:1px solid rgba(139,92,246,0.2);border-radius:20px;
         padding:2.5rem;text-align:center;margin-bottom:2rem;">
        <div style="font-size:4rem;margin-bottom:0.5rem;">{emoji}</div>
        <div style="font-size:4.5rem;font-weight:900;color:{color};letter-spacing:-0.03em;
             text-shadow:0 0 40px {color}44;">{score:.0f}<span style="font-size:2rem;">%</span></div>
        <div style="font-size:1.3rem;font-weight:700;color:#f0f0f5;margin-top:0.25rem;">{level}</div>
        <div style="color:#9898b0;font-size:0.95rem;margin-top:0.75rem;max-width:500px;margin-left:auto;margin-right:auto;">
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_gauge, col_chart = st.columns([1, 2])

    with col_gauge:
        st.plotly_chart(
            readiness_gauge(score, level),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        # Next milestone
        milestone = readiness.get("next_milestone", {})
        if milestone:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="color:#5a5a72;font-size:0.75rem;text-transform:uppercase;
                     letter-spacing:0.08em;margin-bottom:0.25rem;">Next Milestone</div>
                <div style="color:{milestone.get('color','#8b5cf6')};font-weight:700;font-size:1rem;">
                    {milestone.get('level','')}
                </div>
                <div style="color:#9898b0;font-size:0.85rem;margin-top:0.25rem;">
                    +{milestone.get('gap',0):.0f} points needed
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_chart:
        st.markdown("#### Component Breakdown")
        st.plotly_chart(
            readiness_components_bar(readiness["components"]),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Component Details ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔍 Detailed Component Analysis")

    comp_cols = st.columns(4)
    for i, (name, data) in enumerate(readiness["components"].items()):
        with comp_cols[i]:
            s = data["score"]
            status = data["status"]
            status_colors = {"Strong": "#22c55e", "Good": "#3b82f6", "Needs Work": "#f97316", "Critical": "#ef4444"}
            sc = status_colors.get(status, "#8b5cf6")
            st.markdown(f"""
            <div class="card" style="text-align:center;border-top:2px solid {sc};">
                <div style="font-size:2rem;font-weight:800;color:{sc};">{s:.0f}</div>
                <div style="font-size:0.8rem;font-weight:700;color:#f0f0f5;margin-top:0.25rem;">{name}</div>
                <div style="font-size:0.72rem;color:#5a5a72;margin-top:0.15rem;">Weight: {data['weight']}</div>
                <div style="margin-top:0.75rem;">
                    <span style="background:{sc}22;color:{sc};border:1px solid {sc}33;
                         padding:0.2rem 0.5rem;border-radius:999px;font-size:0.72rem;font-weight:700;">
                        {status}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Recommendations ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🚀 Action Plan")
    for rec in readiness.get("recommendations", []):
        st.markdown(f"""
        <div class="question-card" style="margin-bottom:0.5rem;">
            <div style="color:#f0f0f5;font-size:0.875rem;">{rec}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Level Guide ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📏 Score Scale Reference")
    levels = [
        (0, 40, "🌱 Beginner", "#ef4444", "Focus on building core skills and 2-3 portfolio projects"),
        (40, 60, "📈 Developing", "#f97316", "Fill skill gaps and strengthen your project portfolio"),
        (60, 80, "🎯 Placement Ready", "#22c55e", "Polish resume and practice interviews actively"),
        (80, 100, "🚀 Highly Competitive", "#8b5cf6", "Target top-tier companies and negotiate confidently"),
    ]
    scale_cols = st.columns(4)
    for i, (min_s, max_s, lname, lcolor, ldesc) in enumerate(levels):
        is_current = min_s <= score < max_s
        with scale_cols[i]:
            st.markdown(f"""
            <div class="card" style="border:{'2px solid ' + lcolor if is_current else '1px solid rgba(255,255,255,0.06)'};
                 opacity:{'1' if is_current else '0.7'};">
                <div style="color:{lcolor};font-weight:700;font-size:0.875rem;">{lname}</div>
                <div style="color:#5a5a72;font-size:0.75rem;margin-top:0.15rem;">{min_s}–{max_s} points</div>
                <div style="color:#9898b0;font-size:0.78rem;margin-top:0.5rem;line-height:1.5;">{ldesc}</div>
                {'<div style="color:' + lcolor + ';font-size:0.75rem;margin-top:0.5rem;font-weight:700;">← YOU ARE HERE</div>' if is_current else ''}
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
        <p style="color:#9898b0;">Click the button above to calculate your placement readiness score</p>
    </div>
    """, unsafe_allow_html=True)
