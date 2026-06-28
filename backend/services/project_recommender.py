"""
Project Recommendations Service.
Suggests resume portfolio projects matching the candidate profile and role gap.
"""
import os
import json
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_json
from backend.services.prompts import PROMPTS


def recommend_projects(profile: Dict, target_role: str) -> Dict:
    """
    Generate customized project recommendations based on candidate gaps.
    """
    logger.info(f"Generating project recommendations for {target_role}")

    # Determine candidate experience level
    level = _determine_experience_level(profile)

    # Get candidate's existing projects
    existing = [p.get("title", "") for p in profile.get("projects", [])]

    # Try AI generation first
    try:
        from backend.services.ai_client import is_ai_configured
        if is_ai_configured():
            ai_recs = _get_ai_recommendations(profile, target_role, level, existing)
            if ai_recs and "projects" in ai_recs:
                return ai_recs
    except Exception as e:
        logger.warning(f"AI project recommendation failed: {e}. Falling back to DB.")

    # Fallback to local project database
    static_projects = _get_db_recommendations(target_role, level)

    return {
        "experience_level": level,
        "projects": static_projects,
        "build_order": [p["title"] for p in static_projects[:3]] if static_projects else [],
        "portfolio_strategy": _get_portfolio_strategy(target_role, level),
        "github_tips": [
            "Create a clean README.md with clear installation and usage steps.",
            "Include architectural diagrams and screenshots or GIFs of the app.",
            "Write modular, documented code and use environment variables for secrets."
        ]
    }


def _determine_experience_level(profile: Dict) -> str:
    """Assess experience level (beginner, intermediate, advanced)."""
    exp = profile.get("experience", [])
    skills = profile.get("skills", [])
    projects = profile.get("projects", [])

    score = 0
    if len(exp) >= 3:
        score += 3
    elif len(exp) >= 1:
        score += 1

    if len(skills) >= 12:
        score += 2
    elif len(skills) >= 6:
        score += 1

    if len(projects) >= 3:
        score += 2
    elif len(projects) >= 1:
        score += 1

    if score >= 6:
        return "advanced"
    elif score >= 3:
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

    prompt = PROMPTS["project_recs"].format(
        level=level,
        target_role=target_role,
        skills=', '.join(skills),
        existing_projects=', '.join(existing_projects) or 'None'
    )

    schema = {
        "projects": list,
        "build_order": list,
        "portfolio_strategy": str,
        "github_tips": list
    }

    return generate_json(prompt, temperature=0.8, max_tokens=3000, schema=schema)


def _get_portfolio_strategy(target_role: str, level: str) -> str:
    """Static portfolio strategy by role."""
    strategies = {
        "Data Analyst": "Focus on end-to-end projects with clean visualizations. Use real public datasets. Deploy dashboards on Streamlit Cloud.",
        "Data Scientist": "Build ML pipelines with documented experiments. Show your thought process. Deploy models as APIs.",
        "Software Engineer": "Build full-stack applications with robust backend APIs, clear database design, and unit tests. Containerize using Docker.",
        "DevOps Engineer": "Build automated infrastructure pipelines. Implement CI/CD, Kubernetes deployments, and terraform infrastructure as code.",
        "AI/ML Engineer": "Fine-tune open-source models, build RAG applications with vector databases, or deploy scalable deep learning models. Highlight API/latency metrics."
    }
    return strategies.get(target_role, "Focus on building a diverse portfolio that showcases strong problem-solving and documentation.")


def _load_projects_db() -> Dict:
    """Load standard local project ideas database."""
    # Return minimal default DB structure to prevent file read crashes
    return {
        "Software Engineer": {
            "beginner": [
                {
                    "title": "Task Manager API",
                    "description": "RESTful task manager API with token authentication, CRUD operations, and request validation.",
                    "why_build": "Shows understanding of core HTTP methods, routing, database integrations, and secure auth flows.",
                    "technologies": ["FastAPI", "SQLite", "Pydantic", "JWT"],
                    "difficulty": "Beginner",
                    "estimated_time": "2 weeks",
                    "impact_score": 6,
                    "github_topics": ["fastapi", "backend", "sqlite"],
                    "deployment": "Render / Fly.io",
                    "what_to_add": "Implement a task grouping system with tags and deadline notifications.",
                    "recruiters_love": "Demonstrates backend engineering foundations and secure authorization handling."
                }
            ],
            "intermediate": [
                {
                    "title": "Distributed Task Scheduler",
                    "description": "Asynchronous backend worker service that schedules and executes background tasks with retry handling.",
                    "why_build": "Demonstrates architecture design, event-driven design, and queue message handling.",
                    "technologies": ["Python", "Celery", "Redis", "Docker"],
                    "difficulty": "Intermediate",
                    "estimated_time": "3 weeks",
                    "impact_score": 8,
                    "github_topics": ["asynchronous", "redis", "celery"],
                    "deployment": "AWS EC2 / Render Docker",
                    "what_to_add": "Build a simple web GUI using Streamlit to monitor queue task progress in real time.",
                    "recruiters_love": "Demonstrates familiarity with enterprise caching queues, background workers, and containerization."
                }
            ]
        }
    }
