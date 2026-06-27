"""
Premium CSS styling system for AI Interview & Placement Copilot.
Inspired by Linear, Vercel, and Notion — dark mode first, glassmorphism.
"""

GLOBAL_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════════════════
   IMPORTS & RESET
═══════════════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #111118;
    --bg-card: #16161f;
    --bg-card-hover: #1e1e2a;
    --bg-glass: rgba(22, 22, 31, 0.8);
    --border: rgba(255, 255, 255, 0.06);
    --border-hover: rgba(255, 255, 255, 0.12);
    --text-primary: #f0f0f5;
    --text-secondary: #9898b0;
    --text-muted: #5a5a72;
    --accent-purple: #8b5cf6;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-green: #22c55e;
    --accent-orange: #f97316;
    --accent-red: #ef4444;
    --accent-pink: #ec4899;
    --gradient-1: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
    --gradient-2: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
    --gradient-3: linear-gradient(135deg, #22c55e 0%, #06b6d4 100%);
    --gradient-hero: linear-gradient(135deg, #0a0a0f 0%, #1a1028 50%, #0a0a0f 100%);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 24px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 48px rgba(0,0,0,0.5);
    --shadow-glow: 0 0 40px rgba(139, 92, 246, 0.15);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
}

/* ── Base ──────────────────────────────────────────────────────────────────── */
* { box-sizing: border-box; }

.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
}

/* Hide Streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* Main content area */
.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1200px !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ── Typography ─────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
}

p, li, label, .stMarkdown {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
}

/* ── Buttons ────────────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--gradient-1) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.5rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.3) !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.5) !important;
    opacity: 0.95 !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Secondary button variant */
.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    box-shadow: none !important;
}

/* ── Inputs ─────────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    outline: none !important;
}

/* ── File Uploader ───────────────────────────────────────────────────────────── */
.stFileUploader > div {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius-lg) !important;
    transition: all 0.3s ease !important;
}

.stFileUploader > div:hover {
    border-color: var(--accent-purple) !important;
    background: rgba(139, 92, 246, 0.05) !important;
}

/* ── Select Box ──────────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ── Progress/Slider ─────────────────────────────────────────────────────────── */
.stProgress > div > div > div {
    background: var(--gradient-1) !important;
    border-radius: 4px !important;
}

.stSlider > div > div {
    color: var(--accent-purple) !important;
}

/* ── Metrics ────────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.25rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--accent-purple) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-glow) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
}

/* ── Expanders ──────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

.streamlit-expanderContent {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: calc(var(--radius-md) - 4px) !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    background: var(--gradient-1) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.4) !important;
}

/* ── Dividers ───────────────────────────────────────────────────────────────── */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Plotly Charts ───────────────────────────────────────────────────────────── */
.js-plotly-plot {
    border-radius: var(--radius-lg) !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-hover); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-purple); }

/* ── Spinner ────────────────────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--accent-purple) !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
══════════════════════════════════════════════════════════════════════════════ */

/* ── Hero Section ────────────────────────────────────────────────────────────── */
.hero-section {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1028 40%, #0f1a28 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.08) 0%, transparent 60%);
    pointer-events: none;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin: 0;
    font-weight: 400;
}

/* ── Premium Cards ───────────────────────────────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.card-glass {
    background: var(--bg-glass);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
}

/* ── Score Badge ─────────────────────────────────────────────────────────────── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.score-excellent { background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); }
.score-good { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
.score-fair { background: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3); }
.score-poor { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }

/* ── Skill Tags ──────────────────────────────────────────────────────────────── */
.skill-tag {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 2px;
    transition: all 0.2s;
}

.skill-tag-have {
    background: rgba(34, 197, 94, 0.12);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.25);
}

.skill-tag-missing {
    background: rgba(239, 68, 68, 0.12);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.25);
}

.skill-tag-neutral {
    background: rgba(139, 92, 246, 0.12);
    color: #a78bfa;
    border: 1px solid rgba(139, 92, 246, 0.25);
}

/* ── Section Header ──────────────────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}

.section-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    background: var(--gradient-1);
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.01em;
}

/* ── Progress Bar ────────────────────────────────────────────────────────────── */
.progress-bar-container {
    width: 100%;
    height: 8px;
    background: rgba(255,255,255,0.05);
    border-radius: 999px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--gradient-1);
    transition: width 1s ease;
}

/* ── Stats Grid ──────────────────────────────────────────────────────────────── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.stat-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem;
    text-align: center;
    transition: all 0.2s;
}

.stat-item:hover {
    border-color: var(--accent-purple);
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.1);
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block;
}

.stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

/* ── Chat Interface ──────────────────────────────────────────────────────────── */
.chat-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    max-height: 600px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.chat-message {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.chat-message.user { flex-direction: row-reverse; }

.chat-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    font-weight: 700;
}

.chat-avatar.ai {
    background: var(--gradient-1);
    color: white;
}

.chat-avatar.user {
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #a78bfa;
}

.chat-bubble {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    line-height: 1.6;
}

.chat-bubble.ai {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    color: var(--text-primary);
    border-top-left-radius: 4px;
}

