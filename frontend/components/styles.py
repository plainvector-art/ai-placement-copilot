"""
Premium CSS styling system for AI Interview & Placement Copilot.
Inspired by Linear, Vercel, and Notion — dark mode first, glassmorphism.
"""

GLOBAL_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════════════════
   IMPORTS & RESET (Heritage Intelligence Theme)
   ═══════════════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #121212;
    --bg-secondary: #0e0e0e;
    --bg-card: rgba(27, 48, 34, 0.25); /* Smoked Emerald Glass */
    --bg-card-hover: rgba(27, 48, 34, 0.4);
    --bg-glass: rgba(14, 14, 14, 0.6);
    --border: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(233, 193, 118, 0.2); /* Burnished Gold Stroke Hint */
    --text-primary: #e5e2e1;
    --text-secondary: #c3c8c1;
    --text-muted: #8d928c;
    --accent-sage: #b4cdb8; /* Sage Green */
    --accent-gold: #e9c176; /* Burnished Gold */
    --accent-emerald: #1b3022; /* Forest Emerald */
    --accent-burgundy: #7a322f; /* Burgundy / Error Accent */
    --gradient-1: linear-gradient(135deg, #1b3022 0%, #e9c176 100%);
    --gradient-2: linear-gradient(135deg, #e9c176 0%, #b4cdb8 100%);
    --gradient-3: linear-gradient(135deg, #1b3022 0%, #121212 100%);
    --gradient-hero: radial-gradient(circle at top left, #1b3022 0%, #121212 50%, #0e0e0e 100%);
    --shadow-sm: 0 4px 12px rgba(0,0,0,0.3);
    --shadow-md: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    --shadow-lg: 0 20px 40px rgba(0, 0, 0, 0.6);
    --shadow-glow: 0 0 25px rgba(233, 193, 118, 0.15);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
}

/* ── Base App Layout ──────────────────────────────────────────────────────── */
* { box-sizing: border-box; }

.stApp {
    background: radial-gradient(at 0% 0%, #121212 0%, transparent 60%),
                radial-gradient(at 100% 0%, #1b3022 0%, transparent 60%),
                radial-gradient(at 100% 100%, #0e0e0e 0%, transparent 60%),
                radial-gradient(at 0% 100%, #121212 0%, transparent 60%) !important;
    background-color: #121212 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
}

/* Hide Streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* Main content area spacing */
.main .block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 1300px !important;
}

/* ── Sidebar Redesign ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0e0e0e !important;
    border-right: 1px solid rgba(233, 193, 118, 0.1) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
}

[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.5rem !important;
}

/* Style native Streamlit expand/collapse icons */
[data-testid="collapsedControl"] button,
button[data-testid="stSidebarCollapseButton"] {
    color: var(--accent-gold) !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="collapsedControl"] button svg,
button[data-testid="stSidebarCollapseButton"] svg {
    fill: var(--accent-gold) !important;
    color: var(--accent-gold) !important;
}
[data-testid="collapsedControl"] button:hover,
button[data-testid="stSidebarCollapseButton"]:hover {
    background-color: rgba(233, 193, 118, 0.1) !important;
    box-shadow: 0 0 15px rgba(233, 193, 118, 0.2) !important;
}

/* ── Typography ───────────────────────────────────────────────────────────── */
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

/* Exclude Material Symbols from generic font overrides */
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp {
    font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Symbols Sharp' !important;
}

/* ── Tactile Buttons ──────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent-gold) !important;
    color: var(--accent-emerald) !important;
    border: 1px solid rgba(233, 193, 118, 0.3) !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.75rem !important;
    cursor: pointer !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    box-shadow: var(--shadow-sm) !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 10px 25px -5px rgba(233, 193, 118, 0.35) !important;
    opacity: 0.95 !important;
}

.stButton > button:active {
    transform: scale(0.96) !important;
}

/* Secondary button variant */
.stButton > button[kind="secondary"] {
    background: rgba(27, 48, 34, 0.25) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    box-shadow: none !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(27, 48, 34, 0.4) !important;
    border-color: rgba(233, 193, 118, 0.2) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Smoked Inputs ────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: rgba(14, 14, 14, 0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-gold) !important;
    box-shadow: 0 0 0 3px rgba(233, 193, 118, 0.15) !important;
    outline: none !important;
}

/* ── File Uploader ────────────────────────────────────────────────────────── */
.stFileUploader > div {
    background: rgba(27, 48, 34, 0.15) !important;
    border: 2px dashed rgba(233, 193, 118, 0.2) !important;
    border-radius: var(--radius-lg) !important;
    transition: all 0.3s ease !important;
}

.stFileUploader > div:hover {
    border-color: var(--accent-gold) !important;
    background: rgba(27, 48, 34, 0.3) !important;
}

/* ── Select Box ───────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: rgba(14, 14, 14, 0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ── Progress/Sliders ──────────────────────────────────────────────────────── */
.stProgress > div > div > div {
    background: var(--gradient-1) !important;
    border-radius: 4px !important;
}

.stSlider > div > div {
    color: var(--accent-gold) !important;
}

/* ── Metrics ──────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.25rem !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow-md) !important;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(233, 193, 118, 0.2) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-glow) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-gold) !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
}

/* ── Expanders ────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: rgba(27, 48, 34, 0.2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

.streamlit-expanderContent {
    background: rgba(14, 14, 14, 0.4) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(14, 14, 14, 0.6) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
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
    background: rgba(27, 48, 34, 0.5) !important;
    color: var(--accent-gold) !important;
    border: 1px solid rgba(233, 193, 118, 0.2) !important;
}

/* ── Dividers ─────────────────────────────────────────────────────────────── */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Plotly Charts Container ─────────────────────────────────────────────── */
.js-plotly-plot {
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}

/* ── Scrollbars ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(233, 193, 118, 0.15); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-gold); }

/* ── Spinner ──────────────────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--accent-gold) !important;
}

/* ══════════════════════════════════════════════════════════════════════════════
   CUSTOM GLASSMORPHIC COMPONENTS
   ══════════════════════════════════════════════════════════════════════════════ */

/* ── Hero Section (Mesh Background) ────────────────────────────────────────── */
.hero-section {
    background: radial-gradient(at 0% 0%, #121212 0%, transparent 60%),
                radial-gradient(at 100% 0%, #1b3022 0%, transparent 60%),
                radial-gradient(at 100% 100%, #0e0e0e 0%, transparent 60%),
                radial-gradient(at 0% 100%, #121212 0%, transparent 60%) !important;
    background-color: #121212 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: var(--radius-xl) !important;
    padding: 3rem 2.5rem;
    margin-bottom: 2.25rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-md) !important;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(233, 193, 118, 0.03) 0%, transparent 60%);
    pointer-events: none;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--text-primary) !important;
    background: var(--gradient-2);
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

/* ── Smoked Glass Cards ───────────────────────────────────────────────────── */
.card {
    background: var(--bg-card);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-md);
}

.card:hover {
    border-color: rgba(233, 193, 118, 0.2);
    transform: translateY(-3px);
    background: var(--bg-card-hover);
    box-shadow: var(--shadow-lg);
}

.card-glass {
    background: var(--bg-card);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
}

/* ── Score Badges (Elite / Standard styling) ─────────────────────────────── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.score-excellent { background: rgba(180, 205, 184, 0.15); color: #b4cdb8; border: 1px solid rgba(180, 205, 184, 0.3); }
.score-good { background: rgba(233, 193, 118, 0.15); color: #e9c176; border: 1px solid rgba(233, 193, 118, 0.3); }
.score-fair { background: rgba(233, 193, 118, 0.08); color: #b18d48; border: 1px solid rgba(233, 193, 118, 0.2); }
.score-poor { background: rgba(122, 50, 47, 0.15); color: #ff9e97; border: 1px solid rgba(122, 50, 47, 0.3); }

/* ── Skill Tags ───────────────────────────────────────────────────────────── */
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
    background: rgba(180, 205, 184, 0.12);
    color: #b4cdb8;
    border: 1px solid rgba(180, 205, 184, 0.25);
}

.skill-tag-missing {
    background: rgba(122, 50, 47, 0.12);
    color: #ff9e97;
    border: 1px solid rgba(122, 50, 47, 0.25);
}

.skill-tag-neutral {
    background: rgba(233, 193, 118, 0.08);
    color: #e9c176;
    border: 1px solid rgba(233, 193, 118, 0.2);
}

/* ── Section Header ───────────────────────────────────────────────────────── */
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
    color: #1b3022;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.01em;
}

/* ── Progress Bar ─────────────────────────────────────────────────────────── */
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

/* ── Stats Grid ───────────────────────────────────────────────────────────── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.stat-item {
    background: rgba(14, 14, 14, 0.4);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem 1rem;
    text-align: center;
    transition: all 0.25s ease;
}

.stat-item:hover {
    border-color: var(--accent-gold);
    box-shadow: 0 0 20px rgba(233, 193, 118, 0.1);
    transform: translateY(-2px);
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    background: var(--gradient-2);
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

/* ── Conversation Simulator ──────────────────────────────────────────────── */
.chat-container {
    background: rgba(14, 14, 14, 0.4);
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
    color: #1b3022;
}

.chat-avatar.user {
    background: rgba(233, 193, 118, 0.15);
    border: 1px solid rgba(233, 193, 118, 0.3);
    color: var(--accent-gold);
}

.chat-bubble {
    max-width: 80%;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    line-height: 1.6;
}

.chat-bubble.ai {
    background: rgba(27, 48, 34, 0.25);
    border: 1px solid var(--border);
    color: var(--text-primary);
    border-top-left-radius: 4px;
}

.chat-bubble.user {
    background: var(--accent-gold);
    color: #1b3022;
    border-top-right-radius: 4px;
    font-weight: 500;
}

/* ── Question Modules ─────────────────────────────────────────────────────── */
.question-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    border-left: 3px solid var(--accent-gold);
    transition: all 0.2s;
}

.question-card:hover {
    border-color: rgba(233, 193, 118, 0.2);
    border-left-color: var(--accent-gold);
    transform: translateX(4px);
    box-shadow: var(--shadow-sm);
}

.question-card.hr { border-left-color: var(--accent-sage); }
.question-card.technical { border-left-color: var(--accent-gold); }
.question-card.project { border-left-color: rgba(233, 193, 118, 0.6); }
.question-card.behavioral { border-left-color: var(--accent-burgundy); }

/* ── Roadmap Timelines ────────────────────────────────────────────────────── */
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
    color: #1b3022;
    weight: bold;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(233, 193, 118, 0.25);
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
    border-color: var(--accent-gold);
}

/* ── Smart Recommenders ───────────────────────────────────────────────────── */
.rec-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, rgba(233, 193, 118, 0.05) 100%);
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
    border-color: rgba(233, 193, 118, 0.3);
    transform: translateY(-3px);
    box-shadow: var(--shadow-glow);
}

/* ── Contextual Alerts ────────────────────────────────────────────────────── */
.alert-info {
    background: rgba(180, 205, 184, 0.08);
    border: 1px solid rgba(180, 205, 184, 0.2);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    color: #b4cdb8;
    font-size: 0.875rem;
}

.alert-success {
    background: rgba(180, 205, 184, 0.12);
    border: 1px solid rgba(180, 205, 184, 0.3);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    color: #b4cdb8;
    font-size: 0.875rem;
}

.alert-warning {
    background: rgba(122, 50, 47, 0.1);
    border: 1px solid rgba(122, 50, 47, 0.2);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    color: #ff9e97;
    font-size: 0.875rem;
}

/* ── Gradient Typography ──────────────────────────────────────────────────── */
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

/* ── Bento & Redesign Integration Classes ─────────────────────────────────── */
.glass-module {
    background: rgba(27, 48, 34, 0.3) !important; /* deep emerald tint */
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(233, 193, 118, 0.1) !important; /* gold stroke hint */
}

.breathing-button {
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 0 0 rgba(233, 193, 118, 0);
}
.breathing-button:hover {
    transform: scale(1.02);
    box-shadow: 0 10px 25px -5px rgba(233, 193, 118, 0.3);
}
.breathing-button:active {
    transform: scale(0.96);
}

.bento-card {
    opacity: 0;
    transform: translateY(20px);
    animation: fadeInCard 0.8s forwards cubic-bezier(0.22, 1, 0.36, 1);
}
@keyframes fadeInCard {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.circular-gauge {
    transition: stroke-dashoffset 2s ease-in-out;
    filter: drop-shadow(0 0 8px rgba(233, 193, 118, 0.4));
}
.animate-delay-1 { animation-delay: 0.1s; }
.animate-delay-2 { animation-delay: 0.2s; }
.animate-delay-3 { animation-delay: 0.3s; }
.animate-delay-4 { animation-delay: 0.4s; }
.animate-delay-5 { animation-delay: 0.5s; }

.rec-card {
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
