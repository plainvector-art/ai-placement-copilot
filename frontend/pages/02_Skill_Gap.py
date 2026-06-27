"""Page 2: Skill Gap Analysis"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import skill_radar, skill_coverage_bar
from backend.services.skill_analyzer import analyze_skill_gap, get_available_roles

st.set_page_config(page_title="Skill Gap | Placement Copilot", page_icon="🎯", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎯 Skill Gap Analysis</div>
    <p class="hero-subtitle">See exactly which skills you have and what you need to land your target role</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("profile"):
    st.warning("⚠️ Please upload your resume first (Resume Analysis page)")
    st.stop()

profile = st.session_state.profile

# Role Selector
col_role, col_btn = st.columns([3, 1])
with col_role:
    roles = get_available_roles()
    target_role = st.selectbox(
        "Target Role",
        roles,
        index=roles.index(st.session_state.target_role) if st.session_state.target_role in roles else 0,
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🔍 Analyze Gap", use_container_width=True)

if analyze_btn or (st.session_state.get("skill_gap") and st.session_state.get("target_role") == target_role):
    if analyze_btn:
        with st.spinner("Analyzing skill gap..."):
            st.session_state.target_role = target_role
            gap = analyze_skill_gap(profile.get("skills", []), target_role)
            st.session_state.skill_gap = gap

    gap = st.session_state.skill_gap
    if not gap or "error" in gap:
        st.error("Could not analyze skill gap.")
        st.stop()

    coverage = gap.get("coverage", {})

    # ── Coverage Metrics ──────────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Overall Coverage", f"{coverage.get('overall', 0):.0f}%",
                  delta=f"+{max(0, coverage.get('overall',0)-50):.0f}% above avg")
    with c2:
        st.metric("Required Skills Met", f"{len(gap.get('matched_skills',[]))}/{gap.get('total_required',0)}")
    with c3:
        st.metric("Missing Critical", len(gap.get("missing_core_skills", [])), delta_color="inverse")
    with c4:
        strength = gap.get("skill_strength", {})
        st.metric("Skill Level", strength.get("level", "—"))

    # ── Role Info ─────────────────────────────────────────────────────────────────
    col_info, col_chart = st.columns([1, 2])
    with col_info:
        st.markdown(f"""
        <div class="card">
            <h4 style="color:#f0f0f5;margin:0 0 0.75rem 0;">📌 {target_role}</h4>
            <p style="color:#9898b0;font-size:0.875rem;margin:0 0 1rem 0;">{gap.get('role_description','')}</p>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
                <div>
                    <span style="color:#5a5a72;font-size:0.78rem;">💰 Avg Salary</span>
                    <div style="color:#22c55e;font-weight:700;font-size:0.9rem;">{gap.get('avg_salary','—')}</div>
                </div>
                <div>
                    <span style="color:#5a5a72;font-size:0.78rem;">📈 Market Growth</span>
                    <div style="color:#3b82f6;font-weight:700;font-size:0.9rem;">{gap.get('market_growth','—')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Coverage bar chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(
            skill_coverage_bar(gap.get("matched_skills", []), gap.get("missing_skills", [])),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_chart:
        from backend.services.skill_analyzer import get_role_info
        role_data = get_role_info(target_role) or {}
        required = role_data.get("required_skills", [])[:8]
        st.plotly_chart(
            skill_radar(profile.get("skills", []), required, target_role),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Skills Breakdown ──────────────────────────────────────────────────────────
    st.markdown("---")
    tab_have, tab_miss, tab_priority, tab_certs = st.tabs([
        "✅ Skills You Have", "❌ Missing Skills", "🔥 Priority Skills", "📜 Recommended Certs"
    ])

    with tab_have:
        matched = gap.get("matched_skills", [])
        if matched:
            tags = "".join([f'<span class="skill-tag skill-tag-have">✓ {s}</span>' for s in matched])
            st.markdown(f'<div style="line-height:2.2;">{tags}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warning">No matching skills found for this role.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        preferred = gap.get("matched_preferred", [])
        if preferred:
            st.markdown("**Bonus: Preferred Skills You Also Have**")
            tags2 = "".join([f'<span class="skill-tag skill-tag-neutral">⭐ {s}</span>' for s in preferred])
            st.markdown(f'<div style="line-height:2.2;">{tags2}</div>', unsafe_allow_html=True)

    with tab_miss:
        missing = gap.get("missing_skills", [])
        if missing:
            tags = "".join([f'<span class="skill-tag skill-tag-missing">✗ {s}</span>' for s in missing])
            st.markdown(f'<div style="line-height:2.2;">{tags}</div>', unsafe_allow_html=True)
        else:
            st.success("🎉 Excellent! You have all the required skills for this role!")

        missing_pref = gap.get("missing_preferred", [])
        if missing_pref:
            st.markdown("---")
            st.markdown("**Nice-to-Have Skills (Not Required)**")
            tags3 = "".join([f'<span class="skill-tag" style="background:rgba(90,90,114,0.12);color:#5a5a72;border:1px solid rgba(90,90,114,0.2);">{s}</span>' for s in missing_pref])
            st.markdown(f'<div style="line-height:2.2;">{tags3}</div>', unsafe_allow_html=True)

    with tab_priority:
        priority_skills = gap.get("priority_skills", [])
        if priority_skills:
            for skill_info in priority_skills:
                priority_color = "#ef4444" if skill_info["priority"] == "Critical" else "#f97316"
                st.markdown(f"""
                <div class="question-card" style="border-left-color:{priority_color};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div style="color:#f0f0f5;font-weight:700;font-size:0.9rem;">
                                {skill_info['skill']}
                            </div>
                            <div style="color:#9898b0;font-size:0.8rem;margin-top:0.2rem;">
                                {skill_info.get('reason','')}
                            </div>
                        </div>
                        <div style="text-align:right;flex-shrink:0;">
                            <span style="background:rgba(255,255,255,0.05);color:{priority_color};
                                border:1px solid {priority_color}33;border-radius:999px;
                                padding:0.2rem 0.6rem;font-size:0.75rem;font-weight:700;">
                                {skill_info['priority']}
                            </span>
                            <div style="color:#5a5a72;font-size:0.75rem;margin-top:0.3rem;">
                                ⏱ {skill_info.get('learn_time','')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No critical skills missing!")

    with tab_certs:
        certs = gap.get("recommended_certifications", [])
        if certs:
            for cert in certs:
                st.markdown(f"""
                <div class="card" style="margin-bottom:0.5rem;">
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                        <div style="font-size:1.2rem;">🏆</div>
                        <div>
                            <div style="color:#f0f0f5;font-weight:600;font-size:0.875rem;">{cert}</div>
                            <div style="color:#9898b0;font-size:0.78rem;">Industry recognized certification</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific certifications listed for this role.")

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🎯</div>
        <p style="color:#9898b0;">Select a target role and click Analyze Gap</p>
    </div>
    """, unsafe_allow_html=True)
