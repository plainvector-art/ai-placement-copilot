"""
Learning Roadmap Generator.
Creates personalized 30/60/90 day + 6-month roadmaps based on skill gaps.
"""
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_json


ROADMAP_SYSTEM = """You are an expert career development coach and curriculum designer 
who creates highly practical, week-by-week learning roadmaps for tech professionals."""


def generate_roadmap(
    profile: Dict,
    target_role: str,
    skill_gap_data: Dict,
    available_hours_per_week: int = 10,
) -> Dict:
    """
    Generate a personalized learning roadmap.

    Args:
        profile: Candidate profile
        target_role: Target job role
        skill_gap_data: Skill gap analysis result
        available_hours_per_week: Study hours per week

    Returns:
        Structured 6-month roadmap with phases
    """
    logger.info(f"Generating learning roadmap for {target_role}")

    name = profile.get("name", "the candidate")
    existing_skills = profile.get("skills", [])[:10]
    missing_skills = skill_gap_data.get("missing_skills", [])[:10]
    priority_skills = [s["skill"] for s in skill_gap_data.get("priority_skills", [])[:5]]

    prompt = f"""{ROADMAP_SYSTEM}

Create a comprehensive personalized learning roadmap for {name} targeting the {target_role} role.

CURRENT STATE:
- Existing Skills: {', '.join(existing_skills)}
- Missing Required Skills: {', '.join(missing_skills)}
- Priority Skills to Learn: {', '.join(priority_skills)}
- Available Study Time: {available_hours_per_week} hours/week

Create a practical, actionable roadmap in this exact JSON structure:
{{
  "summary": {{
    "target_role": "{target_role}",
    "total_duration": "6 months",
    "total_hours": <number>,
    "key_focus_areas": ["...", "...", "..."],
    "expected_outcome": "..."
  }},
  "phases": {{
    "phase_1": {{
      "name": "Foundation Building",
      "duration": "30 days",
      "weeks": 4,
      "goal": "...",
      "weeks_breakdown": [
        {{
          "week": 1,
          "focus": "...",
          "topics": ["...", "..."],
          "project": "...",
          "hours": <number>,
          "resources": [
            {{"title": "...", "type": "Course/Book/Video/Practice", "url": "...", "free": true/false}}
          ],
          "milestone": "..."
        }}
      ],
      "phase_project": "...",
      "skills_gained": ["...", "..."],
      "milestone": "..."
    }},
    "phase_2": {{
      "name": "Core Skills Development",
      "duration": "60 days",
      "weeks": 8,
      "goal": "...",
      // similar structure, focus on key technical skills for {target_role}
    }},
    "phase_3": {{
      "name": "Advanced Skills & Projects",
      "duration": "90 days",
      "weeks": 12,
      "goal": "...",
      // advanced topics, portfolio projects
    }},
    "phase_4": {{
      "name": "Interview Prep & Job Search",
      "duration": "6 months",
      "weeks": 24,
      "goal": "...",
      // system design, mock interviews, applications
    }}
  }},
  "daily_schedule": {{
    "morning": "...",
    "evening": "...",
    "weekend": "..."
  }},
  "key_milestones": [
    {{"month": 1, "milestone": "...", "proof": "..."}},
    {{"month": 2, "milestone": "...", "proof": "..."}},
    {{"month": 3, "milestone": "...", "proof": "..."}},
    {{"month": 6, "milestone": "...", "proof": "..."}}
  ],
  "recommended_projects": [
    {{"name": "...", "phase": 1, "skills": ["..."], "complexity": "Beginner"}},
    {{"name": "...", "phase": 2, "skills": ["..."], "complexity": "Intermediate"}},
    {{"name": "...", "phase": 3, "skills": ["..."], "complexity": "Advanced"}}
  ],
  "top_resources": [
    {{"title": "...", "type": "...", "url": "...", "why": "...", "free": true}}
  ],
  "success_metrics": ["...", "...", "..."]
}}

Make it realistic, specific to {target_role}, and reference actual tools and resources."""

    result = generate_json(prompt, temperature=0.6, max_tokens=6000)

    if not result or not result.get("phases"):
        logger.warning("AI roadmap generation returned empty, using template")
        result = _generate_template_roadmap(target_role, missing_skills, available_hours_per_week)

    # Add metadata
    result["metadata"] = {
        "generated_for": name,
        "target_role": target_role,
        "hours_per_week": available_hours_per_week,
        "missing_skills_count": len(missing_skills),
        "priority_skills": priority_skills,
    }

    logger.info(f"Roadmap generated: {len(result.get('phases', {}))} phases")
    return result


