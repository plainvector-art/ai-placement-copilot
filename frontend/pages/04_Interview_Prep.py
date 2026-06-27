"""Page 4: Interview Prep — AI Question Generator"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from backend.services.interview_gen import generate_interview_questions

st.set_page_config(page_title="Interview Prep | Placement Copilot", page_icon="❓", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">❓ Interview Question Bank</div>
    <p class="hero-subtitle">AI-generated questions tailored to your resume, projects, and target role</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("profile"):
    st.warning("⚠️ Please upload your resume first.")
    st.stop()

profile = st.session_state.profile
target_role = st.session_state.get("target_role", "Software Engineer")

col_cfg, col_btn = st.columns([3, 1])
with col_cfg:
    difficulty = st.select_slider(
        "Question Difficulty",
        options=["Easy", "Mixed", "Hard"],
        value="Mixed",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🤖 Generate Questions", use_container_width=True)

if generate_btn:
    with st.spinner(f"🤖 Generating 40 personalized questions for {target_role}..."):
        questions = generate_interview_questions(profile, target_role, difficulty)
        st.session_state.interview_questions = questions
        st.success("✅ Questions generated!")
        st.rerun()

questions = st.session_state.get("interview_questions")

if questions:
    meta = questions.get("metadata", {})
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Questions", meta.get("total_questions", 0))
    with c2: st.metric("HR Questions", len(questions.get("hr_questions", [])))
    with c3: st.metric("Technical", len(questions.get("technical_questions", [])))
    with c4: st.metric("Project-Based", len(questions.get("project_questions", [])))

    st.markdown("---")

    tab_hr, tab_tech, tab_proj, tab_beh = st.tabs([
        f"🤝 HR ({len(questions.get('hr_questions',[]))})",
        f"💻 Technical ({len(questions.get('technical_questions',[]))})",
        f"🚀 Project ({len(questions.get('project_questions',[]))})",
        f"🧠 Behavioral ({len(questions.get('behavioral_questions',[]))})",
    ])

    def render_questions(q_list, category):
        category_colors = {
            "HR": "#3b82f6",
            "Technical": "#8b5cf6",
            "Project": "#06b6d4",
            "Behavioral": "#f97316",
        }
        color = category_colors.get(category, "#8b5cf6")
        for q in q_list:
            difficulty_badge = q.get("difficulty", "Medium")
            diff_colors = {"Easy": "#22c55e", "Medium": "#f97316", "Hard": "#ef4444"}
            dc = diff_colors.get(difficulty_badge, "#9898b0")

            with st.expander(f"Q{q.get('id','')}: {q.get('question','')}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if q.get("tip"):
                        st.markdown(f"""
                        <div class="alert-info">
                            💡 <strong>Tip:</strong> {q['tip']}
                        </div>
                        """, unsafe_allow_html=True)
                    if q.get("expected_topics"):
                        topics = ", ".join(q["expected_topics"])
                        st.markdown(f"**Cover these topics:** {topics}")
                    if q.get("framework"):
                        st.markdown(f"""
                        <div class="alert-success">
                            📐 Use the <strong>{q['framework']}</strong> framework: 
                            Situation → Task → Action → Result
                        </div>
                        """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="text-align:right;">
                        <span style="background:{dc}22;color:{dc};border:1px solid {dc}33;
                             padding:0.2rem 0.6rem;border-radius:999px;font-size:0.78rem;font-weight:700;">
                            {difficulty_badge}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_hr:
        st.markdown("*General HR and background questions — focus on storytelling and genuine answers*")
        render_questions(questions.get("hr_questions", []), "HR")

    with tab_tech:
        st.markdown("*Technical questions specific to your target role — show your depth*")
        render_questions(questions.get("technical_questions", []), "Technical")

    with tab_proj:
        st.markdown("*Deep-dive questions about your actual projects — know every detail*")
        render_questions(questions.get("project_questions", []), "Project")

    with tab_beh:
        st.markdown("*Behavioral questions — use the STAR method (Situation, Task, Action, Result)*")
        render_questions(questions.get("behavioral_questions", []), "Behavioral")

    # Export
    st.markdown("---")
    if st.button("📋 Export All Questions"):
        import json
        output = ""
        for category, key in [("HR Questions", "hr_questions"), ("Technical Questions", "technical_questions"),
                               ("Project Questions", "project_questions"), ("Behavioral Questions", "behavioral_questions")]:
            output += f"\n\n## {category}\n\n"
            for q in questions.get(key, []):
                output += f"Q{q.get('id','')}: {q.get('question','')}\n"
                if q.get('tip'): output += f"Tip: {q['tip']}\n"
                output += "\n"

        st.download_button(
            "📥 Download as Text",
            data=output,
            file_name=f"interview_questions_{target_role.replace(' ','_')}.txt",
            mime="text/plain",
        )

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">❓</div>
        <p style="color:#9898b0;">Click "Generate Questions" to create your personalized question bank</p>
        <p style="color:#5a5a72;font-size:0.85rem;">Questions are based on your resume, projects, and target role</p>
    </div>
    """, unsafe_allow_html=True)
