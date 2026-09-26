"""
Auth router — DEMO MODE
Sign up / Sign in work with any credentials (mirrors the frontend mock behaviour).
Passwords are stored hashed but login accepts any password for demo ease.
"""
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import hash_password, create_access_token, get_current_user
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(body: schemas.UserRegister, db: Session = Depends(get_db)):
    # Demo: if email already exists just return that user (no duplicate error)
    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        token = create_access_token({"sub": existing.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(existing))

    user = models.User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        phone=body.phone,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/login", response_model=schemas.Token)
def login(body: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()

    # Demo: if user doesn't exist, auto-create them (like a mock login)
    if not user:
        name = body.email.split("@")[0].replace(".", " ").title()
        user = models.User(
            id=str(uuid.uuid4()),
            name=name,
            email=body.email,
            hashed_password=hash_password(body.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return schemas.Token(access_token=token, user=schemas.UserOut.model_validate(user))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserOut.model_validate(current_user)


@router.patch("/me", response_model=schemas.UserOut)
def update_profile(
    body: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.name is not None:
        current_user.name = body.name
    if body.phone is not None:
        current_user.phone = body.phone
    if body.avatar is not None:
        current_user.avatar = body.avatar
    db.commit()
    db.refresh(current_user)
    return schemas.UserOut.model_validate(current_user)
