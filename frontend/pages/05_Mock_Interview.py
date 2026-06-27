"""Page 5: AI Mock Interview Simulator"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.components.styles import inject_css
from frontend.components.charts import interview_performance_radar
from backend.services.mock_interview import start_interview, process_response, evaluate_interview

st.set_page_config(page_title="Mock Interview | Placement Copilot", page_icon="🤖", layout="wide")
inject_css()

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🤖 AI Mock Interview</div>
    <p class="hero-subtitle">Practice with Alex, your AI interviewer — personalized questions, real-time responses</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("profile"):
    st.warning("⚠️ Please upload your resume first.")
    st.stop()

profile = st.session_state.profile
target_role = st.session_state.get("target_role", "Software Engineer")

# ── Session Management ─────────────────────────────────────────────────────────
mock_session = st.session_state.get("mock_session")

if not mock_session:
    # Start screen
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(22,22,31,0.9),rgba(26,16,40,0.9));
         border:1px solid rgba(139,92,246,0.2);border-radius:16px;padding:2rem;margin-bottom:2rem;">
        <div style="display:flex;gap:1.5rem;align-items:flex-start;">
            <div style="background:linear-gradient(135deg,#8b5cf6,#3b82f6);width:56px;height:56px;
                 border-radius:50%;display:flex;align-items:center;justify-content:center;
                 font-size:1.5rem;flex-shrink:0;">🤖</div>
            <div>
                <h3 style="color:#f0f0f5;margin:0 0 0.5rem 0;">Meet Alex, your AI Interviewer</h3>
                <p style="color:#9898b0;margin:0;font-size:0.9rem;">
                    Alex will conduct a 15-question mock interview for the 
                    <strong style="color:#a78bfa;">{target_role}</strong> role, 
                    personalized to your actual resume and projects. 
                    You'll receive detailed performance feedback at the end.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-value">15</span>
            <span class="stat-label">Questions</span>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-value">~30</span>
            <span class="stat-label">Minutes</span>
        </div>
        """, unsafe_allow_html=True)
    with col_info3:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-value">5</span>
            <span class="stat-label">Metrics Scored</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Mock Interview", use_container_width=False):
        with st.spinner("Alex is preparing your interview..."):
            session = start_interview(profile, target_role)
            st.session_state.mock_session = session
            st.rerun()

