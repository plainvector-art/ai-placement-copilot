"""Interview routes: question generation and mock interview."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.database import crud
from backend.services.interview_gen import generate_interview_questions
from backend.services.mock_interview import start_interview, process_response, evaluate_interview

router = APIRouter()


class QuestionGenRequest(BaseModel):
    session_id: str
    target_role: str
    difficulty: str = "Mixed"


class MockInterviewStartRequest(BaseModel):
    session_id: str
    target_role: str


class MockInterviewChatRequest(BaseModel):
    session_id: str
    interview_session: Dict
    user_response: str


class EvaluateRequest(BaseModel):
    session_id: str
    interview_session: Dict


@router.post("/generate")
async def generate_questions(
    request: QuestionGenRequest,
    db: Session = Depends(get_db),
):
    """Generate personalized interview questions."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    questions = generate_interview_questions(
        profile, request.target_role, request.difficulty
    )

    # Save
    crud.upsert_analysis(
        db, candidate.id, request.target_role,
        {"interview_questions": questions},
    )

    return questions


@router.post("/mock/start")
async def start_mock_interview(
    request: MockInterviewStartRequest,
    db: Session = Depends(get_db),
):
    """Initialize a new mock interview session."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    session = start_interview(profile, request.target_role)

    return session


@router.post("/mock/chat")
async def mock_interview_chat(request: MockInterviewChatRequest, db: Session = Depends(get_db)):
    """Process a user response in the mock interview."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    updated_session = process_response(
        request.interview_session,
        request.user_response,
        profile,
    )

    return updated_session


@router.post("/mock/evaluate")
async def evaluate_mock_interview(request: EvaluateRequest, db: Session = Depends(get_db)):
    """Evaluate completed mock interview and generate feedback report."""
    candidate = crud.get_candidate_by_session(db, request.session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile = candidate.structured_data
    evaluation = evaluate_interview(request.interview_session, profile)

    return evaluation
