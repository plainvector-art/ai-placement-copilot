"""Analytics dashboard data routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.services.skill_analyzer import get_available_roles

router = APIRouter()


@router.get("/roles")
async def analytics_roles():
    """Return all available roles for analytics."""
    return {"roles": get_available_roles()}


@router.get("/summary/{session_id}")
async def get_analytics_summary(session_id: str, db: Session = Depends(get_db)):
    """Get aggregated analytics for a candidate session."""
    candidate = crud.get_candidate_by_session(db, session_id)
    if not candidate:
        return {"error": "Profile not found"}

    return {
        "candidate": candidate.name,
        "total_analyses": len(candidate.analysis_results),
        "interview_sessions": len(candidate.interview_sessions),
    }
