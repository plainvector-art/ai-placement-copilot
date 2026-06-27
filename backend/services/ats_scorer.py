"""
ATS Resume Scoring Engine.
Evaluates resume quality across 6 dimensions and returns a score out of 100
with actionable improvement suggestions.
"""
import re
from typing import Dict, List, Tuple, Optional
from loguru import logger


# ── Scoring Weights (must sum to 100) ────────────────────────────────────────
WEIGHTS = {
    "skills": 25,
    "projects": 20,
    "experience": 20,
    "keywords": 15,
    "education": 10,
    "certifications": 10,
}

# ── ATS-Friendly Keywords by Category ────────────────────────────────────────
POWER_VERBS = [
    "achieved", "built", "created", "designed", "developed", "engineered",
    "implemented", "improved", "increased", "launched", "led", "managed",
    "optimized", "reduced", "scaled", "streamlined", "delivered", "deployed",
    "architected", "collaborated", "mentored", "automated", "analyzed",
    "orchestrated", "established", "integrated", "transformed",
]

QUANTIFICATION_PATTERNS = [
    r'\d+%', r'\$\d+', r'\d+x\b', r'\d+\+', r'\d+ (users|customers|clients|projects)',
    r'(increased|decreased|improved|reduced|saved|generated)\s+by\s+\d+',
]


def score_contact_info(profile: Dict) -> Tuple[int, List[str]]:
    """Score contact information completeness (0-100)."""
    suggestions = []
    score = 0

    if profile.get("email"):
        score += 30
    else:
        suggestions.append("Add a professional email address")

    if profile.get("phone"):
        score += 20
    else:
        suggestions.append("Add a phone number")

    if profile.get("linkedin"):
        score += 25
    else:
        suggestions.append("Add your LinkedIn profile URL to increase visibility")

    if profile.get("github"):
        score += 15
    else:
        suggestions.append("Add your GitHub profile URL to showcase your code")

    if profile.get("location"):
        score += 10
    else:
        suggestions.append("Add your city/location for ATS geographic filtering")

    return min(score, 100), suggestions


def score_skills(profile: Dict, target_role: Optional[str] = None) -> Tuple[int, List[str]]:
    """Score skills section (0-100)."""
    skills = profile.get("skills", [])
    suggestions = []
    score = 0

    if not skills:
        return 0, ["Add a dedicated Skills section with relevant technical skills"]

    # Count skills
    if len(skills) >= 10:
        score += 40
    elif len(skills) >= 6:
        score += 25
    elif len(skills) >= 3:
        score += 15
    else:
        suggestions.append("Add more relevant technical skills (aim for 10-15 skills)")

    # Check for categorization (inferred from having diverse skills)
    score += 30  # Presence bonus

    # Quantity bonus
    if len(skills) >= 15:
        score += 30
    elif len(skills) >= 10:
        score += 20
    elif len(skills) >= 5:
        score += 10
    else:
        suggestions.append("Expand your skills section with more relevant technologies")

    if len(skills) > 20:
        suggestions.append("Consider categorizing skills (Technical, Tools, Soft Skills)")

    return min(score, 100), suggestions


def score_experience(profile: Dict) -> Tuple[int, List[str]]:
    """Score experience section (0-100)."""
    experience = profile.get("experience", [])
    raw_text = profile.get("raw_text", "")
    suggestions = []
    score = 0

    if not experience:
        suggestions.append("Add work experience, internships, or volunteer work")
        return 0, suggestions

    score += 30  # Has experience entries

    # Check for quantification
    text_lower = raw_text.lower()
    quantified_count = sum(
        1 for pattern in QUANTIFICATION_PATTERNS
        if re.search(pattern, text_lower, re.IGNORECASE)
    )

    if quantified_count >= 3:
        score += 40
    elif quantified_count >= 1:
        score += 20
        suggestions.append("Quantify more achievements with numbers (e.g., 'improved performance by 40%')")
    else:
        suggestions.append("Add quantified achievements with metrics and numbers")

    # Check for action verbs
    verb_count = sum(1 for verb in POWER_VERBS if verb in text_lower)
    if verb_count >= 5:
        score += 30
    elif verb_count >= 3:
        score += 20
        suggestions.append("Use more strong action verbs (e.g., Led, Built, Optimized)")
    else:
        suggestions.append("Start bullet points with strong action verbs (Led, Built, Optimized, Delivered)")

    if len(experience) >= 2:
        score += 0  # Already counted
    else:
        suggestions.append("Add more experience entries including internships, freelance work, or academic projects")

    return min(score, 100), suggestions


def score_projects(profile: Dict) -> Tuple[int, List[str]]:
    """Score projects section (0-100)."""
    projects = profile.get("projects", [])
    suggestions = []
    score = 0

    if not projects:
        suggestions.append("Add a Projects section — crucial for ATS and recruiter screening")
        return 0, suggestions

    score += 30  # Has projects

    if len(projects) >= 3:
        score += 30
    elif len(projects) >= 2:
        score += 20
        suggestions.append("Add at least 3 projects to demonstrate breadth")
    else:
        suggestions.append("Add more projects (2-4 projects are ideal)")

    # Check if projects have technology mentions
    tech_mentioned = sum(1 for p in projects if p.get("technologies"))
    if tech_mentioned == len(projects):
        score += 25
    else:
        suggestions.append("Add technology stack to each project description")

    # Check for GitHub links
    has_links = any(
        "github" in str(p).lower() or "http" in str(p).lower()
        for p in projects
    )
    if has_links:
        score += 15
    else:
        suggestions.append("Add GitHub or live demo links to your projects")

    return min(score, 100), suggestions


