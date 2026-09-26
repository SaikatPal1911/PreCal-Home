import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    budget = Column(Float, nullable=True)
    result_json = Column(Text, nullable=False)   # full AnalysisResult stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    profession = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    service_area = Column(String, nullable=False)
    experience = Column(Integer, nullable=False)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    starting_price = Column(Float, nullable=False)
    consultation_fee = Column(Float, default=0.0)
    availability = Column(String, default="Available")   # Available | Busy | Limited
    verified = Column(Boolean, default=False)
    distance = Column(Float, nullable=True)
    portfolio_json = Column(Text, default="[]")
    skills_json = Column(Text, default="[]")
    services_json = Column(Text, default="[]")
    slots_json = Column(Text, default="[]")
    bio = Column(Text, nullable=True)

    bookings = relationship("Booking", back_populates="professional", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    professional_id = Column(String, ForeignKey("professionals.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    location = Column(String, nullable=False)
    category = Column(String, nullable=True)
    date = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)
    requirements = Column(Text, nullable=True)
    reference_number = Column(String, unique=True, nullable=False)
    status = Column(String, default="confirmed")   # confirmed | cancelled | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    professional = relationship("Professional", back_populates="bookings")


class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
