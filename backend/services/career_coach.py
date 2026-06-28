"""
AI Career Coach Service.
RAG-style chatbot using candidate profile as context for personalized advice.
Also handles: Cover Letter generation, LinkedIn profile generation.
"""
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_text, generate_json
from backend.services.prompts import PROMPTS

CAREER_COACH_SYSTEM = """You are CareerCopilot AI — a world-class career coach specializing in 
tech placements. You have deep knowledge of:
- Technical interview preparation (FAANG and startups)
- Resume optimization and ATS systems
- Skill development roadmaps
- Industry trends and salary negotiation
- Portfolio building and personal branding

You give SPECIFIC, ACTIONABLE advice based on the candidate's actual profile. 
No generic platitudes. Always reference their specific skills, projects, and target role.
Keep responses focused, practical, and encouraging. Format with markdown."""


def chat_with_coach(
    user_message: str,
    profile: Dict,
    target_role: str,
    chat_history: List[Dict],
    skill_gap_data: Optional[Dict] = None,
) -> str:
    """
    Process a career coaching chat message.
    """
    context = _build_context(profile, target_role, skill_gap_data)

    # Format chat history (last 10 messages)
    history_text = ""
    for msg in chat_history[-10:]:
        role_label = "Student" if msg["role"] == "user" else "Coach"
        history_text += f"{role_label}: {msg['content']}\n\n"

    prompt = PROMPTS["career_coach_chat"].format(
        system_persona=CAREER_COACH_SYSTEM,
        context=context,
        history_text=history_text,
        user_message=user_message
    )

    response = generate_text(prompt, temperature=0.75, max_tokens=1500)
    return response


def generate_cover_letter(
    profile: Dict,
    target_role: str,
    company_name: str = "",
    job_description: str = "",
) -> str:
    """Generate a personalized cover letter."""
    name = profile.get("name", "Candidate")
    email = profile.get("email", "")
    skills = ", ".join(profile.get("skills", [])[:8])
    projects = "\n".join([
        f"- {p.get('title', '')}: {p.get('description', '')[:100]}"
        for p in profile.get("projects", [])[:3]
    ])
    experience = profile.get("experience", [])

    company_clause = f" at {company_name}" if company_name else ""
    jd_context = f"JOB DESCRIPTION CONTEXT: {job_description[:500]}" if job_description else ""

    prompt = PROMPTS["cover_letter"].format(
        name=name,
        target_role=target_role,
        company_clause=company_clause,
        skills=skills,
        projects=projects,
        experience_count=len(experience),
        email=email,
        jd_context=jd_context
    )

    return generate_text(prompt, temperature=0.8, max_tokens=1000)


def generate_linkedin_headline(profile: Dict, target_role: str) -> Dict:
    """Generate LinkedIn headline and About section."""
    name = profile.get("name", "")
    skills = profile.get("skills", [])[:6]
    certs = profile.get("certifications", [])[:2]

    prompt = PROMPTS["linkedin_headline"].format(
        name=name,
        target_role=target_role,
        skills=', '.join(skills),
        certs=', '.join(certs) or 'None yet'
    )

    schema = {
        "headlines": list,
        "about_section": str,
        "skills_to_add": list,
        "connection_message_template": str
    }

    return generate_json(prompt, temperature=0.75, max_tokens=1500, schema=schema)


def predict_career_path(profile: Dict, target_role: str) -> Dict:
    """Generate career trajectory prediction."""
    prompt = PROMPTS["career_path"].format(
        target_role=target_role,
        skills=', '.join(profile.get('skills', [])[:8]),
        projects_count=len(profile.get('projects', [])),
        experience_count=len(profile.get('experience', []))
    )

    schema = {
        "current_level": str,
        "path": list,
        "alternative_paths": list,
        "salary_trajectory": str,
        "advice": str
    }

    return generate_json(prompt, temperature=0.5, max_tokens=2000, schema=schema)


def estimate_salary(profile: Dict, target_role: str, location: str = "US") -> Dict:
    """Estimate salary range based on profile."""
    skills = profile.get("skills", [])
    exp_count = len(profile.get("experience", []))
    cert_count = len(profile.get("certifications", []))

    prompt = PROMPTS["salary_estimate"].format(
        target_role=target_role,
        location=location,
        skills_count=len(skills),
        skills_list=', '.join(skills[:5]),
        experience_count=exp_count,
        cert_count=cert_count
    )

    schema = {
        "entry_level": dict,
        "mid_level": dict,
        "senior_level": dict,
        "candidate_estimate": dict,
        "top_paying_companies": list,
        "skills_that_increase_salary": list,
        "negotiation_tips": list,
        "currency": str
    }

    return generate_json(prompt, temperature=0.3, max_tokens=1000, schema=schema)


def _build_context(profile: Dict, target_role: str, skill_gap_data: Optional[Dict]) -> str:
    """Build rich context string for the AI coach."""
    lines = [
        f"Name: {profile.get('name', 'Student')}",
        f"Target Role: {target_role}",
        f"Skills ({len(profile.get('skills', []))}): {', '.join(profile.get('skills', [])[:10])}",
        f"Projects ({len(profile.get('projects', []))}): {', '.join([p.get('title','') for p in profile.get('projects', [])[:3]])}",
        f"Education: {profile.get('education', [{}])[0].get('degree', 'Not specified') if profile.get('education') else 'Not specified'}",
        f"Certifications: {', '.join(profile.get('certifications', [])[:3]) or 'None'}",
    ]

    if skill_gap_data:
        lines.extend([
            f"Skill Coverage: {skill_gap_data.get('coverage', {}).get('overall', 0):.0f}%",
            f"Missing Skills: {', '.join(skill_gap_data.get('missing_skills', [])[:5])}",
        ])

    return "\n".join(lines)
