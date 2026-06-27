"""Career coaching routes: JD match, coach chat, projects, cover letter."""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.services.career_coach import (
    chat_with_coach, generate_cover_letter,
    generate_linkedin_headline, predict_career_path, estimate_salary
)
from backend.services.jd_matcher import calculate_jd_match
from backend.services.project_recommender import recommend_projects

router = APIRouter()


class CoachChatRequest(BaseModel):
    session_id: str
    message: str
    target_role: str
    chat_history: List[Dict] = []


class JDMatchRequest(BaseModel):
    session_id: str
    job_description: str


class CoverLetterRequest(BaseModel):
    session_id: str
    target_role: str
    company_name: str = ""
    job_description: str = ""


class LinkedInRequest(BaseModel):
    session_id: str
    target_role: str


class ProjectsRequest(BaseModel):
    session_id: str
    target_role: str


@router.post("/coach")
async def career_coach_chat(request: CoachChatRequest, db: Session = Depends(get_db)):
    """Chat with AI career coach."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    response = chat_with_coach(
        request.message, profile, request.target_role, request.chat_history
    )

    # Save to chat history
    crud.add_chat_message(db, request.session_id, "user", request.message)
    crud.add_chat_message(db, request.session_id, "assistant", response)

    return {"response": response}


@router.post("/jd-match")
async def jd_match(request: JDMatchRequest, db: Session = Depends(get_db)):
    """Match resume against job description."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    result = calculate_jd_match(profile, request.job_description)

    crud.upsert_analysis(
        db, candidate.id, "JD Match",
        {"jd_match_score": result.get("overall_match_score"), "jd_match_data": result},
    )

    return result


@router.post("/cover-letter")
async def cover_letter(request: CoverLetterRequest, db: Session = Depends(get_db)):
    """Generate a personalized cover letter."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    letter = generate_cover_letter(
        profile, request.target_role, request.company_name, request.job_description
    )

    return {"cover_letter": letter}


@router.post("/linkedin")
async def linkedin_profile(request: LinkedInRequest, db: Session = Depends(get_db)):
    """Generate LinkedIn headline and About section."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    result = generate_linkedin_headline(profile, request.target_role)

    return result


@router.post("/projects")
async def project_recommendations(request: ProjectsRequest, db: Session = Depends(get_db)):
    """Get personalized project recommendations."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    result = recommend_projects(profile, request.target_role)

    return result


@router.post("/salary")
async def salary_estimate(
    request: LinkedInRequest,
    location: str = "US",
    db: Session = Depends(get_db),
):
    """Estimate salary range for target role."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    result = estimate_salary(profile, request.target_role, location)

    return result
