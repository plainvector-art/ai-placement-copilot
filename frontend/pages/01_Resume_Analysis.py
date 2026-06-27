"""
Page 1: Resume Analysis
Upload resume, view parsed profile, and get ATS score.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import ats_gauge, ats_breakdown_bar
from backend.services.resume_parser import parse_resume
from backend.services.ats_scorer import calculate_ats_score
from backend.utils.file_handler import save_uploaded_file

st.set_page_config(page_title="Resume Analysis | Placement Copilot", page_icon="📄", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">📄 Resume Analysis</div>
    <p class="hero-subtitle">Upload your resume for AI-powered ATS scoring and profile extraction</p>
</div>
""", unsafe_allow_html=True)

# ── Upload Section ──────────────────────────────────────────────────────────────
col_upload, col_info = st.columns([3, 2])

with col_upload:
    st.markdown('<div class="section-header"><div class="section-icon">📁</div><h3 class="section-title">Upload Resume</h3></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drag & drop your resume",
        type=["pdf", "docx"],
        help="Supports PDF and DOCX files up to 10MB",
        label_visibility="collapsed",
    )

    if uploaded_file:
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        st.markdown(f"""
        <div class="alert-info">
            📎 <strong>{uploaded_file.name}</strong> &nbsp;·&nbsp; {file_size_kb:.1f} KB &nbsp;·&nbsp; {uploaded_file.type}
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔍 Analyze Resume", use_container_width=True):
            with st.spinner("🤖 Parsing resume and extracting profile..."):
                try:
                    # Save file
                    file_path = save_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)

                    # Parse
                    profile = parse_resume(file_path)
                    st.session_state.profile = profile

                    # ATS Score
                    ats = calculate_ats_score(profile, st.session_state.get("target_role"))
                    st.session_state.ats_score = ats
                    st.session_state.skill_gap = None  # Reset dependent

                    st.success(f"✅ Resume analyzed successfully for **{profile.get('name', 'candidate')}**!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with col_info:
    st.markdown("""
    <div class="card">
        <h4 style="color:#f0f0f5;margin:0 0 1rem 0;">What we extract</h4>
        <div style="display:flex;flex-direction:column;gap:0.5rem;">
            <div style="color:#9898b0;font-size:0.875rem;">✅ Name & Contact Info</div>
            <div style="color:#9898b0;font-size:0.875rem;">✅ Education & GPA</div>
            <div style="color:#9898b0;font-size:0.875rem;">✅ Work Experience</div>
            <div style="color:#9898b0;font-size:0.875rem;">✅ Technical Skills</div>
            <div style="color:#9898b0;font-size:0.875rem;">✅ Projects & GitHub Links</div>
            <div style="color:#9898b0;font-size:0.875rem;">✅ Certifications</div>
            <div style="color:#9898b0;font-size:0.875rem;">✅ Achievements</div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.06);margin:1rem 0;">
        <div style="color:#5a5a72;font-size:0.78rem;">
            🔒 Files are processed locally and not stored permanently.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.get("profile") and st.session_state.get("ats_score"):
    profile = st.session_state.profile
    ats = st.session_state.ats_score

    st.markdown("---")

    # Profile Overview
    tab1, tab2, tab3 = st.tabs(["📊 ATS Score", "👤 Profile", "💡 Suggestions"])

    with tab1:
        col_gauge, col_breakdown = st.columns([2, 3])

        with col_gauge:
            st.plotly_chart(
                ats_gauge(ats["overall_score"]),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            # Rating badge
            rating = ats.get("rating", "")
            color_map = {"Excellent": "#22c55e", "Good": "#3b82f6", "Fair": "#f97316", "Needs Improvement": "#ef4444"}
            color = color_map.get(rating, "#8b5cf6")
            st.markdown(f"""
            <div style="text-align:center;padding:0.5rem;">
                <span style="background:rgba(255,255,255,0.05);border:1px solid {color}33;
                    color:{color};padding:0.4rem 1.2rem;border-radius:999px;
                    font-weight:700;font-size:0.9rem;">
                    {rating}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col_breakdown:
            st.markdown("#### Score Breakdown")
            st.plotly_chart(
                ats_breakdown_bar(ats["weighted_scores"], ats["weights"]),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        # Quick stats row
        stats = ats.get("stats", {})
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Skills", stats.get("total_skills", 0))
        with c2:
            st.metric("Projects", stats.get("total_projects", 0))
        with c3:
            st.metric("Experience", stats.get("total_experience", 0))
        with c4:
            st.metric("Word Count", stats.get("word_count", 0))

    with tab2:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### 👤 Contact Info")
            st.markdown(f"""
            <div class="card">
                <table style="width:100%;border-collapse:collapse;">
                    <tr><td style="color:#5a5a72;font-size:0.8rem;padding:4px 0;width:35%;">Name</td>
                        <td style="color:#f0f0f5;font-size:0.875rem;">{profile.get('name','—')}</td></tr>
                    <tr><td style="color:#5a5a72;font-size:0.8rem;padding:4px 0;">Email</td>
                        <td style="color:#f0f0f5;font-size:0.875rem;">{profile.get('email','—')}</td></tr>
                    <tr><td style="color:#5a5a72;font-size:0.8rem;padding:4px 0;">Phone</td>
                        <td style="color:#f0f0f5;font-size:0.875rem;">{profile.get('phone','—')}</td></tr>
                    <tr><td style="color:#5a5a72;font-size:0.8rem;padding:4px 0;">LinkedIn</td>
                        <td style="color:#f0f0f5;font-size:0.875rem;">{profile.get('linkedin','—')}</td></tr>
                    <tr><td style="color:#5a5a72;font-size:0.8rem;padding:4px 0;">GitHub</td>
                        <td style="color:#f0f0f5;font-size:0.875rem;">{profile.get('github','—')}</td></tr>
                    <tr><td style="color:#5a5a72;font-size:0.8rem;padding:4px 0;">Location</td>
                        <td style="color:#f0f0f5;font-size:0.875rem;">{profile.get('location','—')}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🎓 Education")
            for edu in profile.get("education", [])[:3]:
                st.markdown(f"""
                <div class="card" style="margin-bottom:0.5rem;">
                    <div style="color:#f0f0f5;font-size:0.875rem;font-weight:600;">{edu.get('degree','')}</div>
                    <div style="color:#9898b0;font-size:0.8rem;">{edu.get('year','')}</div>
                </div>
                """, unsafe_allow_html=True)

        with c2:
            st.markdown("#### 💡 Skills")
            skills = profile.get("skills", [])
            if skills:
                tags_html = "".join([
                    f'<span class="skill-tag skill-tag-neutral">{s}</span>' for s in skills
                ])
                st.markdown(f'<div style="line-height:2;">{tags_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-warning">No skills detected. Ensure your resume has a Skills section.</div>', unsafe_allow_html=True)

            st.markdown("#### 📜 Certifications")
            certs = profile.get("certifications", [])
            if certs:
                for cert in certs[:5]:
                    st.markdown(f'<div style="color:#9898b0;font-size:0.875rem;padding:2px 0;">🏆 {cert}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-warning">No certifications found.</div>', unsafe_allow_html=True)

        # Projects
        st.markdown("#### 🚀 Projects")
        projects = profile.get("projects", [])
        if projects:
            proj_cols = st.columns(min(len(projects), 3))
            for i, proj in enumerate(projects[:3]):
                with proj_cols[i]:
                    tech_html = "".join([f'<span class="skill-tag skill-tag-neutral" style="font-size:0.7rem;">{t}</span>' for t in (proj.get("technologies", [])[:4])])
                    st.markdown(f"""
                    <div class="card">
                        <div style="font-size:0.9rem;font-weight:700;color:#f0f0f5;margin-bottom:0.5rem;">
                            {proj.get('title','Project')}
                        </div>
                        <div style="font-size:0.8rem;color:#9898b0;margin-bottom:0.75rem;line-height:1.5;">
                            {str(proj.get('description',''))[:150]}...
                        </div>
                        <div>{tech_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warning">⚠️ No projects detected. Add a Projects section to your resume.</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("#### 💡 Improvement Suggestions")
        suggestions = ats.get("suggestions", [])
        for i, sug in enumerate(suggestions, 1):
            priority = "🔴" if i <= 3 else ("🟡" if i <= 6 else "🟢")
            st.markdown(f"""
            <div class="question-card" style="margin-bottom:0.5rem;">
                <div style="display:flex;align-items:flex-start;gap:0.75rem;">
                    <span style="font-size:1rem;">{priority}</span>
                    <div style="color:#f0f0f5;font-size:0.875rem;">{sug}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📤 Export Options")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📋 Copy Profile JSON", use_container_width=True):
                import json
                st.code(json.dumps(profile, indent=2, default=str), language="json")

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:4rem;margin-bottom:1rem;">📄</div>
        <h3 style="color:#f0f0f5;">Upload your resume to get started</h3>
        <p style="color:#5a5a72;">Drag and drop a PDF or DOCX file above</p>
    </div>
    """, unsafe_allow_html=True)
