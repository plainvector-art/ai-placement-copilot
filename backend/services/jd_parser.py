"""
Job Description Parser.
Uses Gemini to extract structured requirements from raw JD text.
Identifies must-haves vs nice-to-haves, seniority, and role context.
"""
from backend.services.ai_client import generate_json
from loguru import logger


def parse_job_description(jd_text: str) -> dict:
    """
    Parses structured requirements from raw Job Description text.
    """
    logger.info(f"Parsing JD with AI — {len(jd_text)} chars")

    prompt = f"""
    Analyze the following job description and extract the structured requirements:
    
    JOB DESCRIPTION:
    {jd_text}
    
    Extract the information as a JSON object with these exact keys:
    - "role_title": string — inferred job title
    - "seniority_level": string — one of: Intern, Junior, Mid, Senior, Lead
    - "required_skills": list of must-have technical skills
    - "preferred_skills": list of nice-to-have skills
    - "key_responsibilities": list of top 4 responsibilities as short phrases
    - "minimum_experience_years": integer representing years of experience, or null if not specified
    - "domain": string — e.g. Data Analytics, Backend Engineering, ML/AI, Front-End, DevOps, Full-Stack, etc.
    - "red_flags_for_mismatch": list of 2-3 things that would disqualify a candidate immediately
    
    Make sure the response contains ONLY valid JSON and no code block wrappers.
    """

    result = generate_json(prompt, temperature=0.2, max_tokens=800)

    if not result or "required_skills" not in result:
        logger.warning("Failed to parse JD with AI or returned data is empty. Using fallback.")
        return {
            "role_title": "Unknown",
            "required_skills": [],
            "preferred_skills": [],
            "seniority_level": "Unknown",
            "domain": "General",
            "key_responsibilities": [],
            "minimum_experience_years": None,
            "red_flags_for_mismatch": []
        }

    # Ensure other keys are present with sensible defaults to prevent KeyErrors
    defaults = {
        "role_title": "Unknown",
        "seniority_level": "Unknown",
        "required_skills": [],
        "preferred_skills": [],
        "key_responsibilities": [],
        "minimum_experience_years": None,
        "domain": "General",
        "red_flags_for_mismatch": []
    }
    for key, val in defaults.items():
        if key not in result or result[key] is None:
            result[key] = val

    return result
