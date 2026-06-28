"""Page 8: AI Career Coach Chatbot + Premium Tools"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from backend.services.career_coach import (
    chat_with_coach, generate_cover_letter,
    generate_linkedin_headline, predict_career_path
)
from backend.services.ai_client import has_api_key

st.set_page_config(page_title="Career Coach | Placement Copilot", page_icon="💬", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">💬 AI Career Coach</div>
    <p class="hero-subtitle">Your personal AI career advisor — ask anything about your career journey</p>
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

tab_chat, tab_cover, tab_linkedin, tab_career = st.tabs([
    "💬 Career Chat", "✉️ Cover Letter", "🔗 LinkedIn Profile", "🚀 Career Path"
])

# ── Tab 1: Career Chat ─────────────────────────────────────────────────────────
with tab_chat:
    # Quick prompts
    st.markdown("**Quick Questions:**")
    quick_prompts = [
        "What should I learn first to land a job?",
        "How do I crack placements at top companies?",
        "Which projects should I build for my portfolio?",
        "How do I negotiate my salary?",
        "How do I prepare for system design interviews?",
        "Review my profile and give improvement tips",
    ]

    prompt_cols = st.columns(3)
    for i, prompt in enumerate(quick_prompts):
        with prompt_cols[i % 3]:
            if st.button(prompt, key=f"qp_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.spinner("Coach is responding..."):
                    gap = st.session_state.get("skill_gap")
                    response = chat_with_coach(prompt, profile, target_role, st.session_state.chat_history, gap)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    st.markdown("---")

    # Chat history display
    chat_display = st.container()
    with chat_display:
        if not st.session_state.chat_history:
            st.markdown(f"""
            <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
                 border-radius:16px;padding:2rem;text-align:center;">
                <div style="font-size:2.5rem;margin-bottom:0.75rem;">🤖</div>
                <h4 style="color:#f0f0f5;margin:0 0 0.5rem 0;">CareerCopilot AI</h4>
                <p style="color:#9898b0;margin:0;font-size:0.9rem;">
                    I'm your personal career coach, with full context about your profile.<br>
                    Ask me anything — skill gaps, interview prep, career planning, or salary negotiation.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                is_ai = msg["role"] == "assistant"
                if is_ai:
                    st.markdown(f"""
                    <div style="display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:1.25rem;">
                        <div style="background:linear-gradient(135deg,#8b5cf6,#3b82f6);width:36px;height:36px;
                             border-radius:50%;display:flex;align-items:center;justify-content:center;
                             color:white;font-weight:700;flex-shrink:0;">C</div>
                        <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
                             border-radius:12px;border-top-left-radius:4px;padding:1rem 1.25rem;
                             max-width:90%;font-size:0.875rem;color:#f0f0f5;line-height:1.7;
                             white-space:pre-wrap;">
                            {msg['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:1.25rem;
                         justify-content:flex-end;">
                        <div style="background:#e9c176;
                             border-radius:12px;border-top-right-radius:4px;padding:0.75rem 1rem;
                             max-width:75%;font-size:0.875rem;color:#1b3022;line-height:1.6;font-weight:500;">
                            {msg['content']}
                        </div>
                        <div style="background:rgba(233,193,118,0.15);border:1px solid rgba(233,193,118,0.3);
                             width:36px;height:36px;border-radius:50%;display:flex;align-items:center;
                             justify-content:center;color:#e9c176;flex-shrink:0;font-weight:700;">U</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Input
    st.markdown("---")
    user_input = st.text_input(
        "Ask your career coach",
        placeholder="Ask me anything about your career, skills, or interview preparation...",
        label_visibility="collapsed",
        key="coach_input",
    )

    col_send, col_clear = st.columns([5, 1])
    with col_send:
        send_btn = st.button("💬 Send Message", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if send_btn and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Coach is thinking..."):
            gap = st.session_state.get("skill_gap")
            response = chat_with_coach(user_input, profile, target_role, st.session_state.chat_history, gap)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ── Tab 2: Cover Letter ────────────────────────────────────────────────────────
with tab_cover:
    st.markdown("#### ✉️ AI Cover Letter Generator")
    col_cl1, col_cl2 = st.columns(2)
    with col_cl1:
        company = st.text_input("Company Name (optional)", placeholder="e.g., Google, Startup XYZ")
    with col_cl2:
        pass

    jd_for_cl = st.text_area(
        "Job Description (optional — improves personalization)",
        height=100,
        placeholder="Paste the job description to generate a more targeted cover letter...",
    )

    if st.button("✉️ Generate Cover Letter", use_container_width=False):
        with st.spinner("Crafting your personalized cover letter..."):
            letter = generate_cover_letter(profile, target_role, company, jd_for_cl)
            st.session_state["cover_letter"] = letter

    if st.session_state.get("cover_letter"):
        st.markdown("---")
        st.markdown(f"""
        <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
             border-radius:12px;padding:2rem;font-family:'Inter',sans-serif;
             font-size:0.9rem;color:#f0f0f5;line-height:1.8;white-space:pre-wrap;">
{st.session_state['cover_letter']}
        </div>
        """, unsafe_allow_html=True)

        col_copy, col_dl = st.columns(2)
        with col_dl:
            st.download_button(
                "📥 Download Cover Letter",
                data=st.session_state["cover_letter"],
                file_name=f"cover_letter_{target_role.replace(' ','_')}.txt",
                mime="text/plain",
            )

# ── Tab 3: LinkedIn Profile ─────────────────────────────────────────────────────
with tab_linkedin:
    st.markdown("#### 🔗 LinkedIn Profile Generator")
    st.markdown("*Generate professional LinkedIn headline and About section tailored to your profile*")

    if st.button("🔗 Generate LinkedIn Content", use_container_width=False):
        with st.spinner("Crafting your LinkedIn profile..."):
            result = generate_linkedin_headline(profile, target_role)
            st.session_state["linkedin_result"] = result

    if st.session_state.get("linkedin_result"):
        li = st.session_state["linkedin_result"]

        st.markdown("#### 🎯 Headline Options")
        headlines = li.get("headlines", [])
        for i, h in enumerate(headlines, 1):
            st.markdown(f"""
            <div class="card" style="margin-bottom:0.5rem;cursor:pointer;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="color:#f0f0f5;font-size:0.9rem;">{h}</div>
                    <span style="color:#a78bfa;font-size:0.78rem;font-weight:700;">Option {i}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 📝 About Section")
        about = li.get("about_section", "")
        st.markdown(f"""
        <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
             border-radius:12px;padding:1.5rem;white-space:pre-wrap;
             font-size:0.875rem;color:#f0f0f5;line-height:1.8;">
{about}
        </div>
        """, unsafe_allow_html=True)

        skills_to_add = li.get("skills_to_add", [])
        if skills_to_add:
            st.markdown("**📌 Skills to add to LinkedIn:**")
            tags = "".join([f'<span class="skill-tag skill-tag-neutral">{s}</span>' for s in skills_to_add])
            st.markdown(f'<div style="line-height:2.5;">{tags}</div>', unsafe_allow_html=True)

        if li.get("connection_message_template"):
            st.markdown("**💬 Connection Request Template:**")
            st.markdown(f'<div class="alert-info">{li["connection_message_template"]}</div>', unsafe_allow_html=True)

        if about:
            st.download_button("📥 Download LinkedIn Content", data=f"HEADLINE OPTIONS:\n{'\\n'.join(headlines)}\n\nABOUT SECTION:\n{about}", file_name="linkedin_content.txt", mime="text/plain")

# ── Tab 4: Career Path ──────────────────────────────────────────────────────────
with tab_career:
    st.markdown("#### 🚀 Career Path Predictor")
    st.markdown("*See a realistic 5-year career trajectory from your current position*")

    if st.button("🔮 Predict Career Path", use_container_width=False):
        with st.spinner("Analyzing your career trajectory..."):
            path = predict_career_path(profile, target_role)
            st.session_state["career_path"] = path

    if st.session_state.get("career_path"):
        cp = st.session_state["career_path"]

        st.markdown(f"""
        <div class="alert-info">
            <strong>Current Level:</strong> {cp.get('current_level','')} &nbsp;·&nbsp;
            <strong>Trajectory:</strong> {cp.get('salary_trajectory','')}
        </div>
        """, unsafe_allow_html=True)

        path_items = cp.get("path", [])
        for item in path_items:
            yr = item.get("year", 0)
            role_name = item.get("role", "")
            salary = item.get("salary_range", "")
            milestone = item.get("milestone", "")
            skills_needed = ", ".join(item.get("key_skills", [])[:3])

            year_color = "#8b5cf6" if yr == 0 else ("#3b82f6" if yr <= 2 else "#22c55e")
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-dot" style="background:linear-gradient(135deg,{year_color},{year_color}88);">
                    Y{yr}
                </div>
                <div class="timeline-content">
                    <div style="display:flex;justify-content:space-between;">
                        <div style="color:#f0f0f5;font-weight:700;font-size:0.9rem;">{role_name}</div>
                        <div style="color:#22c55e;font-weight:700;font-size:0.875rem;">{salary}</div>
                    </div>
                    {f'<div style="color:#9898b0;font-size:0.8rem;margin-top:0.2rem;">{milestone}</div>' if milestone else ''}
                    {f'<div style="color:#5a5a72;font-size:0.78rem;margin-top:0.2rem;">Skills: {skills_needed}</div>' if skills_needed else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

        alt_paths = cp.get("alternative_paths", [])
        if alt_paths:
            st.markdown("**Alternative Career Paths:**")
            for ap in alt_paths:
                st.markdown(f"↗️ {ap}")
