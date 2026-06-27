"""File upload validation utilities."""
import os
from pathlib import Path
from typing import Tuple
from loguru import logger

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))


def validate_file(file_path: str, filename: str) -> Tuple[bool, str]:
    """
    Validate uploaded file type and size.

    Returns:
        (is_valid, error_message)
    """
    path = Path(file_path)
    ext = Path(filename).suffix.lower()

    # Check extension
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed. Only PDF and DOCX supported."

    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({size_mb:.1f}MB) exceeds {MAX_FILE_SIZE_MB}MB limit."

    # Check file is not empty
    if path.stat().st_size < 100:
        return False, "File appears to be empty or corrupt."

    return True, ""


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filename."""
    import re
    name = Path(filename).stem
    ext = Path(filename).suffix
    safe_name = re.sub(r'[^\w\-_]', '_', name)
    return f"{safe_name[:50]}{ext}"
