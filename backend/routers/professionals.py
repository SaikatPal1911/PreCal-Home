import json
import uuid
import random
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/professionals", tags=["Professionals"])


def _serialize(p: models.Professional) -> schemas.ProfessionalOut:
    return schemas.ProfessionalOut(
        id=p.id,
        name=p.name,
        avatar=p.avatar,
        profession=p.profession,
        specialization=p.specialization,
        serviceArea=p.service_area,
        experience=p.experience,
        rating=p.rating,
        reviews=p.reviews,
        startingPrice=p.starting_price,
        consultationFee=p.consultation_fee,
        availability=p.availability,
        verified=p.verified,
        distance=p.distance,
        portfolio=json.loads(p.portfolio_json or "[]"),
        skills=json.loads(p.skills_json or "[]"),
        services=json.loads(p.services_json or "[]"),
        slots=json.loads(p.slots_json or "[]"),
        bio=p.bio,
    )


@router.get("/", response_model=List[schemas.ProfessionalOut])
def list_professionals(
    profession: Optional[str] = Query(None),
    availability: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    """List all professionals with optional filters."""
    q = db.query(models.Professional)
    if profession:
        q = q.filter(models.Professional.profession.ilike(f"%{profession}%"))
    if availability:
        q = q.filter(models.Professional.availability == availability)
    if min_rating is not None:
        q = q.filter(models.Professional.rating >= min_rating)
    return [_serialize(p) for p in q.all()]


@router.get("/{professional_id}", response_model=schemas.ProfessionalOut)
def get_professional(professional_id: str, db: Session = Depends(get_db)):
    p = db.query(models.Professional).filter(models.Professional.id == professional_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Professional not found")
    return _serialize(p)


def _gen_ref() -> str:
    return "PCH-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


@router.post("/book", response_model=schemas.BookingOut, status_code=status.HTTP_201_CREATED)
def book_professional(
    body: schemas.BookingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    professional = db.query(models.Professional).filter(models.Professional.id == body.professional_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    booking = models.Booking(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        professional_id=body.professional_id,
        customer_name=body.customer_name,
        phone=body.phone,
        location=body.location,
        category=body.category,
        date=body.date,
        time_slot=body.time_slot,
        requirements=body.requirements,
        reference_number=_gen_ref(),
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return schemas.BookingOut.model_validate(booking)


@router.get("/bookings/me", response_model=List[schemas.BookingOut])
def my_bookings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == current_user.id)
        .order_by(models.Booking.created_at.desc())
        .all()
    )
    return [schemas.BookingOut.model_validate(b) for b in bookings]
