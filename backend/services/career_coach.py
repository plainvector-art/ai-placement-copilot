"""
AI Career Coach Service.
RAG-style chatbot using candidate profile as context for personalized advice.
Also handles: Cover Letter generation, LinkedIn profile generation.
"""
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_text, generate_json


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

    Args:
        user_message: User's question/message
        profile: Candidate profile context
        target_role: Current target role
        chat_history: Previous conversation messages
        skill_gap_data: Optional skill gap analysis for context

    Returns:
        AI coach response text
    """
    # Build rich context
    context = _build_context(profile, target_role, skill_gap_data)

    # Format chat history (last 10 messages)
    history_text = ""
    for msg in chat_history[-10:]:
        role_label = "Student" if msg["role"] == "user" else "Coach"
        history_text += f"{role_label}: {msg['content']}\n\n"

    prompt = f"""{CAREER_COACH_SYSTEM}

=== CANDIDATE CONTEXT ===
{context}

=== CONVERSATION HISTORY ===
{history_text}
=== NEW MESSAGE ===
Student: {user_message}

Respond as CareerCopilot Coach. Be specific, reference their actual profile data, 
and give actionable steps they can take TODAY."""

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

    prompt = f"""Write a compelling, professional cover letter for {name} applying for {target_role}{f' at {company_name}' if company_name else ''}.

CANDIDATE PROFILE:
- Skills: {skills}
- Key Projects: {projects}
- Experience entries: {len(experience)}
- Email: {email}

{f'JOB DESCRIPTION CONTEXT: {job_description[:500]}' if job_description else ''}

Requirements:
- Opening paragraph: Hook + why this role excites them
- Middle paragraphs: Specific achievements + how skills match the role (reference 2-3 real skills)
- Closing: Call to action, confidence, next steps
- Professional but personable tone
- 300-400 words total
- Do NOT use generic phrases like "I am writing to express my interest"
- Reference specific technologies and projects naturally
- Make it sound HUMAN, not AI-generated

Format as a proper business letter."""

    return generate_text(prompt, temperature=0.8, max_tokens=1000)


def generate_linkedin_headline(profile: Dict, target_role: str) -> Dict:
    """Generate LinkedIn headline and About section."""
    name = profile.get("name", "")
    skills = profile.get("skills", [])[:6]
    certs = profile.get("certifications", [])[:2]

    prompt = f"""Generate LinkedIn profile content for {name} targeting {target_role}.

Current Skills: {', '.join(skills)}
Certifications: {', '.join(certs) or 'None yet'}

Return JSON:
{{
  "headlines": [
    "Option 1: keyword-rich, role-specific headline",
    "Option 2: achievement-focused headline",
    "Option 3: aspirational headline with current state"
  ],
  "about_section": "3-4 paragraph LinkedIn About section. Professional, personable, includes key skills and what makes them unique. End with a call to connect.",
  "skills_to_add": ["...", "...", "..."],
  "connection_message_template": "Short personalized connection request message template"
}}"""

    return generate_json(prompt, temperature=0.75, max_tokens=1500)


def predict_career_path(profile: Dict, target_role: str) -> Dict:
    """Generate career trajectory prediction."""
    prompt = f"""Map out a realistic 5-year career path for someone targeting {target_role}.

Current profile:
- Skills: {', '.join(profile.get('skills', [])[:8])}
- Projects: {len(profile.get('projects', []))}
- Experience: {len(profile.get('experience', []))} entries

Return JSON:
{{
  "current_level": "...",
  "path": [
    {{"year": 0, "role": "...", "salary_range": "...", "key_skills": ["..."], "companies": ["types"]}},
    {{"year": 1, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}},
    {{"year": 2, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}},
    {{"year": 3, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}},
    {{"year": 5, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}}
  ],
  "alternative_paths": ["...", "..."],
  "salary_trajectory": "...",
  "advice": "..."
}}"""

    return generate_json(prompt, temperature=0.5, max_tokens=2000)


def estimate_salary(profile: Dict, target_role: str, location: str = "US") -> Dict:
    """Estimate salary range based on profile."""
    skills = profile.get("skills", [])
    exp_count = len(profile.get("experience", []))
    cert_count = len(profile.get("certifications", []))

    prompt = f"""Estimate realistic salary ranges for a {target_role} candidate in {location}.

Profile strength:
- Skills count: {len(skills)} ({', '.join(skills[:5])})
- Experience entries: {exp_count}
- Certifications: {cert_count}

Return JSON:
{{
  "entry_level": {{"min": <number>, "max": <number>, "typical": <number>}},
  "mid_level": {{"min": <number>, "max": <number>, "typical": <number>}},
  "senior_level": {{"min": <number>, "max": <number>, "typical": <number>}},
  "candidate_estimate": {{"min": <number>, "max": <number>, "level": "Entry/Mid/Senior"}},
  "top_paying_companies": ["...", "...", "..."],
  "skills_that_increase_salary": ["...", "...", "..."],
  "negotiation_tips": ["...", "..."],
  "currency": "USD"
}}"""

    return generate_json(prompt, temperature=0.3, max_tokens=1000)


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
