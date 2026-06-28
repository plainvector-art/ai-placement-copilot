"""Page 6: Learning Roadmap Generator"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import roadmap_timeline
from backend.services.roadmap_gen import generate_roadmap
from backend.services.skill_analyzer import analyze_skill_gap
from backend.services.ai_client import has_api_key

st.set_page_config(page_title="Learning Roadmap | Placement Copilot", page_icon="🗺️", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🗺️ Personalized Learning Roadmap</div>
    <p class="hero-subtitle">Your 6-month plan to go from where you are to where you want to be</p>
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
target_role = st.session_state.get("target_role", "Software Engineer")

col_hours, col_btn = st.columns([3, 1])
with col_hours:
    hours = st.slider("Available study hours per week", 5, 40, 10, step=5)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    gen_btn = st.button("🤖 Generate Roadmap", use_container_width=True)

if gen_btn:
    with st.spinner("🤖 Building your personalized 6-month roadmap..."):
        gap = st.session_state.get("skill_gap") or analyze_skill_gap(
            profile.get("skills", []), target_role
        )
        st.session_state.skill_gap = gap
        roadmap = generate_roadmap(profile, target_role, gap, hours)
        st.session_state.roadmap = roadmap
        st.rerun()

roadmap = st.session_state.get("roadmap")

if roadmap:
    summary = roadmap.get("summary", {})
    meta = roadmap.get("metadata", {})

    # Summary cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Duration", summary.get("total_duration", "6 months"))
    with c2: st.metric("Total Hours", summary.get("total_hours", hours * 24))
    with c3: st.metric("Hours/Week", hours)
    with c4: st.metric("Missing Skills", meta.get("missing_skills_count", 0))

    # Expected outcome
    if summary.get("expected_outcome"):
        st.markdown(f"""
        <div class="alert-success">
            🎯 <strong>Expected Outcome:</strong> {summary['expected_outcome']}
        </div>
        """, unsafe_allow_html=True)

    # Timeline chart
    st.markdown("---")
    phases = roadmap.get("phases", {})
    if phases:
        st.markdown("#### 📅 Timeline Overview")
        st.plotly_chart(roadmap_timeline(phases), use_container_width=True, config={"displayModeBar": False})

    # Phase Tabs
    st.markdown("#### 🗂️ Phase Breakdown")
    phase_tabs = st.tabs(["🔵 Month 1", "🟣 Month 2-3", "🟡 Month 3-6", "🟢 Job Search"])
    phase_keys = ["phase_1", "phase_2", "phase_3", "phase_4"]
    phase_icons = ["🔵", "🟣", "🟡", "🟢"]

    for tab, phase_key, icon in zip(phase_tabs, phase_keys, phase_icons):
        with tab:
            phase = phases.get(phase_key, {})
            if not phase:
                st.info("Roadmap data for this phase is being generated...")
                continue

            st.markdown(f"""
            <div class="card" style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <h4 style="color:#e5e2e1;margin:0 0 0.25rem 0;">
                            {icon} {phase.get('name',phase_key.title())}
                        </h4>
                        <p style="color:#c3c8c1;margin:0;font-size:0.875rem;">{phase.get('goal','')}</p>
                    </div>
                    <div style="text-align:right;flex-shrink:0;">
                        <span style="background:rgba(233,193,118,0.15);color:#e9c176;
                             border:1px solid rgba(233,193,118,0.25);
                             padding:0.2rem 0.8rem;border-radius:999px;font-size:0.8rem;font-weight:600;">
                            {phase.get('duration','')}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Skills to gain
            skills_gained = phase.get("skills_gained", [])
            if skills_gained:
                tags = "".join([f'<span class="skill-tag skill-tag-neutral">{s}</span>' for s in skills_gained])
                st.markdown(f"**Skills You'll Gain:** {tags}", unsafe_allow_html=True)

            # Week-by-week breakdown
            weeks = phase.get("weeks_breakdown", [])
            if weeks:
                st.markdown("**Week-by-Week Plan:**")
                for week in weeks:
                    with st.expander(f"Week {week.get('week','')}: {week.get('focus','')}"):
                        col_topics, col_resources = st.columns(2)
                        with col_topics:
                            topics = week.get("topics", [])
                            if topics:
                                st.markdown("📚 **Topics to cover:**")
                                for t in topics:
                                    st.markdown(f"- {t}")
                            if week.get("project"):
                                st.markdown(f"🛠️ **Mini Project:** {week['project']}")
                            if week.get("milestone"):
                                st.markdown(f"""
                                <div class="alert-success">🏆 Milestone: {week['milestone']}</div>
                                """, unsafe_allow_html=True)

                        with col_resources:
                            resources = week.get("resources", [])
                            if resources:
                                st.markdown("🔗 **Resources:**")
                                for r in resources:
                                    free_badge = "🆓" if r.get("free") else "💰"
                                    url = r.get("url", "#")
                                    if url and url != "#":
                                        st.markdown(f"{free_badge} [{r['title']}]({url}) — *{r.get('type','')}*")
                                    else:
                                        st.markdown(f"{free_badge} {r.get('title','')} — *{r.get('type','')}*")

            # Milestone
            if phase.get("milestone"):
                st.markdown(f"""
                <div style="background:rgba(27,48,34,0.3);
                     border:1px solid rgba(233,193,118,0.2);border-radius:10px;
                     padding:0.875rem 1rem;margin-top:1rem;">
                    🎯 <strong style="color:#e5e2e1;">Phase Milestone:</strong>
                    <span style="color:#c3c8c1;"> {phase['milestone']}</span>
                </div>
                """, unsafe_allow_html=True)

    # Key Milestones Timeline
    milestones = roadmap.get("key_milestones", [])
    if milestones:
        st.markdown("---")
        st.markdown("#### 🏆 Key Milestones")
        for m in milestones:
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot">M{m.get('month','?')}</div>
                <div class="timeline-content">
                    <div style="color:#f0f0f5;font-weight:600;font-size:0.9rem;">{m.get('milestone','')}</div>
                    <div style="color:#9898b0;font-size:0.8rem;margin-top:0.2rem;">
                        Proof: {m.get('proof','')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Top Resources
    resources = roadmap.get("top_resources", [])
    if resources:
        st.markdown("---")
        st.markdown("#### 🔗 Essential Resources")
        res_cols = st.columns(min(len(resources), 4))
        for i, r in enumerate(resources[:4]):
            with res_cols[i]:
                free_badge = "🆓 Free" if r.get("free") else "💰 Paid"
                url = r.get("url", "#")
                st.markdown(f"""
                <div class="rec-card" style="text-align:center;height:160px;display:flex;
                     flex-direction:column;justify-content:center;gap:0.4rem;">
                    <div style="font-size:0.875rem;font-weight:700;color:#f0f0f5;">{r.get('title','')}</div>
                    <div style="font-size:0.75rem;color:#9898b0;">{r.get('type','')}</div>
                    <div style="font-size:0.75rem;color:#22c55e if r.get('free') else #f97316;">{free_badge}</div>
                    <div style="font-size:0.78rem;color:#5a5a72;">{r.get('why','')[:60]}</div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🗺️</div>
        <p style="color:#9898b0;">Click "Generate Roadmap" to create your personalized learning plan</p>
    </div>
    """, unsafe_allow_html=True)
