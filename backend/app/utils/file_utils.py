from __future__ import annotations

import logging
import mimetypes
import os
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_file(
    file: UploadFile,
    max_size_mb: int = 50,
    allowed_extensions: list[str] | None = None,
) -> None:
    """Validate file size and extension. Raises HTTPException on failure."""
    ext = Path(file.filename or "").suffix.lower()
    allowed = allowed_extensions or settings.ALLOWED_EXTENSIONS

    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' not allowed. Supported: {', '.join(allowed)}",
        )


async def save_upload_file(file: UploadFile, document_id: str) -> Path:
    """Save an uploaded file to the local upload directory."""
    ext = Path(file.filename or "document").suffix
    filename = f"{document_id}{ext}"
    file_path = UPLOAD_DIR / filename

    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await out_file.write(chunk)

    logger.debug(f"Saved upload: {file_path}")
    return file_path
