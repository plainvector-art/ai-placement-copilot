"""Page 11: Intelligent Candidate Ranker"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from backend.services.ai_client import is_ai_configured, get_ai_provider_info

st.set_page_config(
    page_title="Candidate Ranker | Placement Copilot",
    page_icon="🏆",
    layout="wide",
)

inject_css()

# Override styling to match the premium dark gold/beige design from the screenshot
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,0..700&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Global font overrides */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
}
p, span, div, a, li, label, .stMarkdown {
    font-family: 'Lora', serif !important;
}

/* Background gradient */
.stApp {
    background: radial-gradient(circle at top left, #151811 0%, #0a0c08 50%, #030403 100%) !important;
}

/* Header visible and transparent */
header {
    visibility: visible !important;
    background: transparent !important;
}

/* Sidebar Collapse/Expand Toggle Controls */
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] button {
    color: transparent !important;
    background: transparent !important;
    border: none !important;
    font-size: 0px !important;
}
[data-testid="collapsedControl"] *,
button[data-testid="stSidebarCollapseButton"] *,
section[data-testid="stSidebar"] button * {
    display: none !important;
}

/* Closed state - double arrow pointing right » */
[data-testid="collapsedControl"]::before {
    content: "»" !important;
    font-size: 1.8rem !important;
    color: #d4af37 !important;
    font-weight: 700 !important;
    display: inline-block !important;
    line-height: 1 !important;
}

/* Open state - double arrow pointing left « */
section[data-testid="stSidebar"] button::before,
button[data-testid="stSidebarCollapseButton"]::before {
    content: "«" !important;
    font-size: 1.8rem !important;
    color: #d4af37 !important;
    font-weight: 700 !important;
    display: inline-block !important;
    line-height: 1 !important;
}

/* Customize sidebar sidebar styling */
[data-testid="stSidebar"] {
    background: #090a07 !important;
    border-right: 1px solid rgba(212, 175, 55, 0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# API connection status in the sidebar
with st.sidebar:
    st.page_link("app.py", label="Home Dashboard", icon="🏠")
    st.markdown("---")
    st.markdown("### 🔌 API Integrations")
    if is_ai_configured():
        info = get_ai_provider_info()
        st.success(f"⚡ LLM Active: {info['model'].upper()}")
    else:
        st.warning("⚠️ Running in Demo Mode\n(Configure GEMINI_API_KEY in .env)")

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🏆 Intelligent Candidate Ranker</div>
    <p class="hero-subtitle">
        Paste a job description, upload candidate resumes, and get an AI-ranked shortlist
        with semantic fit scores, behavioral signals, and recruiter-ready verdicts.
    </p>
</div>
""", unsafe_allow_html=True)

# Layout — two-column input section
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 📝 Job Description")
    jd_text = st.text_area(
        "Job Description Input",
        placeholder="Paste the full job description here to extract requirements...",
        height=280,
        label_visibility="collapsed",
    )