def _generate_template_roadmap(
    target_role: str,
    missing_skills: List[str],
    hours_per_week: int,
) -> Dict:
    """Template roadmap when AI is unavailable."""
    top_3 = missing_skills[:3] if missing_skills else ["Core Skills", "Projects", "Interviews"]

    return {
        "summary": {
            "target_role": target_role,
            "total_duration": "6 months",
            "total_hours": hours_per_week * 24,
            "key_focus_areas": top_3,
            "expected_outcome": f"Land a {target_role} role at a top company",
        },
        "phases": {
            "phase_1": {
                "name": "Foundation Building",
                "duration": "30 days",
                "weeks": 4,
                "goal": f"Build foundational skills for {target_role}",
                "weeks_breakdown": [
                    {
                        "week": i+1,
                        "focus": f"Learn {top_3[min(i, len(top_3)-1)]}",
                        "topics": [f"{top_3[min(i, len(top_3)-1)]} basics", "Hands-on practice"],
                        "hours": hours_per_week,
                        "resources": [
                            {"title": "Free Course on YouTube/Coursera", "type": "Course", "url": "#", "free": True}
                        ],
                        "milestone": f"Complete {top_3[min(i, len(top_3)-1)]} basics",
                    }
                    for i in range(4)
                ],
                "skills_gained": top_3[:2],
                "milestone": "Foundation complete",
            },
            "phase_2": {
                "name": "Core Skills Development",
                "duration": "30-60 days",
                "weeks": 8,
                "goal": "Master the key technical skills",
                "skills_gained": missing_skills[:4] if len(missing_skills) > 2 else missing_skills,
                "milestone": "Build first portfolio project",
            },
            "phase_3": {
                "name": "Projects & Portfolio",
                "duration": "60-90 days",
                "weeks": 12,
                "goal": "Build 3 impressive portfolio projects",
                "skills_gained": missing_skills[4:] if len(missing_skills) > 4 else [],
                "milestone": "3 projects on GitHub",
            },
            "phase_4": {
                "name": "Interview Prep & Applications",
                "duration": "Month 4-6",
                "weeks": 24,
                "goal": "Land placement interviews and offers",
                "skills_gained": ["Interview skills", "System design", "Networking"],
                "milestone": "Receive job offer",
            },
        },
        "key_milestones": [
            {"month": 1, "milestone": "Core skills established", "proof": "2 practice projects"},
            {"month": 2, "milestone": "Portfolio project #1 deployed", "proof": "GitHub link"},
            {"month": 3, "milestone": "3 portfolio projects live", "proof": "GitHub portfolio"},
            {"month": 6, "milestone": "Job offer received", "proof": "Offer letter"},
        ],
        "top_resources": [
            {"title": "freeCodeCamp", "type": "Free Course Platform", "url": "https://freecodecamp.org", "why": "Free, comprehensive", "free": True},
            {"title": "Coursera", "type": "Course Platform", "url": "https://coursera.org", "why": "Industry-backed certificates", "free": False},
            {"title": "LeetCode", "type": "Practice", "url": "https://leetcode.com", "why": "Essential for technical interviews", "free": True},
            {"title": "GitHub", "type": "Portfolio", "url": "https://github.com", "why": "Showcase your projects", "free": True},
        ],
        "success_metrics": [
            "Complete all planned learning resources",
            "Build and deploy 3 portfolio projects",
            "Solve 100+ coding problems",
            "Complete 10+ mock interviews",
            "Apply to 50+ positions",
        ],
    }


def get_daily_plan(roadmap: Dict, current_day: int) -> Dict:
    """Get today's specific learning plan from roadmap."""
    current_week = (current_day // 7) + 1
    current_phase = "phase_1" if current_day <= 30 else (
        "phase_2" if current_day <= 60 else (
            "phase_3" if current_day <= 90 else "phase_4"
        )
    )

    phase_data = roadmap.get("phases", {}).get(current_phase, {})

    return {
        "day": current_day,
        "week": current_week,
        "phase": current_phase.replace("_", " ").title(),
        "today_focus": phase_data.get("goal", "Continue your learning journey"),
        "daily_schedule": roadmap.get("daily_schedule", {}),
    }
