import json
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def _serialize(project: models.Project) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        category=project.category,
        thumbnail=project.thumbnail,
        budget=project.budget,
        result=json.loads(project.result_json),
        created_at=project.created_at,
    )


@router.get("/", response_model=List[schemas.ProjectOut])
def list_projects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = (
        db.query(models.Project)
        .filter(models.Project.user_id == current_user.id)
        .order_by(models.Project.created_at.desc())
        .all()
    )
    return [_serialize(p) for p in projects]


@router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = models.Project(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=body.name,
        category=body.category,
        thumbnail=body.thumbnail,
        budget=body.budget,
        result_json=json.dumps(body.result),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _serialize(project)


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(
    project_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _serialize(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
