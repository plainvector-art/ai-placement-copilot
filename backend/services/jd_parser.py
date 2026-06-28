"""
Job Description Parser.
Uses Gemini to extract structured requirements from raw JD text.
Identifies must-haves vs nice-to-haves, seniority, and role context.
"""
from backend.services.ai_client import generate_json
from backend.services.prompts import PROMPTS
from loguru import logger


def parse_job_description(jd_text: str) -> dict:
    """
    Parses structured requirements from raw Job Description text.
    """
    logger.info(f"Parsing JD with AI — {len(jd_text)} chars")

    prompt = PROMPTS["jd_parser"].format(jd_text=jd_text)

    schema = {
        "role_title": str,
        "seniority_level": str,
        "required_skills": list,
        "preferred_skills": list,
        "key_responsibilities": list,
        "domain": str,
        "red_flags_for_mismatch": list
    }

    result = generate_json(prompt, temperature=0.2, max_tokens=800, schema=schema)

    fallback = {
        "role_title": "Unknown",
        "required_skills": [],
        "preferred_skills": [],
        "seniority_level": "Unknown",
        "domain": "General",
        "key_responsibilities": [],
        "minimum_experience_years": None,
        "red_flags_for_mismatch": []
    }

    if not result or "required_skills" not in result:
        logger.warning("Failed to parse JD with AI or returned data is empty. Using fallback.")
        return fallback

    # Ensure other keys are present with sensible defaults to prevent KeyErrors
    for key, val in fallback.items():
        if key not in result or result[key] is None:
            result[key] = val

    return result