with col_right:
    st.markdown("### 📂 Resumes")
    uploaded_files = st.file_uploader(
        "Upload Candidate Resumes (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    
    st.markdown("""
    <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
         border-radius:12px;padding:0.85rem 1rem;font-size:0.8rem;color:#9898b0;margin-top:0.75rem;">
        ⚡ Supports up to 20 resumes concurrently.<br>
        🎯 Powered by semantic vector search & LLM-generated recruiter insights.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Run button validation and display
is_disabled = not jd_text.strip() or not uploaded_files
if is_disabled:
    st.button("🚀 Rank Candidates", use_container_width=True, type="primary", disabled=True)
    st.warning("⚠️ Please paste a Job Description and upload at least one candidate resume to begin.")
    run_btn = False
else:
    run_btn = st.button("🚀 Rank Candidates", use_container_width=True, type="primary")

# Processing logic
if run_btn:
    with st.spinner("Processing resumes and generating recruiter insights..."):
        # Step 1: parse JD
        from backend.services.jd_parser import parse_job_description
        jd_parsed = parse_job_description(jd_text)

        # Step 2: parse all resumes
        from backend.services.resume_parser import parse_resume
        from backend.utils.file_handler import save_uploaded_file, cleanup_file
        profiles = []
        for uploaded_file in uploaded_files:
            path = None
            try:
                path = save_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)
                profile = parse_resume(path)
                profile["source_filename"] = uploaded_file.name
                profiles.append(profile)
            except Exception as e:
                st.error(f"Failed to parse {uploaded_file.name}: {e}")
                continue
            finally:
                if path:
                    cleanup_file(path)

        # Step 3: semantic ranking
        from backend.services.semantic_ranker import rank_candidates
        ranked = rank_candidates(profiles, jd_text)

        # Step 4: compute ATS and signal scores, fuse all three, and generate AI insights
        from backend.services.ats_scorer import calculate_ats_score
        from backend.services.signal_scorer import compute_signals, fuse_scores
        from backend.services.explainability import explain_rank
        from backend.services.recruiter_insights import generate_candidate_insights

        results = []
        for i, candidate in enumerate(ranked):
            ats = calculate_ats_score(candidate)
            signals = compute_signals(candidate)
            scores = fuse_scores(
                semantic_score=candidate["semantic_score"],
                ats_score=ats.get("overall_score", 0),
                signal_score=signals["composite_signal_score"],
            )
            explanation = explain_rank(candidate, signals, scores, jd_parsed, rank=i+1)
            insights = generate_candidate_insights(candidate, scores, jd_parsed)
            results.append({
                "profile": candidate,
                "ats": ats,
                "signals": signals,
                "scores": scores,
                "explanation": explanation,
                "insights": insights,
            })

        st.session_state["ranker_results"] = results
        st.session_state["ranker_jd_parsed"] = jd_parsed
        st.rerun()

# Helper for drawing custom styled progress bars
def draw_progress_bar(label: str, value: float, color: str):
    st.markdown(f"""
    <div style="margin-bottom:0.9rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;">
            <span style="font-size:0.8rem;color:#9898b0;font-weight:600;">{label}</span>
            <span style="font-size:0.85rem;color:{color};font-weight:700;">{value:.1f}%</span>
        </div>
        <div style="width:100%;height:7px;background:rgba(255,255,255,0.04);border-radius:4px;overflow:hidden;">
            <div style="width:{value}%;height:100%;background:{color};border-radius:4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Results display
results = st.session_state.get("ranker_results")
jd_parsed = st.session_state.get("ranker_jd_parsed")

if results and jd_parsed:
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Candidates Ranked", len(results))
    col_b.metric("Top Score", f"{results[0]['scores']['final_score']}%")
    col_c.metric("Target Role", jd_parsed.get("role_title", "—"))

    with st.expander("📋 Parsed Job Requirements", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Must-have skills**")
            for s in jd_parsed.get("required_skills", []):
                st.markdown(f"- {s}")
        with col2:
            st.markdown("**Nice-to-have skills**")
            for s in jd_parsed.get("preferred_skills", []):
                st.markdown(f"- {s}")
        st.markdown(f"**Seniority:** {jd_parsed.get('seniority_level', '—')} &nbsp;|&nbsp; "
                    f"**Domain:** {jd_parsed.get('domain', '—')} &nbsp;|&nbsp; "
                    f"**Min Experience:** {jd_parsed.get('minimum_experience_years', '—')} yrs",
                    unsafe_allow_html=True)

    st.markdown("### 🏆 Candidate Shortlist")
    
    for result in results:
        rank = result["explanation"]["rank"]
        name = result["explanation"]["candidate_name"]
        filename = result["profile"].get("source_filename", "")
        final_score = result["scores"]["final_score"]
        verdict = result["explanation"]["recruiter_verdict"]
        
        verdict_color = {
            "Strong shortlist": "#22c55e",
            "Consider": "#f97316",
            "Deprioritise": "#ef4444",
        }.get(verdict, "#9898b0")

        with st.container():
            st.markdown(f"""
            <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.07);
                 border-left: 3px solid {verdict_color};
                 border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <span style="font-size:1.05rem;font-weight:700;color:#f0f0f5;">
                            #{rank} — {name}
                        </span>
                        <span style="margin-left:12px;font-size:0.78rem;color:#9898b0;">
                            {filename}
                        </span>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:1.4rem;font-weight:800;color:{verdict_color};">
                            {final_score}%
                        </span>
                        <div style="font-size:0.72rem;color:{verdict_color};font-weight:600;">
                            {verdict}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Details — {name}", expanded=(rank == 1)):
                tab_insights, tab_metrics, tab_strengths, tab_skills = st.tabs([
                    "🤖 AI Recruiter Insights", "📊 Fit Metrics", "💡 Strengths & Gaps", "🛠️ Technical Stack"
                ])
                
                # Tab 1: AI Insights
                with tab_insights:
                    insights = result.get("insights", {})
                    st.markdown(f"""
                    <div style="background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.15);
                         border-radius:12px;padding:1rem;margin-bottom:1rem;color:#f0f0f5;line-height:1.6;font-size:0.9rem;">
                        {insights.get('fit_analysis')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_vetting, col_questions = st.columns(2)
                    with col_vetting:
                        st.markdown("**🔍 Technical Vetting Focus**")
                        for pt in insights.get('technical_vetting_points', []):
                            st.markdown(f"• {pt}")
                    with col_questions:
                        st.markdown("**💬 Suggested Interview Questions**")
                        for q in insights.get('suggested_interview_questions', []):
                            st.markdown(f"• *\"{q}\"*")
                
                # Tab 2: Fit Metrics
                with tab_metrics:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("Final Fusion Score", f"{final_score}%")
                        # Add quick visual indicators for social profile presence
                        github_url = result["profile"].get("github")
                        linkedin_url = result["profile"].get("linkedin")
                        badges = []
                        if github_url:
                            badges.append(f'<a href="https://{github_url}" target="_blank" style="text-decoration:none;"><span style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);color:#f0f0f5;padding:0.25rem 0.5rem;border-radius:6px;font-size:0.75rem;margin-right:0.5rem;">💻 GitHub</span></a>')
                        if linkedin_url:
                            badges.append(f'<a href="https://{linkedin_url}" target="_blank" style="text-decoration:none;"><span style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);color:#60a5fa;padding:0.25rem 0.5rem;border-radius:6px;font-size:0.75rem;">👔 LinkedIn</span></a>')
                        if badges:
                            st.markdown(f'<div style="margin-top:0.75rem;">{"".join(badges)}</div>', unsafe_allow_html=True)
                            
                    with col2:
                        draw_progress_bar("Semantic Fit (50% weight)", result['scores']['semantic_score'], "#8b5cf6")
                        draw_progress_bar("ATS Score (30% weight)", result['scores']['ats_score'], "#3b82f6")
                        draw_progress_bar("Behavioral Signals (20% weight)", result['scores']['signal_score'], "#f97316")
                
                # Tab 3: Strengths & Gaps
                with tab_strengths:
                    col_str, col_gap = st.columns(2)
                    with col_str:
                        st.markdown("**✅ Strengths**")
                        for s in result["explanation"]["strengths"]:
                             st.markdown(f"• {s}")
                    with col_gap:
                        st.markdown("**⚠️ Areas to Investigate / Gaps**")
                        for g in result["explanation"]["gaps"]:
                             st.markdown(f"• {g}")
                
                # Tab 4: Skills & Profile
                with tab_skills:
                    skills_str = ", ".join(result["profile"].get("skills", [])[:15])
                    st.markdown(f"**Detected Technical Skills:** {skills_str}")
                    st.markdown(f"**Resume Word Count:** {result['profile'].get('total_words', 0)} words &nbsp;|&nbsp; **Education Detected:** {len(result['profile'].get('education', []))} entry(ies)", unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏆</div>
        <p style="color:#9898b0;">Paste a job description and upload candidate resumes above to rank them</p>
    </div>
    """, unsafe_allow_html=True)
