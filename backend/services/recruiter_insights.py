"""
Recruiter Insights Generator.
Uses Gemini to generate detailed plain-English recruiter insights,
fit assessments, and interview questions for ranked candidates.
"""
from backend.services.ai_client import generate_json, is_ai_configured
from backend.services.prompts import PROMPTS
from loguru import logger

def generate_candidate_insights(
    profile: dict,
    scores: dict,
    jd_parsed: dict
) -> dict:
    """
    Generates detailed recruiter insights using Gemini.
    """
    logger.info(f"Generating LLM insights for candidate: {profile.get('name', 'Unknown')}")
    
    fallback = {
        "fit_analysis": f"Candidate demonstrates a {scores.get('semantic_score')}% semantic match for the {jd_parsed.get('role_title', 'specified')} position.",
        "technical_vetting_points": ["Assess core technology skills", "Verify project experience"],
        "suggested_interview_questions": ["Can you talk about a technical challenge you faced?", "How do you keep up with new technology?"]
    }

    if not is_ai_configured():
        logger.warning("AI is not configured. Returning fallback insights.")
        return fallback

    prompt = PROMPTS["recruiter_insights"].format(
        role_title=jd_parsed.get('role_title', 'Software Engineer'),
        required_skills=", ".join(jd_parsed.get('required_skills', [])),
        domain=jd_parsed.get('domain', 'General'),
        name=profile.get('name', 'Candidate'),
        skills=", ".join(profile.get('skills', [])),
        summary=profile.get('summary', ''),
        semantic_score=scores.get('semantic_score', 0),
        ats_score=scores.get('ats_score', 0)
    )
    
    # Define validation schema
    schema = {
        "fit_analysis": str,
        "technical_vetting_points": list,
        "suggested_interview_questions": list
    }
    
    result = generate_json(prompt, temperature=0.3, max_tokens=600, fallback=fallback, schema=schema)
    
    # Ensure all required keys are in the result
    for key in ["fit_analysis", "technical_vetting_points", "suggested_interview_questions"]:
        if key not in result or not result[key]:
            result[key] = fallback[key]
            
    return result