.chat-bubble.user {
    background: var(--gradient-1);
    color: white;
    border-top-right-radius: 4px;
}

/* ── Question Cards ──────────────────────────────────────────────────────────── */
.question-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    border-left: 3px solid var(--accent-purple);
    transition: all 0.2s;
}

.question-card:hover {
    border-color: var(--border-hover);
    border-left-color: var(--accent-purple);
    transform: translateX(4px);
    box-shadow: var(--shadow-sm);
}

.question-card.hr { border-left-color: var(--accent-blue); }
.question-card.technical { border-left-color: var(--accent-purple); }
.question-card.project { border-left-color: var(--accent-cyan); }
.question-card.behavioral { border-left-color: var(--accent-orange); }

/* ── Roadmap Timeline ────────────────────────────────────────────────────────── */
.timeline-item {
    display: flex;
    gap: 1rem;
    padding: 1rem 0;
    position: relative;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: 17px;
    top: 50px;
    width: 2px;
    height: calc(100% - 30px);
    background: var(--border);
}

.timeline-item:last-child::before { display: none; }

.timeline-dot {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--gradient-1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
    z-index: 1;
}

.timeline-content {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    flex: 1;
    transition: all 0.2s;
}

.timeline-content:hover {
    border-color: var(--accent-purple);
}

/* ── Recommendation Card ─────────────────────────────────────────────────────── */
.rec-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, rgba(139, 92, 246, 0.05) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}

.rec-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gradient-1);
    opacity: 0;
    transition: opacity 0.2s;
}

.rec-card:hover::after { opacity: 1; }
.rec-card:hover {
    border-color: rgba(139, 92, 246, 0.3);
    transform: translateY(-3px);
    box-shadow: var(--shadow-glow);
}

/* ── Alert Styles ────────────────────────────────────────────────────────────── */
.alert-info {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    color: #93c5fd;
    font-size: 0.875rem;
}

.alert-success {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    color: #86efac;
    font-size: 0.875rem;
}

.alert-warning {
    background: rgba(249, 115, 22, 0.1);
    border: 1px solid rgba(249, 115, 22, 0.2);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    color: #fdba74;
    font-size: 0.875rem;
}

/* ── Loading Skeleton ────────────────────────────────────────────────────────── */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.skeleton {
    background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
    border-radius: var(--radius-sm);
}

/* ── Gradient Text ───────────────────────────────────────────────────────────── */
.gradient-text {
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gradient-text-2 {
    background: var(--gradient-2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Animated gradient border ────────────────────────────────────────────────── */
@keyframes border-rotate {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.animated-border {
    background: linear-gradient(270deg, #8b5cf6, #3b82f6, #06b6d4, #8b5cf6);
    background-size: 300% 300%;
    animation: border-rotate 4s ease infinite;
    padding: 1px;
    border-radius: var(--radius-lg);
}

.animated-border-inner {
    background: var(--bg-card);
    border-radius: calc(var(--radius-lg) - 1px);
    padding: 1.5rem;
}

/* ── Sidebar Nav Styles ──────────────────────────────────────────────────────── */
.sidebar-logo {
    font-size: 1.1rem;
    font-weight: 800;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

.sidebar-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    padding: 0.5rem 0;
    margin-top: 1rem;
}

/* ── Responsive ─────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
    }
    .hero-title { font-size: 1.8rem; }
}

/* ── Animations ──────────────────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.2); }
    50% { box-shadow: 0 0 40px rgba(139, 92, 246, 0.4); }
}

.fade-in-up { animation: fadeInUp 0.5s ease forwards; }
.pulse-glow { animation: pulse-glow 3s ease infinite; }
</style>
"""


def inject_css():
    """Inject the global CSS into Streamlit."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def card(content: str, classes: str = "") -> str:
    """Wrap content in a premium card."""
    return f'<div class="card {classes}">{content}</div>'


def hero(title: str, subtitle: str, icon: str = "🎯") -> str:
    """Render hero section HTML."""
    return f"""
    <div class="hero-section">
        <div class="hero-title">{icon} {title}</div>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """


def skill_tag(skill: str, variant: str = "neutral") -> str:
    """Render a skill tag badge."""
    return f'<span class="skill-tag skill-tag-{variant}">{skill}</span>'


def score_badge(score: float, label: str = "") -> str:
    """Render a score badge with appropriate color."""
    if score >= 80:
        cls = "score-excellent"
        emoji = "✅"
    elif score >= 65:
        cls = "score-good"
        emoji = "🔵"
    elif score >= 50:
        cls = "score-fair"
        emoji = "⚠️"
    else:
        cls = "score-poor"
        emoji = "❌"
    return f'<span class="score-badge {cls}">{emoji} {score:.0f}{label}</span>'


def section_header(title: str, icon: str = "📊") -> str:
    """Render a styled section header."""
    return f"""
    <div class="section-header">
        <div class="section-icon">{icon}</div>
        <h3 class="section-title">{title}</h3>
    </div>
    """


def progress_bar(value: float, color: str = "#8b5cf6") -> str:
    """Render a styled progress bar."""
    return f"""
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: {value}%; background: {color};"></div>
    </div>
    """
