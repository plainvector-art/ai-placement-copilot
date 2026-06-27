"""Page 9: Project Recommendations"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from backend.services.project_recommender import recommend_projects

st.set_page_config(page_title="Projects | Placement Copilot", page_icon="🚀", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🚀 Project Recommendations</div>
    <p class="hero-subtitle">AI-curated project ideas that will impress recruiters in your target role</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("profile"):
    st.warning("⚠️ Please upload your resume first.")
    st.stop()

profile = st.session_state.profile
target_role = st.session_state.get("target_role", "Software Engineer")

if st.button("🤖 Get Project Recommendations", use_container_width=False):
    with st.spinner(f"Finding the best projects for {target_role}..."):
        result = recommend_projects(profile, target_role)
        st.session_state["project_recs"] = result
        st.rerun()

recs = st.session_state.get("project_recs")

if recs:
    level = recs.get("experience_level", "beginner").title()
    strategy = recs.get("portfolio_strategy", "")

    col_info, col_tips = st.columns([2, 1])
    with col_info:
        st.metric("Experience Level", level)
        if strategy:
            st.markdown(f'<div class="alert-info">💡 <strong>Portfolio Strategy:</strong> {strategy}</div>', unsafe_allow_html=True)

    # Build order
    build_order = recs.get("build_order", [])
    if build_order:
        st.markdown("**📋 Recommended Build Order:**")
        order_html = " → ".join([f'<span style="color:#a78bfa;font-weight:600;">{p}</span>' for p in build_order[:4]])
        st.markdown(f'<div style="color:#9898b0;font-size:0.9rem;margin:0.5rem 0 1.5rem 0;">{order_html}</div>', unsafe_allow_html=True)

    # AI Recommendations
    ai_projects = recs.get("ai_recommendations", [])
    curated = recs.get("curated_recommendations", [])

    all_projects = ai_projects or curated

    if all_projects:
        st.markdown("---")
        st.markdown("#### 🎯 Recommended Projects")

        for proj in all_projects:
            impact = proj.get("impact_score", 7)
            difficulty = proj.get("difficulty", "Intermediate")
            diff_colors = {"Beginner": "#22c55e", "Intermediate": "#f97316", "Advanced": "#ef4444"}
            dc = diff_colors.get(difficulty, "#8b5cf6")

            tech_tags = "".join([
                f'<span class="skill-tag skill-tag-neutral">{t}</span>'
                for t in proj.get("technologies", [])[:5]
            ])

            with st.expander(f"{'⭐' * min(int(impact/2),5) if impact else '🚀'} {proj.get('title','Project')}", expanded=False):
                col_desc, col_meta = st.columns([3, 1])

                with col_desc:
                    st.markdown(f"**{proj.get('description','')}**")

                    if proj.get("why_build"):
                        st.markdown(f"""
                        <div class="alert-info">
                            🎯 <strong>Why build this:</strong> {proj['why_build']}
                        </div>
                        """, unsafe_allow_html=True)

                    if proj.get("recruiters_love"):
                        st.markdown(f"""
                        <div class="alert-success">
                            ❤️ <strong>Recruiters love it:</strong> {proj['recruiters_love']}
                        </div>
                        """, unsafe_allow_html=True)

                    if proj.get("what_to_add"):
                        st.markdown(f"**✨ Unique Feature Idea:** {proj['what_to_add']}")

                    if proj.get("deployment"):
                        st.markdown(f"**🚀 Deploy on:** {proj['deployment']}")

                with col_meta:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;">
                        <div style="color:{dc};font-weight:700;font-size:0.875rem;">{difficulty}</div>
                        <div style="color:#5a5a72;font-size:0.75rem;margin:0.25rem 0;">Difficulty</div>
                        <hr style="border-color:rgba(255,255,255,0.06);margin:0.5rem 0;">
                        <div style="color:#f0f0f5;font-weight:700;">{proj.get('estimated_time','2-4 weeks')}</div>
                        <div style="color:#5a5a72;font-size:0.75rem;">Duration</div>
                        <hr style="border-color:rgba(255,255,255,0.06);margin:0.5rem 0;">
                        <div style="color:#f0f0f5;font-weight:700;">{impact}/10</div>
                        <div style="color:#5a5a72;font-size:0.75rem;">Impact Score</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("**Technologies:**")
                st.markdown(f'<div style="line-height:2.5;">{tech_tags}</div>', unsafe_allow_html=True)

                if proj.get("github_topics"):
                    topics = " ".join([f"#{t}" for t in proj["github_topics"][:4]])
                    st.markdown(f'<div style="color:#5a5a72;font-size:0.8rem;margin-top:0.5rem;">GitHub tags: {topics}</div>', unsafe_allow_html=True)

    # GitHub Tips
    github_tips = recs.get("github_tips", [])
    if github_tips:
        st.markdown("---")
        st.markdown("#### 💡 GitHub Portfolio Tips")
        for tip in github_tips:
            st.markdown(f"""
            <div class="question-card" style="margin-bottom:0.5rem;">
                <div style="color:#f0f0f5;font-size:0.875rem;">💡 {tip}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    # Pre-generate state
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🚀</div>
        <p style="color:#9898b0;">Click the button above to get AI-curated project recommendations</p>
    </div>
    """, unsafe_allow_html=True)
