"""
Behavioral Signal Scoring.
Extracts proxy signals for candidate activity and project depth
from parsed resume profile data. Used to enrich the final ranking.
"""
import re
from typing import Dict
from loguru import logger


def compute_signals(profile: dict) -> dict:
    """
    Extracts proxy signals for candidate activity and project depth from profile.
    """
    # github_present
    github_present = bool(profile.get("github"))

    # linkedin_present
    linkedin_present = bool(profile.get("linkedin"))

    # project_count
    projects = profile.get("projects") or []
    project_count = len(projects)

    # project_depth_score
    depth_pts = 0.0
    for p in projects:
        desc = p.get("description") or ""
        techs = p.get("technologies") or []
        if desc.strip() != "" and len(techs) >= 1:
            depth_pts += 20.0
    project_depth_score = min(depth_pts, 100.0)

    # skills_breadth_score
    skills = profile.get("skills") or []
    skill_count = len(skills)
    if skill_count <= 4:
        skills_breadth_score = 20.0
    elif skill_count <= 9:
        skills_breadth_score = 45.0
    elif skill_count <= 14:
        skills_breadth_score = 65.0
    elif skill_count <= 19:
        skills_breadth_score = 80.0
    else:
        skills_breadth_score = 100.0

    # quantification_score
    raw_text = profile.get("raw_text") or ""
    matches = re.findall(r'\d+%', raw_text)
    match_count = len(matches)
    if match_count == 0:
        quantification_score = 0.0
    elif match_count == 1:
        quantification_score = 30.0
    elif match_count == 2:
        quantification_score = 60.0
    else:
        quantification_score = 100.0

    # certifications_score
    certs = profile.get("certifications") or []
    cert_count = len(certs)
    if cert_count == 0:
        certifications_score = 0.0
    elif cert_count == 1:
        certifications_score = 40.0
    elif cert_count == 2:
        certifications_score = 70.0
    else:
        certifications_score = 100.0

    # composite_signal_score
    composite_signal_score = round(
        project_depth_score * 0.30 +
        skills_breadth_score * 0.25 +
        quantification_score * 0.25 +
        certifications_score * 0.20,
        1
    )

    return {
        "github_present": github_present,
        "linkedin_present": linkedin_present,
        "project_count": project_count,
        "project_depth_score": project_depth_score,
        "skills_breadth_score": skills_breadth_score,
        "quantification_score": quantification_score,
        "certifications_score": certifications_score,
        "composite_signal_score": composite_signal_score
    }


def fuse_scores(
    semantic_score: float,
    ats_score: float,
    signal_score: float,
) -> dict:
    """
    Fuses semantic score, ATS score, and behavioral signal score.
    """
    final_score = round(
        semantic_score * 0.50 +
        ats_score * 0.30 +
        signal_score * 0.20,
        1
    )
    
    score_breakdown = {
        "Semantic fit": round(semantic_score * 0.50, 1),
        "ATS quality": round(ats_score * 0.30, 1),
        "Behavioral signals": round(signal_score * 0.20, 1)
    }

    return {
        "final_score": final_score,
        "semantic_score": semantic_score,
        "ats_score": ats_score,
        "signal_score": signal_score,
        "score_breakdown": score_breakdown
    }
