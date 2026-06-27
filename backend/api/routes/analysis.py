"""Analysis routes: skill gap, readiness score."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.services.skill_analyzer import analyze_skill_gap, get_available_roles
from backend.services.readiness_scorer import calculate_readiness_score
from backend.services.ats_scorer import calculate_ats_score

router = APIRouter()


class SkillGapRequest(BaseModel):
    session_id: str
    target_role: str


class ReadinessRequest(BaseModel):
    session_id: str
    target_role: str
    interview_score: Optional[float] = None


@router.post("/skill-gap")
async def skill_gap_analysis(
    request: SkillGapRequest,
    db: Session = Depends(get_db),
):
    """Perform skill gap analysis for a target role."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found. Please upload resume first.")

    profile = candidate.structured_data
    skills = profile.get("skills", [])

    result = analyze_skill_gap(skills, request.target_role)

    # Save to database
    crud.upsert_analysis(
        db,
        candidate.id,
        request.target_role,
        {"skill_gap_data": result},
    )

    return result


@router.post("/readiness")
async def placement_readiness(
    request: ReadinessRequest,
    db: Session = Depends(get_db),
):
    """Calculate placement readiness score."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data

    # Get or calculate ATS score
    ats_result = calculate_ats_score(profile)
    ats_score = ats_result.get("overall_score", 50)

    # Get skill gap data
    skill_gap = analyze_skill_gap(profile.get("skills", []), request.target_role)

    # Calculate readiness
    result = calculate_readiness_score(
        ats_score, skill_gap, profile, request.interview_score
    )

    # Save
    crud.upsert_analysis(
        db,
        candidate.id,
        request.target_role,
        {
            "readiness_score": result["overall_score"],
            "readiness_level": result["level"],
            "placement_components": result["components"],
        },
    )

    return result


@router.get("/roles")
async def get_roles():
    """Get list of all available target roles."""
    return {"roles": get_available_roles()}
