"""
AI Interview Question Generator.
Uses Gemini to create personalized, resume-aware interview questions.
"""
import json
from typing import Dict, List, Optional
from loguru import logger

from backend.services.ai_client import generate_json, generate_text
from backend.services.prompts import PROMPTS


def generate_interview_questions(
    profile: Dict,
    target_role: str,
    difficulty: str = "Mixed",
) -> Dict:
    """
    Generate comprehensive interview question set using AI.
    """
    logger.info(f"Generating interview questions for {target_role}")

    name = profile.get("name", "Candidate")
    skills = profile.get("skills", [])[:15]
    projects = profile.get("projects", [])[:3]
    certs = profile.get("certifications", [])[:3]

    project_summary = "\n".join([
        f"- {p.get('title', 'Project')}: {p.get('description', '')[:100]}"
        for p in projects
    ])
    skills_str = ", ".join(skills[:12])

    prompt = PROMPTS["interview_questions"].format(
        target_role=target_role,
        name=name,
        skills_str=skills_str,
        project_summary=project_summary or "Not specified",
        certs=', '.join(certs) or "None",
        difficulty=difficulty
    )

    schema = {
        "hr_questions": list,
        "technical_questions": list,
        "project_questions": list,
        "behavioral_questions": list
    }

    result = generate_json(prompt, temperature=0.8, max_tokens=5000, schema=schema)

    if not result or "error" in str(result).lower() or not isinstance(result, dict) or "hr_questions" not in result:
        logger.warning("AI question generation returned empty or malformed result, using fallback")
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

    schema = {
        "question": str,
        "category": str,
        "tip": str
    }

    return generate_json(prompt, temperature=0.9, schema=schema)


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