elif mock_session.get("status") == "completed":
    # ── Results Screen ────────────────────────────────────────────────────────────
    evaluation = st.session_state.get("mock_evaluation")

    if not evaluation:
        with st.spinner("Generating your performance report..."):
            evaluation = evaluate_interview(mock_session, profile)
            st.session_state.mock_evaluation = evaluation

    if evaluation:
        overall = evaluation.get("overall_score", 0)
        recommendation = evaluation.get("hiring_recommendation", "Maybe")

        rec_colors = {
            "Strong Yes": "#22c55e", "Yes": "#3b82f6",
            "Maybe": "#f97316", "No": "#ef4444"
        }
        rec_color = rec_colors.get(recommendation, "#8b5cf6")

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(22,22,31,0.95),rgba(26,16,40,0.95));
             border:1px solid rgba(139,92,246,0.25);border-radius:20px;
             padding:2.5rem;text-align:center;margin-bottom:2rem;">
            <div style="font-size:1rem;color:#9898b0;text-transform:uppercase;letter-spacing:0.1em;
                 margin-bottom:0.5rem;">Interview Complete</div>
            <div style="font-size:4rem;font-weight:900;background:linear-gradient(135deg,#8b5cf6,#3b82f6);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 background-clip:text;">{overall:.0f}/100</div>
            <div style="font-size:1.1rem;color:#f0f0f5;margin-top:0.5rem;">
                {evaluation.get('overall_feedback','Great performance!')}
            </div>
            <div style="margin-top:1rem;">
                <span style="background:{rec_color}22;color:{rec_color};
                     border:1px solid {rec_color}44;padding:0.4rem 1.2rem;
                     border-radius:999px;font-weight:700;font-size:0.9rem;">
                    Recommendation: {recommendation}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_radar, col_details = st.columns([2, 3])

        with col_radar:
            scores = evaluation.get("scores", {})
            st.plotly_chart(
                interview_performance_radar(scores),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with col_details:
            tab_scores, tab_strengths, tab_improve, tab_next = st.tabs([
                "📊 Scores", "💪 Strengths", "📈 Improve", "➡️ Next Steps"
            ])

            with tab_scores:
                for metric, data in scores.items():
                    s = data.get("score", 0) if isinstance(data, dict) else data
                    fb = data.get("feedback", "") if isinstance(data, dict) else ""
                    bar_color = "#22c55e" if s >= 75 else ("#3b82f6" if s >= 55 else "#ef4444")
                    st.markdown(f"""
                    <div style="margin-bottom:0.75rem;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;">
                            <span style="color:#f0f0f5;font-weight:600;font-size:0.875rem;">
                                {metric.replace('_',' ').title()}
                            </span>
                            <span style="color:{bar_color};font-weight:700;">{s:.0f}/100</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width:{s}%;background:{bar_color};"></div>
                        </div>
                        <div style="color:#9898b0;font-size:0.78rem;margin-top:0.2rem;">{fb}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with tab_strengths:
                for s in evaluation.get("strengths", []):
                    st.markdown(f'<div class="alert-success">💪 {s}</div><br>', unsafe_allow_html=True)
                moments = evaluation.get("standout_moments", [])
                if moments:
                    st.markdown("**Standout Moments:**")
                    for m in moments:
                        st.markdown(f"⭐ {m}")

            with tab_improve:
                for area in evaluation.get("areas_for_improvement", []):
                    st.markdown(f'<div class="alert-warning">📈 {area}</div><br>', unsafe_allow_html=True)

            with tab_next:
                for step in evaluation.get("next_steps", []):
                    st.markdown(f"""
                    <div class="question-card" style="margin-bottom:0.5rem;">
                        <div style="color:#f0f0f5;font-size:0.875rem;">➡️ {step}</div>
                    </div>
                    """, unsafe_allow_html=True)

    if st.button("🔄 Start New Interview"):
        st.session_state.mock_session = None
        st.session_state.mock_evaluation = None
        st.rerun()

else:
    # ── Active Interview ──────────────────────────────────────────────────────────
    messages = mock_session.get("messages", [])
    question_count = mock_session.get("question_count", 0)
    max_questions = mock_session.get("max_questions", 15)
    progress_pct = (question_count / max_questions) * 100

    # Progress bar
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
            <span style="color:#9898b0;font-size:0.8rem;">Interview Progress</span>
            <span style="color:#a78bfa;font-size:0.8rem;font-weight:700;">
                Question {question_count}/{max_questions}
            </span>
        </div>
        <div class="progress-bar-container" style="height:6px;">
            <div class="progress-bar-fill" style="width:{progress_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat window
    chat_container = st.container()
    with chat_container:
        for msg in messages:
            is_ai = msg["role"] == "assistant"
            if is_ai:
                st.markdown(f"""
                <div style="display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:1rem;">
                    <div style="background:linear-gradient(135deg,#8b5cf6,#3b82f6);width:36px;height:36px;
                         border-radius:50%;display:flex;align-items:center;justify-content:center;
                         color:white;font-size:0.9rem;flex-shrink:0;font-weight:700;">A</div>
                    <div style="background:rgba(22,22,31,0.8);border:1px solid rgba(255,255,255,0.06);
                         border-radius:12px;border-top-left-radius:4px;padding:0.875rem 1rem;
                         max-width:85%;font-size:0.9rem;color:#f0f0f5;line-height:1.6;">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;gap:0.75rem;align-items:flex-start;margin-bottom:1rem;justify-content:flex-end;">
                    <div style="background:linear-gradient(135deg,#8b5cf6,#3b82f6);
                         border-radius:12px;border-top-right-radius:4px;padding:0.875rem 1rem;
                         max-width:75%;font-size:0.9rem;color:white;line-height:1.6;">
                        {msg['content']}
                    </div>
                    <div style="background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);
                         width:36px;height:36px;border-radius:50%;display:flex;align-items:center;
                         justify-content:center;color:#a78bfa;font-size:0.9rem;flex-shrink:0;font-weight:700;">
                        U
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Input area
    if mock_session.get("status") == "active":
        st.markdown("---")
        user_input = st.text_area(
            "Your Response",
            placeholder="Type your answer here... Be specific, use examples from your experience.",
            height=120,
            label_visibility="collapsed",
            key="interview_input",
        )

        col_send, col_end = st.columns([3, 1])
        with col_send:
            if st.button("📤 Send Response", use_container_width=True):
                if user_input.strip():
                    with st.spinner("Alex is responding..."):
                        updated = process_response(mock_session, user_input.strip(), profile)
                        st.session_state.mock_session = updated
                        st.rerun()
                else:
                    st.warning("Please type a response first.")

        with col_end:
            if st.button("🏁 End Interview", use_container_width=True):
                mock_session["status"] = "completed"
                st.session_state.mock_session = mock_session
                st.rerun()
