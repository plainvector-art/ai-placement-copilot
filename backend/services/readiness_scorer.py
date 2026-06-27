"""
Placement Readiness Score Calculator.
Composite score from resume, skills, projects, and interview readiness.
"""
from typing import Dict, Optional
from loguru import logger


# ── Component Weights ─────────────────────────────────────────────────────────
COMPONENT_WEIGHTS = {
    "resume_score": 0.25,
    "skills_coverage": 0.35,
    "projects_score": 0.20,
    "interview_readiness": 0.20,
}

# ── Readiness Levels ──────────────────────────────────────────────────────────
READINESS_LEVELS = [
    (0, 40, "Beginner", "#ef4444", "🌱",
     "You're just getting started! Focus on building core skills and completing 2-3 strong projects."),
    (40, 60, "Developing", "#f97316", "📈",
     "Good progress! Fill the key skill gaps and strengthen your project portfolio."),
    (60, 80, "Placement Ready", "#22c55e", "🎯",
     "You're ready for placements! Polish your resume and practice interviews."),
    (80, 101, "Highly Competitive", "#8b5cf6", "🚀",
     "Excellent profile! You're highly competitive. Target top-tier companies."),
]


def calculate_interview_readiness(profile: Dict) -> float:
    """
    Estimate interview readiness from resume signals.
    Returns 0-100 score.
    """
    score = 0.0

    # Projects with descriptions
    projects = profile.get("projects", [])
    if len(projects) >= 3:
        score += 30
    elif len(projects) >= 2:
        score += 20
    elif len(projects) >= 1:
        score += 10

    # Quantified experience
    raw_text = profile.get("raw_text", "").lower()
    import re
    quantified = len(re.findall(r'\d+%|\$\d+|\d+x\b|\d+\+', raw_text))
    if quantified >= 5:
        score += 30
    elif quantified >= 3:
        score += 20
    elif quantified >= 1:
        score += 10

    # Certifications
    certs = profile.get("certifications", [])
    if certs:
        score += min(len(certs) * 10, 20)

    # GitHub/Portfolio
    if profile.get("github"):
        score += 10
    if profile.get("linkedin"):
        score += 10

    return min(score, 100)


def calculate_projects_score(profile: Dict) -> float:
    """Score projects for placement readiness. Returns 0-100."""
    projects = profile.get("projects", [])

    if not projects:
        return 0

    score = 0.0
    count = len(projects)

    # Quantity
    if count >= 4:
        score += 40
    elif count >= 3:
        score += 30
    elif count >= 2:
        score += 20
    else:
        score += 10

    # Quality indicators
    for proj in projects:
        if proj.get("technologies"):
            score += 5
        if proj.get("description") and len(str(proj.get("description", ""))) > 50:
            score += 5

    return min(score, 100)


def calculate_readiness_score(
    ats_score: float,
    skill_gap_data: Dict,
    profile: Dict,
    interview_score: Optional[float] = None,
) -> Dict:
    """
    Calculate overall placement readiness score.

    Args:
        ats_score: ATS score (0-100) from ats_scorer
        skill_gap_data: Skill gap analysis result
        profile: Parsed candidate profile
        interview_score: Optional actual mock interview score

    Returns:
        Comprehensive readiness report
    """
    logger.info("Calculating placement readiness score...")

    # Normalize ATS score to 0-100
    resume_component = min(ats_score, 100)

    # Skills component from coverage
    skills_coverage = skill_gap_data.get("coverage", {}).get("overall", 0)
    skills_component = skills_coverage

    # Projects component
    projects_component = calculate_projects_score(profile)

    # Interview readiness
    if interview_score is not None:
        interview_component = min(interview_score, 100)
    else:
        interview_component = calculate_interview_readiness(profile)

    # Weighted overall score
    overall_score = (
        resume_component * COMPONENT_WEIGHTS["resume_score"] +
        skills_component * COMPONENT_WEIGHTS["skills_coverage"] +
        projects_component * COMPONENT_WEIGHTS["projects_score"] +
        interview_component * COMPONENT_WEIGHTS["interview_readiness"]
    )
    overall_score = round(min(overall_score, 100), 1)

    # Determine readiness level
    level_info = _get_readiness_level(overall_score)

    # Generate component breakdown
    components = {
        "Resume Quality": {
            "score": round(resume_component, 1),
            "weight": "25%",
            "weighted": round(resume_component * 0.25, 1),
            "status": _score_status(resume_component),
        },
        "Skills Coverage": {
            "score": round(skills_component, 1),
            "weight": "35%",
            "weighted": round(skills_component * 0.35, 1),
            "status": _score_status(skills_component),
        },
        "Projects Portfolio": {
            "score": round(projects_component, 1),
            "weight": "20%",
            "weighted": round(projects_component * 0.20, 1),
            "status": _score_status(projects_component),
        },
        "Interview Readiness": {
            "score": round(interview_component, 1),
            "weight": "20%",
            "weighted": round(interview_component * 0.20, 1),
            "status": _score_status(interview_component),
        },
    }

    # Improvement recommendations
    recommendations = _generate_recommendations(
        resume_component, skills_component, projects_component, interview_component,
        skill_gap_data, profile
    )

    return {
        "overall_score": overall_score,
        "level": level_info["level"],
        "level_color": level_info["color"],
        "level_emoji": level_info["emoji"],
        "level_message": level_info["message"],
        "components": components,
        "raw_scores": {
            "resume": round(resume_component, 1),
            "skills": round(skills_component, 1),
            "projects": round(projects_component, 1),
            "interview": round(interview_component, 1),
        },
        "recommendations": recommendations,
        "next_milestone": _get_next_milestone(overall_score),
    }


