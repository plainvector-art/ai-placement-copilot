"""
Recruiter Insights Generator.
Uses Gemini to generate detailed plain-English recruiter insights,
fit assessments, and interview questions for ranked candidates.
"""
from backend.services.ai_client import generate_json, is_ai_configured
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

    prompt = f"""
    You are an expert technical recruiter. Analyze the candidate's profile against the job description requirements.
    
    JOB TITLE: {jd_parsed.get('role_title')}
    REQUIRED SKILLS: {", ".join(jd_parsed.get('required_skills', []))}
    DOMAIN: {jd_parsed.get('domain')}
    
    CANDIDATE PROFILE:
    - Name: {profile.get('name')}
    - Skills: {", ".join(profile.get('skills', []))}
    - Summary: {profile.get('summary')}
    - Semantic Fit Score: {scores.get('semantic_score')}%
    - ATS Quality Score: {scores.get('ats_score')}%
    
    Generate a JSON object with the following keys:
    - "fit_analysis": "A detailed 2-3 sentence recruiter assessment of how well this candidate fits the role."
    - "technical_vetting_points": ["2-3 specific technical topics or skills on their resume that match the job and should be verified"]
    - "suggested_interview_questions": ["2 custom interview questions to ask this candidate based on their background and gaps"]
    
    Make sure the response contains ONLY valid JSON and no code block wrappers.
    """
    
    result = generate_json(prompt, temperature=0.3, max_tokens=600, fallback=fallback)
    
    # Ensure all required keys are in the result
    for key in ["fit_analysis", "technical_vetting_points", "suggested_interview_questions"]:
        if key not in result or not result[key]:
            result[key] = fallback[key]
            
    return result