def score_education(profile: Dict) -> Tuple[int, List[str]]:
    """Score education section (0-100)."""
    education = profile.get("education", [])
    suggestions = []
    score = 0

    if not education:
        suggestions.append("Add an Education section with your degree and institution")
        return 20, suggestions  # Give 20 for having any education

    score += 50  # Has education

    # Check for completeness
    for edu in education:
        if edu.get("year"):
            score += 20
            break
        else:
            suggestions.append("Add graduation year to your education entries")

    if any(edu.get("gpa") for edu in education):
        score += 15
    # GPA optional

    score += 15  # Standard bonus

    return min(score, 100), suggestions


def score_certifications(profile: Dict) -> Tuple[int, List[str]]:
    """Score certifications section (0-100)."""
    certs = profile.get("certifications", [])
    suggestions = []
    score = 0

    if not certs:
        suggestions.append("Add relevant certifications (AWS, Google Cloud, Coursera, etc.)")
        return 20, suggestions

    if len(certs) >= 3:
        score = 100
    elif len(certs) == 2:
        score = 75
        suggestions.append("Add 1-2 more certifications for a stronger profile")
    else:
        score = 50
        suggestions.append("Add more industry-recognized certifications")

    return score, suggestions


def score_keywords(profile: Dict, target_role: Optional[str] = None) -> Tuple[int, List[str]]:
    """Score keyword density and ATS optimization (0-100)."""
    raw_text = profile.get("raw_text", "").lower()
    suggestions = []
    score = 0

    # Check for section headers
    sections_found = []
    section_keywords = {
        "contact": ["email", "phone", "linkedin"],
        "education": ["education", "degree", "university", "college"],
        "experience": ["experience", "internship", "work history"],
        "skills": ["skills", "technologies", "technical skills"],
        "projects": ["projects", "portfolio"],
        "certifications": ["certifications", "certificates"],
    }

    for section, keywords in section_keywords.items():
        if any(kw in raw_text for kw in keywords):
            sections_found.append(section)

    section_score = (len(sections_found) / len(section_keywords)) * 60
    score += section_score

    if len(sections_found) < 5:
        missing = set(section_keywords.keys()) - set(sections_found)
        suggestions.append(f"Add missing sections: {', '.join(missing)}")

    # Check word count (ATS needs enough content)
    word_count = len(raw_text.split())
    if word_count >= 400:
        score += 25
    elif word_count >= 200:
        score += 15
        suggestions.append("Expand your resume content (aim for 400-600 words)")
    else:
        score += 5
        suggestions.append("Your resume is too brief. Add more detail to each section.")

    # Check for bullet points
    bullet_count = raw_text.count('•') + raw_text.count('·') + raw_text.count('-')
    if bullet_count >= 10:
        score += 15
    else:
        suggestions.append("Use bullet points to list responsibilities and achievements")

    return min(score, 100), suggestions


def calculate_ats_score(profile: Dict, target_role: Optional[str] = None) -> Dict:
    """
    Full ATS scoring engine.

    Returns:
        Complete scoring report with category scores and suggestions
    """
    logger.info(f"Calculating ATS score for: {profile.get('name', 'Unknown')}")

    # Score each category
    contact_score, contact_suggestions = score_contact_info(profile)
    skills_score, skills_suggestions = score_skills(profile, target_role)
    exp_score, exp_suggestions = score_experience(profile)
    proj_score, proj_suggestions = score_projects(profile)
    edu_score, edu_suggestions = score_education(profile)
    cert_score, cert_suggestions = score_certifications(profile)
    kw_score, kw_suggestions = score_keywords(profile, target_role)

    # Calculate weighted totals
    category_scores = {
        "skills": round(skills_score * WEIGHTS["skills"] / 100, 1),
        "projects": round(proj_score * WEIGHTS["projects"] / 100, 1),
        "experience": round(exp_score * WEIGHTS["experience"] / 100, 1),
        "keywords": round(kw_score * WEIGHTS["keywords"] / 100, 1),
        "education": round(edu_score * WEIGHTS["education"] / 100, 1),
        "certifications": round(cert_score * WEIGHTS["certifications"] / 100, 1),
    }

    overall_score = round(sum(category_scores.values()), 1)

    # Collect all suggestions, prioritized
    all_suggestions = (
        exp_suggestions + proj_suggestions + kw_suggestions +
        skills_suggestions + contact_suggestions +
        edu_suggestions + cert_suggestions
    )

    # Determine ATS rating
    if overall_score >= 80:
        rating = "Excellent"
        rating_color = "green"
    elif overall_score >= 65:
        rating = "Good"
        rating_color = "blue"
    elif overall_score >= 50:
        rating = "Fair"
        rating_color = "orange"
    else:
        rating = "Needs Improvement"
        rating_color = "red"

    result = {
        "overall_score": overall_score,
        "rating": rating,
        "rating_color": rating_color,
        "raw_scores": {
            "contact": contact_score,
            "skills": skills_score,
            "experience": exp_score,
            "projects": proj_score,
            "education": edu_score,
            "certifications": cert_score,
            "keywords": kw_score,
        },
        "weighted_scores": category_scores,
        "weights": WEIGHTS,
        "suggestions": all_suggestions[:10],  # Top 10 suggestions
        "stats": {
            "total_skills": len(profile.get("skills", [])),
            "total_projects": len(profile.get("projects", [])),
            "total_experience": len(profile.get("experience", [])),
            "total_certifications": len(profile.get("certifications", [])),
            "word_count": len(profile.get("raw_text", "").split()),
        }
    }

    logger.info(f"ATS Score: {overall_score}/100 ({rating})")
    return result
