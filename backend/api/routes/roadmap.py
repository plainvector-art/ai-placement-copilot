"""Roadmap generation API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.services.roadmap_gen import generate_roadmap
from backend.services.skill_analyzer import analyze_skill_gap

router = APIRouter()


class RoadmapRequest(BaseModel):
    session_id: str
    target_role: str
    hours_per_week: int = 10


@router.post("/generate")
async def create_roadmap(request: RoadmapRequest, db: Session = Depends(get_db)):
    """Generate a personalized learning roadmap."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    skill_gap = analyze_skill_gap(profile.get("skills", []), request.target_role)

    roadmap = generate_roadmap(
        profile, request.target_role, skill_gap, request.hours_per_week
    )

    crud.upsert_analysis(
        db, candidate.id, request.target_role,
        {"roadmap_data": roadmap},
    )

    return roadmap
