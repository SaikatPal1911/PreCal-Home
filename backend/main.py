"""
PreCal Home – FastAPI Backend
Run with: uvicorn main:app --reload --port 8000
Docs at:  http://localhost:8000/docs
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine
import models
from routers import auth, analysis, projects, professionals, images
from seed import seed
from config import settings

# Create all DB tables on startup
models.Base.metadata.create_all(bind=engine)

# Seed professionals if not present
seed()

app = FastAPI(
    title="PreCal Home API",
    description="Backend API for the PreCal Home renovation analysis platform",
    version="1.0.0",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ROUTERS ─────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(projects.router)
app.include_router(professionals.router)
app.include_router(images.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "PreCal Home API is running 🏠"}


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "healthy", "version": "1.0.0"}