def _get_readiness_level(score: float) -> Dict:
    for min_s, max_s, level, color, emoji, message in READINESS_LEVELS:
        if min_s <= score < max_s:
            return {"level": level, "color": color, "emoji": emoji, "message": message}
    return {"level": "Highly Competitive", "color": "#8b5cf6", "emoji": "🚀",
            "message": "Excellent profile!"}


def _score_status(score: float) -> str:
    if score >= 75:
        return "Strong"
    elif score >= 50:
        return "Good"
    elif score >= 30:
        return "Needs Work"
    else:
        return "Critical"


def _get_next_milestone(score: float) -> Dict:
    """Return what the next score milestone is."""
    for min_s, max_s, level, color, _, message in READINESS_LEVELS:
        if score < min_s:
            return {
                "level": level,
                "target": min_s,
                "gap": round(min_s - score, 1),
                "color": color,
            }
        elif min_s <= score < max_s:
            if max_s < 101:
                next_idx = READINESS_LEVELS.index((min_s, max_s, level, color, _, message)) + 1
                if next_idx < len(READINESS_LEVELS):
                    nm = READINESS_LEVELS[next_idx]
                    return {
                        "level": nm[2],
                        "target": nm[0],
                        "gap": round(nm[0] - score, 1),
                        "color": nm[3],
                    }
    return {"level": "Peak Performance", "target": 100, "gap": round(100 - score, 1), "color": "#8b5cf6"}


def _generate_recommendations(
    resume: float, skills: float, projects: float, interview: float,
    skill_gap: Dict, profile: Dict
) -> List[str]:
    """Generate prioritized improvement recommendations."""
    recs = []

    # Find lowest scoring component
    components = {"Resume": resume, "Skills": skills, "Projects": projects, "Interview": interview}
    lowest = min(components, key=components.get)

    if lowest == "Resume" or resume < 50:
        recs.append("🔹 Improve your resume: Quantify achievements, add action verbs, and ensure all sections are present")

    if lowest == "Skills" or skills < 50:
        priority = skill_gap.get("priority_skills", [])
        if priority:
            top = priority[0]["skill"] if priority else "core skills"
            recs.append(f"🔹 Learn {top} and other priority skills for your target role")
        recs.append("🔹 Focus on the top 3-5 missing required skills from the skill gap analysis")

    if lowest == "Projects" or projects < 50:
        recs.append("🔹 Build 2-3 portfolio projects using your target role's core technologies")
        recs.append("🔹 Deploy projects on GitHub with detailed README files")

    if lowest == "Interview" or interview < 50:
        recs.append("🔹 Practice the Mock Interview feature daily for 2 weeks")
        recs.append("🔹 Prepare STAR-format answers for behavioral questions")

    # Generic recommendations
    if not profile.get("linkedin"):
        recs.append("🔹 Create/optimize your LinkedIn profile with the generated headline")
    if not profile.get("github"):
        recs.append("🔹 Create a GitHub profile and push your projects")
    if not profile.get("certifications"):
        recs.append("🔹 Earn at least one industry certification to boost credibility")

    return recs[:6]
