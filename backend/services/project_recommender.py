"""
Project Recommendation Engine.
Suggests projects based on role, skills, and experience level.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_json


def _load_projects_db() -> Dict:
    """Load projects database from JSON."""
    path = Path(__file__).parent.parent / "data" / "projects.json"
    with open(path, "r") as f:
        return json.load(f)["projects"]


def recommend_projects(
    profile: Dict,
    target_role: str,
    use_ai: bool = True,
) -> Dict:
    """
    Recommend projects based on candidate profile and target role.

    Returns:
        Curated list of project recommendations with rationale
    """
    skills = profile.get("skills", [])
    existing_projects = [p.get("title", "") for p in profile.get("projects", [])]
    experience_count = len(profile.get("experience", []))

    # Determine experience level
    level = _determine_level(skills, experience_count, profile.get("certifications", []))

    # Load static recommendations
    db_recs = _get_db_recommendations(target_role, level)

    # Use AI for enhanced, personalized recommendations
    if use_ai:
        ai_recs = _get_ai_recommendations(profile, target_role, level, existing_projects)
        if ai_recs:
            return {
                "target_role": target_role,
                "experience_level": level,
                "ai_recommendations": ai_recs.get("projects", []),
                "curated_recommendations": db_recs,
                "build_order": ai_recs.get("build_order", []),
                "portfolio_strategy": ai_recs.get("portfolio_strategy", ""),
                "github_tips": ai_recs.get("github_tips", []),
            }

    return {
        "target_role": target_role,
        "experience_level": level,
        "curated_recommendations": db_recs,
        "portfolio_strategy": _get_portfolio_strategy(target_role, level),
    }


def _determine_level(skills: List[str], exp_count: int, certs: List[str]) -> str:
    """Estimate experience level from profile signals."""
    score = 0
    score += len(skills) * 2
    score += exp_count * 10
    score += len(certs) * 5

    if score >= 50:
        return "advanced"
    elif score >= 25:
        return "intermediate"
    else:
        return "beginner"


def _get_db_recommendations(target_role: str, level: str) -> List[Dict]:
    """Get static recommendations from database."""
    try:
        db = _load_projects_db()
        role_projects = db.get(target_role, db.get("Software Engineer", {}))
        return role_projects.get(level, role_projects.get("beginner", []))
    except Exception as e:
        logger.warning(f"Could not load projects DB: {e}")
        return []


def _get_ai_recommendations(
    profile: Dict,
    target_role: str,
    level: str,
    existing_projects: List[str],
) -> Dict:
    """Use AI to generate personalized project recommendations."""
    skills = profile.get("skills", [])[:8]

    prompt = f"""Recommend 5 specific, unique portfolio projects for a {level} {target_role} candidate.

Their existing skills: {', '.join(skills)}
Projects they already have: {', '.join(existing_projects) or 'None'}

Return JSON:
{{
  "projects": [
    {{
      "title": "...",
      "description": "2-3 sentence project description",
      "why_build": "Why this project impresses {target_role} recruiters",
      "technologies": ["tech1", "tech2", "tech3"],
      "difficulty": "Beginner/Intermediate/Advanced",
      "estimated_time": "X weeks",
      "impact_score": <1-10>,
      "github_topics": ["tag1", "tag2"],
      "deployment": "Where/how to deploy",
      "what_to_add": "One unique feature that makes it stand out",
      "recruiters_love": "Why this specifically impresses recruiters"
    }}
  ],
  "build_order": ["Project 1 title", "Project 2 title", ...],
  "portfolio_strategy": "2-sentence strategy for maximizing portfolio impact",
  "github_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Make projects unique, market-relevant, and different from what they already have.
Focus on projects that solve real problems and demonstrate {target_role} competencies."""

    return generate_json(prompt, temperature=0.8, max_tokens=3000)


def _get_portfolio_strategy(target_role: str, level: str) -> str:
    """Static portfolio strategy by role."""
    strategies = {
        "Data Analyst": "Focus on end-to-end projects with clean visualizations. Use real public datasets. Deploy dashboards on Streamlit Cloud.",
        "Data Scientist": "Build ML pipelines with documented experiments. Show your thought process. Deploy models as APIs.",
        "AI Engineer": "Showcase LLM applications and fine-tuned models. Include RAG systems and AI APIs. Prioritize real-world use cases.",
        "Software Engineer": "Show breadth: backend API, frontend app, and CLI tool. Include CI/CD and clean documentation.",
        "Cybersecurity Analyst": "Document security tools you've built. Include CTF writeups and security research posts.",
        "Embedded Engineer": "Video demos of working hardware are essential. Include circuit diagrams and detailed READMEs.",
    }
    return strategies.get(target_role, "Build projects that solve real problems and demonstrate your core technical skills.")
