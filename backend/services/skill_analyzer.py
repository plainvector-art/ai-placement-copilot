"""
Skill Gap Analysis Service.
Compares candidate skills against role requirements from the roles database.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger


def _load_roles_db() -> Dict:
    """Load roles database from JSON file."""
    roles_path = Path(__file__).parent.parent / "data" / "roles.json"
    with open(roles_path, "r") as f:
        return json.load(f)["roles"]


def _normalize_skill(skill: str) -> str:
    """Normalize skill string for comparison."""
    return skill.lower().strip().replace("-", " ").replace("_", " ")


def analyze_skill_gap(
    candidate_skills: List[str],
    target_role: str,
) -> Dict:
    """
    Perform skill gap analysis for a target role.

    Args:
        candidate_skills: List of skills from resume
        target_role: Target job role name

    Returns:
        Comprehensive skill gap analysis
    """
    roles_db = _load_roles_db()

    if target_role not in roles_db:
        available = list(roles_db.keys())
        logger.warning(f"Role '{target_role}' not found. Available: {available}")
        return {
            "error": f"Role '{target_role}' not found",
            "available_roles": available,
        }

    role_data = roles_db[target_role]
    required_skills = role_data["required_skills"]
    preferred_skills = role_data.get("preferred_skills", [])
    core_skills = role_data.get("core_skills", [])

    # Normalize for comparison
    candidate_normalized = {_normalize_skill(s) for s in candidate_skills}
    required_normalized = [_normalize_skill(s) for s in required_skills]
    preferred_normalized = [_normalize_skill(s) for s in preferred_skills]

    # Find matching and missing skills
    matched_required = []
    missing_required = []
    for i, skill_norm in enumerate(required_normalized):
        # Check if any candidate skill contains or matches this skill
        is_match = any(
            skill_norm in cand_skill or cand_skill in skill_norm
            for cand_skill in candidate_normalized
        )
        if is_match:
            matched_required.append(required_skills[i])
        else:
            missing_required.append(required_skills[i])

    matched_preferred = []
    missing_preferred = []
    for i, skill_norm in enumerate(preferred_normalized):
        is_match = any(
            skill_norm in cand_skill or cand_skill in skill_norm
            for cand_skill in candidate_normalized
        )
        if is_match:
            matched_preferred.append(preferred_skills[i])
        else:
            missing_preferred.append(preferred_skills[i])

    # Core skill check
    missing_core = [
        s for s in core_skills
        if not any(
            _normalize_skill(s) in cand or cand in _normalize_skill(s)
            for cand in candidate_normalized
        )
    ]

    # Coverage metrics
    required_coverage = (
        len(matched_required) / len(required_skills) * 100
        if required_skills else 0
    )
    preferred_coverage = (
        len(matched_preferred) / len(preferred_skills) * 100
        if preferred_skills else 0
    )
    overall_coverage = (required_coverage * 0.7 + preferred_coverage * 0.3)

    # Priority ranking for missing skills
    priority_skills = _rank_priority_skills(
        missing_required, missing_core, role_data
    )

    # Skill strength assessment
    skill_strength = _assess_skill_strength(required_coverage)

    return {
        "target_role": target_role,
        "role_description": role_data.get("description", ""),
        "avg_salary": role_data.get("avg_salary", ""),
        "market_growth": role_data.get("growth", ""),
        "matched_skills": matched_required,
        "missing_skills": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred[:8],  # Show top 8
        "core_skills": core_skills,
        "missing_core_skills": missing_core,
        "coverage": {
            "required": round(required_coverage, 1),
            "preferred": round(preferred_coverage, 1),
            "overall": round(overall_coverage, 1),
        },
        "priority_skills": priority_skills[:6],
        "skill_strength": skill_strength,
        "recommended_certifications": role_data.get("certifications", []),
        "total_required": len(required_skills),
        "total_matched": len(matched_required),
        "candidate_skill_count": len(candidate_skills),
    }


def _rank_priority_skills(
    missing_required: List[str],
    missing_core: List[str],
    role_data: Dict,
) -> List[Dict]:
    """Rank missing skills by priority (core first, then required)."""
    priority = []
    core_set = {_normalize_skill(s) for s in missing_core}

    for skill in missing_required:
        is_core = _normalize_skill(skill) in core_set
        priority.append({
            "skill": skill,
            "priority": "Critical" if is_core else "High",
            "reason": "Core skill for this role" if is_core else "Required skill",
            "learn_time": _estimate_learn_time(skill),
        })

    # Sort: Critical first
    priority.sort(key=lambda x: 0 if x["priority"] == "Critical" else 1)
    return priority


def _estimate_learn_time(skill: str) -> str:
    """Rough learning time estimate for a skill."""
    complex_skills = {
        "machine learning", "deep learning", "kubernetes", "terraform",
        "spark", "distributed systems", "fpga", "verilog",
    }
    medium_skills = {
        "docker", "fastapi", "react", "node.js", "sql", "tableau",
        "power bi", "scikit-learn", "pandas", "mlflow",
    }

    skill_lower = skill.lower()
    if any(cs in skill_lower for cs in complex_skills):
        return "3-6 months"
    elif any(ms in skill_lower for ms in medium_skills):
        return "4-8 weeks"
    else:
        return "2-4 weeks"


def _assess_skill_strength(coverage: float) -> Dict:
    """Assess overall skill strength level."""
    if coverage >= 80:
        return {
            "level": "Strong",
            "color": "green",
            "message": "You have most required skills for this role.",
        }
    elif coverage >= 60:
        return {
            "level": "Good",
            "color": "blue",
            "message": "You have a solid foundation. Focus on the missing core skills.",
        }
    elif coverage >= 40:
        return {
            "level": "Developing",
            "color": "orange",
            "message": "Build the missing skills with a structured 3-month plan.",
        }
    else:
        return {
            "level": "Beginner",
            "color": "red",
            "message": "Start with the core skills and build a strong foundation.",
        }


def get_available_roles() -> List[str]:
    """Return list of all available target roles."""
    return list(_load_roles_db().keys())


def get_role_info(role: str) -> Optional[Dict]:
    """Get detailed role information."""
    roles_db = _load_roles_db()
    return roles_db.get(role)
