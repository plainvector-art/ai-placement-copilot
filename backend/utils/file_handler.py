"""File handling utilities for uploads."""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from loguru import logger

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def ensure_upload_dir() -> Path:
    """Create upload directory if it doesn't exist."""
    upload_path = Path(UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded file to disk with unique name.

    Returns:
        Absolute path to saved file
    """
    upload_path = ensure_upload_dir()
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / unique_name

    with open(file_path, "wb") as f:
        f.write(file_content)

    logger.info(f"Saved upload: {file_path} ({len(file_content)/1024:.1f}KB)")
    return str(file_path)


def cleanup_file(file_path: str) -> None:
    """Delete a file after processing."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not delete file {file_path}: {e}")
