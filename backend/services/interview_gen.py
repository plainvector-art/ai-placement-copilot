"""
AI Interview Question Generator.
Uses Gemini to create personalized, resume-aware interview questions.
"""
import json
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_json, generate_text


SYSTEM_CONTEXT = """You are an expert technical recruiter and interview coach with 15+ years of experience 
at top tech companies. You create highly targeted, relevant interview questions based on a candidate's 
actual resume, projects, and target role."""


def generate_interview_questions(
    profile: Dict,
    target_role: str,
    difficulty: str = "Mixed",
) -> Dict:
    """
    Generate comprehensive interview question set using AI.

    Args:
        profile: Parsed candidate profile
        target_role: Target job role
        difficulty: Question difficulty (Easy/Medium/Hard/Mixed)

    Returns:
        Structured question bank with 40 questions across 4 categories
    """
    logger.info(f"Generating interview questions for {target_role}")

    name = profile.get("name", "the candidate")
    skills = profile.get("skills", [])[:15]
    projects = profile.get("projects", [])[:3]
    experience = profile.get("experience", [])[:2]
    certs = profile.get("certifications", [])[:3]

    # Build context
    project_summary = "\n".join([
        f"- {p.get('title', 'Project')}: {p.get('description', '')[:100]}"
        for p in projects
    ])
    skills_str = ", ".join(skills[:12])

    prompt = f"""Generate a comprehensive interview question set for a {target_role} candidate.

CANDIDATE PROFILE:
- Name: {name}
- Key Skills: {skills_str}
- Projects: {project_summary or "Not specified"}
- Certifications: {', '.join(certs) or "None"}
- Difficulty Level: {difficulty}

Generate exactly this structure in JSON:
{{
  "hr_questions": [
    {{"id": 1, "question": "...", "category": "HR", "difficulty": "Easy", "tip": "..."}}
    // 10 HR/behavioral questions about background, motivation, teamwork
  ],
  "technical_questions": [
    {{"id": 1, "question": "...", "category": "Technical", "difficulty": "Medium/Hard", "tip": "...", "expected_topics": ["..."]}}
    // 15 technical questions specific to {target_role} skills and technologies
  ],
  "project_questions": [
    {{"id": 1, "question": "...", "category": "Project", "difficulty": "Medium", "tip": "..."}}
    // 10 deep-dive questions about the candidate's specific projects
  ],
  "behavioral_questions": [
    {{"id": 1, "question": "...", "category": "Behavioral", "difficulty": "Medium", "tip": "...", "framework": "STAR"}}
    // 5 behavioral questions using STAR format
  ]
}}

Make questions highly specific to the candidate's background. Reference actual skills and projects.
Technical questions should test real knowledge needed for {target_role}."""

    result = generate_json(prompt, temperature=0.8, max_tokens=5000)

    if not result or "error" in str(result).lower():
        logger.warning("AI question generation returned empty result, using fallback")
        return _generate_fallback_questions(target_role, skills)

    # Enrich with metadata
    result["metadata"] = {
        "target_role": target_role,
        "difficulty": difficulty,
        "total_questions": sum([
            len(result.get("hr_questions", [])),
            len(result.get("technical_questions", [])),
            len(result.get("project_questions", [])),
            len(result.get("behavioral_questions", [])),
        ]),
        "candidate_name": name,
        "generated_skills": skills[:5],
    }

    logger.info(f"Generated {result['metadata']['total_questions']} interview questions")
    return result


def generate_single_question(
    profile: Dict,
    target_role: str,
    category: str,
    previous_questions: Optional[List[str]] = None,
) -> Dict:
    """Generate a single follow-up question based on context."""
    prev = "\n".join(previous_questions or [])
    prompt = f"""Generate ONE unique {category} interview question for a {target_role} candidate.

Candidate skills: {', '.join(profile.get('skills', [])[:8])}
Previous questions asked: {prev or 'None'}

Return JSON: {{"question": "...", "category": "{category}", "tip": "..."}}"""

    return generate_json(prompt, temperature=0.9)


def _generate_fallback_questions(target_role: str, skills: List[str]) -> Dict:
    """Return a basic question set when AI is unavailable."""
    skills_str = skills[:3] if skills else ["technical skills"]

    return {
        "hr_questions": [
            {"id": i+1, "question": q, "category": "HR", "difficulty": "Easy", "tip": "Be specific and genuine"}
            for i, q in enumerate([
                "Tell me about yourself and your journey into tech.",
                f"Why are you interested in the {target_role} role?",
                "What's your greatest professional achievement?",
                "Where do you see yourself in 5 years?",
                "Describe a challenge you faced and how you overcame it.",
                "What motivates you to work in this field?",
                "How do you handle tight deadlines and pressure?",
                "What's your preferred work environment?",
                "Tell me about a time you worked in a team.",
                "What do you know about our company?",
            ])
        ],
        "technical_questions": [
            {"id": i+1, "question": q, "category": "Technical", "difficulty": "Medium", "tip": "Explain your thought process"}
            for i, q in enumerate([
                f"Explain the core difference between supervised and unsupervised learning.",
                f"How would you approach debugging a failing data pipeline?",
                f"Describe your experience with {skills_str[0] if skills_str else 'Python'}.",
                f"What is your approach to optimizing slow code?",
                "How do you ensure code quality and maintainability?",
            ])
        ],
        "project_questions": [
            {"id": i+1, "question": q, "category": "Project", "difficulty": "Medium", "tip": "Use the STAR method"}
            for i, q in enumerate([
                "Walk me through your most impactful project.",
                "What technical challenges did you face and how did you solve them?",
                "How did you measure the success of your project?",
                "What would you do differently if you rebuilt it?",
                "How did you collaborate with others on this project?",
            ])
        ],
        "behavioral_questions": [
            {"id": i+1, "question": q, "category": "Behavioral", "difficulty": "Medium", "tip": "Use STAR: Situation, Task, Action, Result", "framework": "STAR"}
            for i, q in enumerate([
                "Tell me about a time you had to learn a new skill quickly.",
                "Describe a situation where you disagreed with a team member. How did you resolve it?",
                "Give an example of when you took initiative without being asked.",
                "Tell me about a time you failed. What did you learn?",
                "Describe a time when you had to manage multiple priorities.",
            ])
        ],
        "metadata": {
            "target_role": target_role,
            "difficulty": "Mixed",
            "total_questions": 25,
            "note": "Demo questions — configure AI API for personalized questions",
        }
    }
