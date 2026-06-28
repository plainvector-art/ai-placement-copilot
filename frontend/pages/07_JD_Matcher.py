"""Page 7: Resume vs JD Matcher"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import jd_match_gauge
from backend.services.jd_matcher import calculate_jd_match
from backend.services.ai_client import has_api_key

st.set_page_config(page_title="JD Matcher | Placement Copilot", page_icon="📋", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">📋 Job Description Matcher</div>
    <p class="hero-subtitle">Paste any job description to see how well your resume matches — beat the ATS</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("profile"):
    st.warning("⚠️ Please upload your resume first.")
    st.stop()

if not has_api_key():
    st.info("💡 **This feature requires an active AI API key.**")
    if st.button("🔑 Open AI Settings", use_container_width=True):
        st.switch_page("pages/12_AI_Settings.py")
    st.stop()

profile = st.session_state.profile

col_jd, col_btns = st.columns([4, 1])
with col_jd:
    jd_text = st.text_area(
        "Paste Job Description",
        placeholder="Paste the full job description here...\n\nExample:\nWe are looking for a Data Scientist with 2+ years of experience...\n\nRequirements:\n• Proficiency in Python and SQL\n• Experience with Machine Learning\n• Knowledge of TensorFlow or PyTorch...",
        height=300,
        label_visibility="collapsed",
    )
with col_btns:
    st.markdown("<br>", unsafe_allow_html=True)
    match_btn = st.button("🔍 Analyze Match", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
         border-radius:10px;padding:1rem;font-size:0.8rem;color:#9898b0;">
        <strong style="color:#f0f0f5;">Your Resume</strong><br>
        {profile.get('name','Candidate')}<br>
        {len(profile.get('skills',[]))} skills detected
    </div>
    """, unsafe_allow_html=True)

if match_btn and jd_text.strip():
    with st.spinner("Analyzing job description match..."):
        result = calculate_jd_match(profile, jd_text)
        st.session_state["jd_result"] = result
        st.rerun()
elif match_btn:
    st.warning("Please paste a job description first.")

result = st.session_state.get("jd_result")

if result:
    rating = result.get("match_rating", {})
    overall = result.get("overall_match_score", 0)

    # ── Score Display ───────────────────────────────────────────────────────────
    st.markdown("---")
    col_gauge, col_scores = st.columns([2, 3])

    with col_gauge:
        st.plotly_chart(
            jd_match_gauge(overall),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        emoji = rating.get("emoji", "🟡")
        label = rating.get("label", "")
        color = {"green": "#22c55e", "blue": "#3b82f6", "orange": "#f97316", "red": "#ef4444"}.get(
            rating.get("color", "orange"), "#8b5cf6"
        )
        st.markdown(f"""
        <div style="text-align:center;">
            <span style="font-size:2rem;">{emoji}</span>
            <div style="color:{color};font-weight:700;font-size:1.1rem;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_scores:
        st.markdown("#### Score Breakdown")
        metrics = [
            ("📝 Keyword Match", result.get("keyword_match_score", 0), "of JD keywords found in resume"),
            ("🛠️ Skill Match", result.get("skill_match_score", 0), "of required skills matched"),
            ("🤖 ATS Optimization", result.get("ats_optimization_score", 0), "ATS pass-through score"),
        ]

        for label, score, desc in metrics:
            bar_color = "#22c55e" if score >= 70 else ("#3b82f6" if score >= 50 else "#ef4444")
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span style="color:#f0f0f5;font-weight:600;font-size:0.875rem;">{label}</span>
                    <span style="color:{bar_color};font-weight:700;">{score:.0f}%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width:{score}%;background:{bar_color};"></div>
                </div>
                <div style="color:#5a5a72;font-size:0.75rem;margin-top:0.2rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Keyword Analysis ─────────────────────────────────────────────────────────
    st.markdown("---")
    tab_match, tab_miss, tab_recs, tab_ai = st.tabs([
        "✅ Matched Keywords", "❌ Missing Keywords", "💡 Recommendations",
        "🤖 AI Insights" if result.get("ai_insights") else "📊 Stats"
    ])

    with tab_match:
        matched = result.get("matched_keywords", [])
        matched_skills = result.get("matched_skills", [])
        if matched:
            st.markdown("**Keywords from JD found in your resume:**")
            tags = "".join([f'<span class="skill-tag skill-tag-have">✓ {kw}</span>' for kw in matched])
            st.markdown(f'<div style="line-height:2.5;">{tags}</div>', unsafe_allow_html=True)
        if matched_skills:
            st.markdown("**Matching Skills:**")
            tags2 = "".join([f'<span class="skill-tag skill-tag-neutral">⭐ {s}</span>' for s in matched_skills])
            st.markdown(f'<div style="line-height:2.5;">{tags2}</div>', unsafe_allow_html=True)

    with tab_miss:
        missing = result.get("missing_keywords", [])
        missing_skills = result.get("missing_skills", [])
        if missing:
            st.markdown("**Keywords in JD not found in your resume:**")
            st.markdown('<div class="alert-warning">Add these keywords naturally to your resume to improve ATS ranking.</div>', unsafe_allow_html=True)
            tags = "".join([f'<span class="skill-tag skill-tag-missing">✗ {kw}</span>' for kw in missing])
            st.markdown(f'<div style="line-height:2.5;">{tags}</div>', unsafe_allow_html=True)
        if missing_skills:
            st.markdown("**Missing Required Skills:**")
            tags2 = "".join([f'<span class="skill-tag skill-tag-missing">✗ {s}</span>' for s in missing_skills])
            st.markdown(f'<div style="line-height:2.5;">{tags2}</div>', unsafe_allow_html=True)

    with tab_recs:
        for rec in result.get("recommendations", []):
            st.markdown(f"""
            <div class="question-card" style="margin-bottom:0.5rem;">
                <div style="color:#f0f0f5;font-size:0.875rem;">{rec}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_ai:
        ai = result.get("ai_insights")
        if ai:
            if ai.get("fit_assessment"):
                st.markdown(f'<div class="alert-info">🤖 {ai["fit_assessment"]}</div>', unsafe_allow_html=True)

            col_strong, col_concern = st.columns(2)
            with col_strong:
                st.markdown("**Why you're a good fit:**")
                for r in ai.get("strong_fit_reasons", []):
                    st.markdown(f"✅ {r}")
            with col_concern:
                st.markdown("**Areas of concern:**")
                for c in ai.get("concern_areas", []):
                    st.markdown(f"⚠️ {c}")

            st.markdown("**Interview talking points:**")
            for tp in ai.get("interview_talking_points", []):
                st.markdown(f"💬 {tp}")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("JD Keywords", result.get("jd_keyword_count", 0))
            with c2: st.metric("Matched", len(result.get("matched_keywords", [])))
            with c3: st.metric("Missing", len(result.get("missing_keywords", [])))

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">📋</div>
        <p style="color:#9898b0;">Paste a job description above and click Analyze Match</p>
    </div>
    """, unsafe_allow_html=True)
