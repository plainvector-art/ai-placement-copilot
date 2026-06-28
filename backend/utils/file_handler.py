"""File handling utilities for uploads using system temporary directory."""
import os
import tempfile
import uuid
from pathlib import Path
from loguru import logger


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file to system temp disk with unique name.

    Returns:
        Absolute path to saved file
    """
    # Security check: file size limit (10MB)
    if len(file_content) > 10 * 1024 * 1024:
        raise ValueError("File size exceeds the maximum limit of 10MB.")

    ext = Path(filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".doc"):
        raise ValueError(f"Unsupported file format: {ext}. Only PDF, DOCX, and DOC are supported.")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(file_content)

    logger.info(f"Saved upload to temp: {file_path} ({len(file_content)/1024:.1f}KB)")
    return file_path


def cleanup_file(file_path: str) -> None:
    """Delete a file after processing."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not delete temp file {file_path}: {e}")
