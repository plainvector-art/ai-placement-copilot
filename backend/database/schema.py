"""
Database schema definitions using SQLAlchemy ORM.
Supports SQLite (default) and PostgreSQL (production).
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Candidate(Base):
    """Core candidate profile extracted from resume."""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    location = Column(String(200))
    linkedin = Column(String(300))
    github = Column(String(300))
    portfolio = Column(String(300))
    raw_text = Column(Text)
    structured_data = Column(JSON)           # Full parsed profile JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resume_uploads = relationship("ResumeUpload", back_populates="candidate")
    analysis_results = relationship("AnalysisResult", back_populates="candidate")
    interview_sessions = relationship("InterviewSession", back_populates="candidate")


class ResumeUpload(Base):
    """Tracks resume file uploads."""
    __tablename__ = "resume_uploads"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    filename = Column(String(300), nullable=False)
    file_type = Column(String(10))           # pdf | docx
    file_path = Column(String(500))
    file_size_kb = Column(Float)
    upload_status = Column(String(20), default="pending")  # pending|processing|done|error
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="resume_uploads")


class AnalysisResult(Base):
    """Stores all analysis results for a candidate."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    target_role = Column(String(100))
    ats_score = Column(Float)
    ats_breakdown = Column(JSON)             # Category scores dict
    skill_gap_data = Column(JSON)            # Missing, existing, coverage
    readiness_score = Column(Float)
    readiness_level = Column(String(30))     # Beginner|Developing|Ready|Competitive
    placement_components = Column(JSON)      # Component breakdown
    interview_questions = Column(JSON)       # Generated questions
    roadmap_data = Column(JSON)              # Learning roadmap
    jd_match_score = Column(Float)
    jd_match_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="analysis_results")


class InterviewSession(Base):
    """Tracks mock interview sessions."""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    session_type = Column(String(30))        # mock | practice
    target_role = Column(String(100))
    status = Column(String(20), default="active")  # active|completed|abandoned
    messages = Column(JSON, default=list)    # Chat history
    performance_scores = Column(JSON)        # Evaluation metrics
    feedback_report = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    candidate = relationship("Candidate", back_populates="interview_sessions")


class ChatHistory(Base):
    """Career coach chat history."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True)
    role = Column(String(20))                # user | assistant
    content = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class SkillTrend(Base):
    """Tracks skill trend data for market analysis."""
    __tablename__ = "skill_trends"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100))
    role = Column(String(100))
    demand_score = Column(Float)
    growth_rate = Column(Float)
    avg_salary_impact = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)
