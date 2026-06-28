"""
CRUD operations for all database models.
"""
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.database.schema import (
    Candidate, ResumeUpload, AnalysisResult,
    InterviewSession, ChatHistory
)


# ── Candidate ─────────────────────────────────────────────────────────────────

def get_candidate_by_session(db: Session, session_id: str) -> Optional[Candidate]:
    return db.query(Candidate).filter(Candidate.session_id == session_id).first()


def create_candidate(db: Session, session_id: str, structured_data: Dict) -> Candidate:
    candidate = Candidate(
        session_id=session_id,
        name=structured_data.get("name"),
        email=structured_data.get("email"),
        phone=structured_data.get("phone"),
        location=structured_data.get("location"),
        linkedin=structured_data.get("linkedin"),
        github=structured_data.get("github"),
        structured_data=structured_data,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def update_candidate(db: Session, candidate: Candidate, data: Dict) -> Candidate:
    for key, value in data.items():
        if hasattr(candidate, key):
            setattr(candidate, key, value)
    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)
    return candidate


# ── Resume Upload ──────────────────────────────────────────────────────────────

def create_resume_upload(
    db: Session,
    candidate_id: int,
    filename: str,
    file_type: str,
    file_path: str,
    file_size_kb: float,
) -> ResumeUpload:
    upload = ResumeUpload(
        candidate_id=candidate_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        file_size_kb=file_size_kb,
        upload_status="done",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


# ── Analysis Results ───────────────────────────────────────────────────────────

def get_analysis_by_candidate(
    db: Session, candidate_id: int, target_role: str
) -> Optional[AnalysisResult]:
    return (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.candidate_id == candidate_id,
            AnalysisResult.target_role == target_role,
        )
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )


def upsert_analysis(
    db: Session,
    candidate_id: int,
    target_role: str,
    data: Dict,
) -> AnalysisResult:
    existing = get_analysis_by_candidate(db, candidate_id, target_role)
    if existing:
        for key, value in data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        result = AnalysisResult(
            candidate_id=candidate_id,
            target_role=target_role,
            **data,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result


# ── Interview Sessions ─────────────────────────────────────────────────────────

def create_interview_session(
    db: Session, candidate_id: int, target_role: str, session_type: str = "mock"
) -> InterviewSession:
    session = InterviewSession(
        candidate_id=candidate_id,
        target_role=target_role,
        session_type=session_type,
        messages=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_interview_session(
    db: Session, session_id: int, messages: List, scores: Optional[Dict] = None
) -> Optional[InterviewSession]:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if session:
        session.messages = messages
        if scores:
            session.performance_scores = scores
        db.commit()
        db.refresh(session)
    return session


# ── Chat History ───────────────────────────────────────────────────────────────

def add_chat_message(
    db: Session, session_id: str, role: str, content: str, metadata: Optional[Dict] = None
) -> ChatHistory:
    msg = ChatHistory(
        session_id=session_id,
        role=role,
        content=content,
        meta_info=metadata or {},
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(db: Session, session_id: str, limit: int = 50) -> List[ChatHistory]:
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .limit(limit)
        .all()
    )
