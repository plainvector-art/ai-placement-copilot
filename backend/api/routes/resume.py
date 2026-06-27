"""Resume upload and parsing API routes."""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from loguru import logger

from backend.database.db import get_db
from backend.database import crud
from backend.services.resume_parser import parse_resume
from backend.services.ats_scorer import calculate_ats_score
from backend.utils.file_handler import save_uploaded_file, cleanup_file
from backend.utils.validators import validate_file, sanitize_filename

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and parse a resume (PDF or DOCX).
    Returns structured candidate profile and ATS score.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read file content
    content = await file.read()
    filename = sanitize_filename(file.filename)

    # Save to disk
    file_path = save_uploaded_file(content, filename)

    try:
        # Validate
        is_valid, error = validate_file(file_path, filename)
        if not is_valid:
            cleanup_file(file_path)
            raise HTTPException(status_code=400, detail=error)

        # Parse resume
        profile = parse_resume(file_path)

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Save to database
        candidate = crud.create_candidate(db, session_id, profile)
        crud.create_resume_upload(
            db,
            candidate_id=candidate.id,
            filename=filename,
            file_type=profile.get("file_type", "pdf"),
            file_path=file_path,
            file_size_kb=len(content) / 1024,
        )

        # Calculate initial ATS score
        ats_result = calculate_ats_score(profile)

        return {
            "success": True,
            "session_id": session_id,
            "candidate_id": candidate.id,
            "profile": profile,
            "ats_score": ats_result,
            "message": f"Resume parsed successfully for {profile.get('name', 'candidate')}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume parsing failed: {e}")
        cleanup_file(file_path)
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
    finally:
        # Keep file for potential re-analysis, cleanup is optional
        pass


@router.get("/{session_id}/profile")
async def get_profile(session_id: str, db: Session = Depends(get_db)):
    """Get candidate profile by session ID."""
    candidate = crud.get_candidate_by_session(db, session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found")
    return candidate.structured_data


@router.get("/{session_id}/ats-score")
async def get_ats_score(
    session_id: str,
    target_role: str = None,
    db: Session = Depends(get_db),
):
    """Get ATS score for a resume."""
    candidate = crud.get_candidate_by_session(db, session_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = candidate.structured_data
    result = calculate_ats_score(profile, target_role)
    return result
