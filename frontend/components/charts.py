"""
Plotly chart builders for the analytics dashboard.
All charts use a consistent dark theme.
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import pandas as pd


# ── Theme ─────────────────────────────────────────────────────────────────────
DARK_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#c3c8c1"},
    "colorway": ["#e9c176", "#b4cdb8", "#819986", "#7a322f", "#ff9e97", "#5d4201"],
}

COLORS = {
    "purple": "#b4cdb8",  # Sage green
    "blue": "#819986",    # Sage Accent
    "cyan": "#e9c176",    # Burnished Gold
    "green": "#b4cdb8",   # Success Sage
    "orange": "#e9c176",  # Warning Gold
    "red": "#7a322f",     # Burgundy / Error
    "pink": "#ff9e97",
    "bg": "rgba(27, 48, 34, 0.25)",
    "border": "rgba(233, 193, 118, 0.1)",
}


def ats_gauge(score: float, title: str = "ATS Score") -> go.Figure:
    """Create an ATS score gauge chart."""
    if score >= 80:
        color = COLORS["green"]
    elif score >= 65:
        color = COLORS["blue"]
    elif score >= 50:
        color = COLORS["orange"]
    else:
        color = COLORS["red"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": title, "font": {"size": 16, "color": "#f0f0f5", "family": "Inter"}},
        delta={"reference": 70, "increasing": {"color": COLORS["green"]}, "decreasing": {"color": COLORS["red"]}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#5a5a72",
                "tickfont": {"color": "#5a5a72", "size": 10},
            },
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.08)"},
                {"range": [40, 65], "color": "rgba(249,115,22,0.08)"},
                {"range": [65, 80], "color": "rgba(59,130,246,0.08)"},
                {"range": [80, 100], "color": "rgba(34,197,94,0.08)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        },
        number={"suffix": "/100", "font": {"size": 32, "color": "#f0f0f5", "family": "Inter"}, "valueformat": ".1f"},
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=30, b=20),
        **DARK_THEME,
    )

    return fig


def readiness_gauge(score: float, level: str) -> go.Figure:
    """Create a placement readiness gauge."""
    colors_by_level = {
        "Beginner": COLORS["red"],
        "Developing": COLORS["orange"],
        "Placement Ready": COLORS["green"],
        "Highly Competitive": COLORS["purple"],
    }
    color = colors_by_level.get(level, COLORS["purple"])

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Placement Readiness", "font": {"size": 16, "color": "#f0f0f5"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#5a5a72", "size": 10}},
            "bar": {"color": color, "thickness": 0.8},
            "bgcolor": "rgba(255,255,255,0.02)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(239,68,68,0.1)", "name": "Beginner"},
                {"range": [40, 60], "color": "rgba(249,115,22,0.1)", "name": "Developing"},
                {"range": [60, 80], "color": "rgba(34,197,94,0.1)", "name": "Ready"},
                {"range": [80, 100], "color": "rgba(139,92,246,0.1)", "name": "Competitive"},
            ],
        },
        number={"suffix": "%", "font": {"size": 36, "color": "#f0f0f5"}, "valueformat": ".1f"},
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=30, b=20),
        **DARK_THEME,
    )

    return fig


def skill_radar(
    candidate_skills: List[str],
    required_skills: List[str],
    role: str,
) -> go.Figure:
    """Create a radar chart comparing candidate vs required skills."""
    # Use required skills as the dimensions
    categories = required_skills[:8]  # Max 8 for readability
    if not categories:
        return go.Figure()

    # Calculate match scores per dimension
    candidate_lower = {s.lower() for s in candidate_skills}

    candidate_scores = []
    for skill in categories:
        has_skill = any(
            skill.lower() in cs or cs in skill.lower()
            for cs in candidate_lower
        )
        candidate_scores.append(100 if has_skill else 15)

    required_scores = [100] * len(categories)

    # Close the radar loop
    categories_plot = categories + [categories[0]]
    candidate_plot = candidate_scores + [candidate_scores[0]]
    required_plot = required_scores + [required_scores[0]]

    fig = go.Figure()

    # Required skills (target)
    fig.add_trace(go.Scatterpolar(
        r=required_plot,
        theta=categories_plot,
        fill="toself",
        name="Required",
        line=dict(color=COLORS["purple"], width=2),
        fillcolor="rgba(139, 92, 246, 0.1)",
        marker=dict(size=6, color=COLORS["purple"]),
    ))

    # Candidate skills
    fig.add_trace(go.Scatterpolar(
        r=candidate_plot,
        theta=categories_plot,
        fill="toself",
        name="Your Profile",
        line=dict(color=COLORS["cyan"], width=2),
        fillcolor="rgba(6, 182, 212, 0.15)",
        marker=dict(size=6, color=COLORS["cyan"]),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#5a5a72", size=9),
                gridcolor="rgba(255,255,255,0.05)",
                linecolor="rgba(255,255,255,0.05)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#9898b0", size=10, family="Inter"),
                gridcolor="rgba(255,255,255,0.06)",
                linecolor="rgba(255,255,255,0.06)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(
            font=dict(color="#9898b0", family="Inter", size=11),
            bgcolor="rgba(22,22,31,0.8)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
        ),
        title=dict(
            text=f"Skills Radar — {role}",
            font=dict(color="#f0f0f5", size=14, family="Inter"),
        ),
        height=420,
        margin=dict(l=60, r=60, t=50, b=40),
        **DARK_THEME,
    )

    return fig


def ats_breakdown_bar(category_scores: Dict, weights: Dict) -> go.Figure:
    """Create a horizontal bar chart for ATS score breakdown."""
    categories = list(category_scores.keys())
    scores = list(category_scores.values())
    max_scores = [weights.get(cat, 25) for cat in categories]

    # Color based on performance
    colors = []
    for s, m in zip(scores, max_scores):
        pct = s / m * 100 if m > 0 else 0
        if pct >= 75:
            colors.append(COLORS["green"])
        elif pct >= 50:
            colors.append(COLORS["blue"])
        elif pct >= 30:
            colors.append(COLORS["orange"])
        else:
            colors.append(COLORS["red"])

    fig = go.Figure()

    # Background bars (max possible)
    fig.add_trace(go.Bar(
        y=[c.title() for c in categories],
        x=max_scores,
        orientation="h",
        marker=dict(color="rgba(255,255,255,0.04)", line=dict(color="rgba(255,255,255,0.06)", width=1)),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Actual scores
    fig.add_trace(go.Bar(
        y=[c.title() for c in categories],
        x=scores,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        text=[f"{s:.1f}/{m}" for s, m in zip(scores, max_scores)],
        textposition="outside",
        textfont=dict(color="#9898b0", size=11, family="Inter"),
        showlegend=False,
        name="Score",
    ))

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            range=[0, max(max_scores) + 3],
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color="#5a5a72", size=10),
        ),
        yaxis=dict(
            tickfont=dict(color="#9898b0", size=12, family="Inter"),
        ),
        height=320,
        margin=dict(l=20, r=80, t=20, b=20),
        **DARK_THEME,
    )

    return fig


def skill_coverage_bar(matched: List[str], missing: List[str]) -> go.Figure:
    """Create a stacked bar showing skill coverage."""
    total = len(matched) + len(missing)
    if total == 0:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Have ✓",
        x=["Skills Coverage"],
        y=[len(matched)],
        marker=dict(color=COLORS["green"], opacity=0.85),
        text=[f"{len(matched)} skills"],
        textposition="inside",
        textfont=dict(color="white", size=12, family="Inter", weight="bold"),
    ))

    fig.add_trace(go.Bar(
        name="Missing ✗",
        x=["Skills Coverage"],
        y=[len(missing)],
        marker=dict(color=COLORS["red"], opacity=0.7),
        text=[f"{len(missing)} missing"],
        textposition="inside",
        textfont=dict(color="white", size=12, family="Inter", weight="bold"),
    ))

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(font=dict(color="#9898b0", family="Inter"), bgcolor="rgba(0,0,0,0)"),
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(showgrid=False, showticklabels=False),
        xaxis=dict(showgrid=False),
        **DARK_THEME,
    )

    return fig


def readiness_components_bar(components: Dict) -> go.Figure:
    """Bar chart showing readiness score components."""
    names = list(components.keys())
    scores = [v["score"] for v in components.values()]
    weights = [v["weight"] for v in components.values()]

    bar_colors = []
    for s in scores:
        if s >= 75:
            bar_colors.append(COLORS["green"])
        elif s >= 50:
            bar_colors.append(COLORS["blue"])
        elif s >= 30:
            bar_colors.append(COLORS["orange"])
        else:
            bar_colors.append(COLORS["red"])

    fig = go.Figure(go.Bar(
        x=names,
        y=scores,
        marker=dict(
            color=bar_colors,
            line=dict(color="rgba(0,0,0,0)", width=0),
            cornerradius=6,
        ),
        text=[f"{s:.0f}%" for s in scores],
        textposition="outside",
        textfont=dict(color="#9898b0", size=11, family="Inter"),
        customdata=weights,
        hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}%<br>Weight: %{customdata}<extra></extra>",
    ))

    fig.update_layout(
        yaxis=dict(
            range=[0, 120],
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color="#5a5a72"),
        ),
        xaxis=dict(tickfont=dict(color="#9898b0", family="Inter")),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        **DARK_THEME,
    )

    return fig


def jd_match_gauge(score: float) -> go.Figure:
    """Job description match gauge."""
    return ats_gauge(score, title="JD Match Score")


def interview_performance_radar(scores: Dict) -> go.Figure:
    """Radar chart for interview performance scores."""
    categories = list(scores.keys())
    values = [v.get("score", 0) if isinstance(v, dict) else v for v in scores.values()]

    categories_plot = categories + [categories[0]]
    values_plot = values + [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_plot,
        theta=categories_plot,
        fill="toself",
        name="Performance",
        line=dict(color=COLORS["purple"], width=2),
        fillcolor="rgba(180, 205, 184, 0.25)",
        marker=dict(size=7, color=COLORS["purple"]),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#5a5a72", size=9),
                gridcolor="rgba(255,255,255,0.05)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#9898b0", size=11, family="Inter"),
                gridcolor="rgba(255,255,255,0.06)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        height=380,
        margin=dict(l=60, r=60, t=40, b=40),
        **DARK_THEME,
    )

    return fig


def roadmap_timeline(phases: Dict) -> go.Figure:
    """Gantt-style roadmap timeline chart."""
    rows = []
    colors_map = {
        "phase_1": COLORS["blue"],
        "phase_2": COLORS["purple"],
        "phase_3": COLORS["cyan"],
        "phase_4": COLORS["green"],
    }

    # Build timeline data
    month_map = {"phase_1": (0, 1), "phase_2": (1, 3), "phase_3": (3, 6), "phase_4": (3, 6)}

    for key, phase in phases.items():
        start, end = month_map.get(key, (0, 1))
        rows.append({
            "Phase": phase.get("name", key),
            "Start": start,
            "End": end,
            "Color": colors_map.get(key, COLORS["purple"]),
        })

    if not rows:
        return go.Figure()

    fig = go.Figure()

    for i, row in enumerate(rows):
        fig.add_trace(go.Bar(
            y=[row["Phase"]],
            x=[row["End"] - row["Start"]],
            base=[row["Start"]],
            orientation="h",
            marker=dict(color=row["Color"], opacity=0.8, line=dict(color="rgba(0,0,0,0)")),
            showlegend=False,
            hovertemplate=f"<b>{row['Phase']}</b><br>Month {row['Start']+1} - {row['End']}<extra></extra>",
        ))

    fig.update_layout(
        xaxis=dict(
            title="Month",
            range=[0, 7],
            tickvals=list(range(7)),
            ticktext=[f"M{i}" for i in range(7)],
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color="#5a5a72"),
        ),
        yaxis=dict(tickfont=dict(color="#9898b0", family="Inter")),
        barmode="overlay",
        height=250,
        margin=dict(l=20, r=20, t=20, b=30),
        **DARK_THEME,
    )

    return fig
