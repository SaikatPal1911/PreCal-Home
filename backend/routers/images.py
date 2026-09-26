import os
import uuid
import aiofiles
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user
from config import settings

router = APIRouter(prefix="/api/images", tags=["Images"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 10
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024


def _get_upload_dir() -> str:
    upload_dir = os.path.join(os.path.dirname(__file__), "..", settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.abspath(upload_dir)


@router.post("/upload", response_model=schemas.ImageUploadOut)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_TYPES}")

    contents = await file.read()

    # Validate size
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_SIZE_MB}MB")

    # Generate unique filename
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = _get_upload_dir()
    filepath = os.path.join(upload_dir, unique_name)

    # Save file
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    # Validate it's a real image using Pillow
    try:
        img = Image.open(filepath)
        img.verify()
    except Exception:
        os.remove(filepath)
        raise HTTPException(status_code=400, detail="Invalid or corrupt image file")

    url = f"/api/images/file/{unique_name}"

    # Save to DB (demo: user_id is None)
    record = models.UploadedImage(
        id=str(uuid.uuid4()),
        user_id=None,
        filename=file.filename or unique_name,
        filepath=filepath,
        url=url,
        content_type=file.content_type,
        size_bytes=len(contents),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return schemas.ImageUploadOut(
        id=record.id,
        filename=record.filename,
        url=url,
        content_type=record.content_type,
        size_bytes=record.size_bytes,
    )


@router.get("/file/{filename}")
def serve_image(filename: str):
    """Serve uploaded images by filename."""
    upload_dir = _get_upload_dir()
    filepath = os.path.join(upload_dir, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)


@router.get("/my", response_model=List[schemas.ImageUploadOut])
def my_images(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    images = (
        db.query(models.UploadedImage)
        .filter(models.UploadedImage.user_id == current_user.id)
        .order_by(models.UploadedImage.created_at.desc())
        .all()
    )
    return [
        schemas.ImageUploadOut(
            id=img.id, filename=img.filename, url=img.url,
            content_type=img.content_type, size_bytes=img.size_bytes
        )
        for img in images
    ]
