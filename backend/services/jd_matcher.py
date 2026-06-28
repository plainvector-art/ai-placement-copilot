"""
Job Description Matching Service.
Compares resume against JD to calculate match score and identify gaps.
"""
import re
from typing import Dict, List, Tuple, Set
from loguru import logger

from backend.services.resume_parser import extract_skills
from backend.services.ai_client import generate_json
from backend.services.prompts import PROMPTS


def calculate_jd_match(
    profile: Dict,
    job_description: str,
    use_ai: bool = True,
) -> Dict:
    """
    Comprehensive resume vs. job description matching.
    """
    logger.info("Calculating JD match score...")

    resume_text = profile.get("raw_text", "")
    resume_skills = {s.lower() for s in profile.get("skills", [])}

    # Extract keywords from JD
    jd_keywords = _extract_jd_keywords(job_description)
    jd_skills = set(s.lower() for s in extract_skills(job_description))

    # Calculate keyword match
    resume_text_lower = resume_text.lower()

    # Keyword matching
    matched_keywords = []
    missing_keywords = []

    for keyword in jd_keywords:
        if keyword.lower() in resume_text_lower:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    # Skill matching
    matched_skills = []
    missing_skills = []
    for skill in jd_skills:
        if any(skill in rs or rs in skill for rs in resume_skills):
            matched_skills.append(skill.title())
        else:
            missing_skills.append(skill.title())

    # Calculate scores
    keyword_match_pct = (
        len(matched_keywords) / len(jd_keywords) * 100
        if jd_keywords else 0
    )
    skill_match_pct = (
        len(matched_skills) / len(jd_skills) * 100
        if jd_skills else 0
    )

    # Overall match (weighted)
    overall_match = round(keyword_match_pct * 0.5 + skill_match_pct * 0.5, 1)

    # Calculate ATS optimization score
    ats_optimization = _calculate_ats_optimization(
        resume_text, job_description, jd_keywords
    )

    result = {
        "overall_match_score": overall_match,
        "keyword_match_score": round(keyword_match_pct, 1),
        "skill_match_score": round(skill_match_pct, 1),
        "ats_optimization_score": ats_optimization,
        "matched_keywords": matched_keywords[:20],
        "missing_keywords": missing_keywords[:15],
        "matched_skills": matched_skills[:15],
        "missing_skills": missing_skills[:10],
        "jd_keyword_count": len(jd_keywords),
        "jd_skill_count": len(jd_skills),
        "match_rating": _get_match_rating(overall_match),
        "recommendations": _generate_jd_recommendations(
            overall_match, missing_keywords, missing_skills, profile
        ),
    }

    # Enhance with AI analysis
    if use_ai and len(job_description) > 100:
        ai_analysis = _ai_jd_analysis(profile, job_description, result)
        if ai_analysis:
            result["ai_insights"] = ai_analysis

    logger.info(f"JD match: {overall_match}% ({result['match_rating']})")
    return result


def _extract_jd_keywords(jd_text: str) -> List[str]:
    """Extract important keywords from job description."""
    # Remove common stop words
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through", "during",
        "we", "you", "they", "our", "your", "their", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "must", "shall",
        "can", "need", "team", "work", "role", "position", "candidate",
        "experience", "years", "year", "ability", "strong", "excellent",
        "good", "knowledge", "understanding", "familiarity",
    }

    # Extract all meaningful words and phrases
    multi_word = re.findall(
        r'\b(?:machine learning|deep learning|natural language|data science|'
        r'power bi|google cloud|amazon web|software development|product management|'
        r'agile methodology|ci/cd|restful api|real-time|full stack|open source)\b',
        jd_text, re.IGNORECASE
    )

    single_words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b|\b[A-Z]{2,}\b', jd_text)

    keywords = set()

    for mw in multi_word:
        keywords.add(mw.title())

    for sw in single_words:
        if sw.lower() not in stop_words and len(sw) > 2:
            keywords.add(sw)

    skills = extract_skills(jd_text)
    keywords.update(skills)

    return list(keywords)[:30]


def _calculate_ats_optimization(
    resume_text: str,
    jd_text: str,
    jd_keywords: List[str],
) -> float:
    """Calculate how well the resume is optimized for ATS with this JD."""
    if not jd_keywords:
        return 0

    resume_lower = resume_text.lower()
    found = sum(1 for kw in jd_keywords if kw.lower() in resume_lower)
    base_score = (found / len(jd_keywords)) * 100

    first_half = resume_lower[:len(resume_lower)//2]
    prominent_count = sum(1 for kw in jd_keywords[:10] if kw.lower() in first_half)
    bonus = (prominent_count / min(10, len(jd_keywords))) * 15

    return round(min(base_score + bonus, 100), 1)


def _get_match_rating(score: float) -> Dict:
    """Get match rating label and color."""
    if score >= 80:
        return {"label": "Excellent Match", "color": "green", "emoji": "🟢"}
    elif score >= 65:
        return {"label": "Good Match", "color": "blue", "emoji": "🔵"}
    elif score >= 50:
        return {"label": "Moderate Match", "color": "orange", "emoji": "🟡"}
    elif score >= 35:
        return {"label": "Weak Match", "color": "red", "emoji": "🔴"}
    else:
        return {"label": "Poor Match", "color": "red", "emoji": "❌"}


def _generate_jd_recommendations(
    match_score: float,
    missing_keywords: List[str],
    missing_skills: List[str],
    profile: Dict,
) -> List[str]:
    """Generate resume improvement recommendations for this JD."""
    recs = []

    if missing_keywords:
        top_kws = ", ".join(missing_keywords[:4])
        recs.append(f"🔑 Add these JD keywords naturally to your resume: {top_kws}")

    if missing_skills:
        recs.append(f"⚡ Highlight or acquire: {', '.join(missing_skills[:3])}")

    if match_score < 60:
        recs.append("📝 Customize your summary/objective to mirror the JD's language")
        recs.append("🎯 Tailor your experience bullet points to match key JD requirements")

    if not profile.get("summary"):
        recs.append("✍️ Add a targeted professional summary that echoes the job description")

    recs.append("💡 Mirror exact phrases from the JD in your resume to beat ATS filters")
    recs.append("📊 Quantify your achievements with numbers that align with JD KPIs")

    return recs[:6]


def _ai_jd_analysis(profile: Dict, jd_text: str, base_result: Dict) -> Dict:
    """Use AI to provide deeper JD matching insights."""
    prompt = PROMPTS["jd_match"].format(
        name=profile.get('name', 'Candidate'),
        skills=', '.join(profile.get('skills', [])[:10]),
        projects=', '.join([p.get('title','') for p in profile.get('projects', [])[:3]]),
        base_score=base_result.get('overall_match_score', 0),
        jd_snippet=jd_text[:800]
    )

    schema = {
        "fit_assessment": str,
        "strong_fit_reasons": list,
        "concern_areas": list,
        "interview_talking_points": list,
        "resume_tailoring_tips": list
    }

    return generate_json(prompt, temperature=0.4, max_tokens=1000, schema=schema)
