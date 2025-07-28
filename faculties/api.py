from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select

from db.base import SessionDep
from db.models import Faculty


faculties_api_router = APIRouter(prefix='/api/faculties', tags=['Faculties API'])


@faculties_api_router.post("/", response_model=Faculty)
def create_faculty(request: Request, faculty: Faculty, session: SessionDep):
    session.add(faculty)
    session.commit()
    session.refresh(faculty)
    return faculty


class FacultiesDT(BaseModel):
    data: list[Faculty]


@faculties_api_router.get("/", response_model=FacultiesDT)
def get_faculties(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    faculties = session.scalars(select(Faculty).offset(offset).limit(limit)).all()
    return {'data': faculties}


@faculties_api_router.get("/{faculty_id}", response_model=Faculty)
def get_faculty(faculty_id: int, session: SessionDep):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty


@faculties_api_router.patch("/{faculty_id}", response_model=Faculty)
def update_faculty(faculty_id: int, faculty: Faculty, session: SessionDep):
    faculty_db = session.get(Faculty, faculty_id)
    if not faculty_db:
        raise HTTPException(status_code=404, detail="Faculty not found")
    faculty_data = faculty.model_dump(exclude_unset=True)
    faculty_db.sqlmodel_update(faculty_data)
    session.add(faculty_db)
    session.commit()
    session.refresh(faculty_db)
    return faculty_db


@faculties_api_router.delete("/{faculty_id}")
def delete_faculty(faculty_id: int, session: SessionDep):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    session.delete(faculty)
    session.commit()
    return {"ok": True}


@faculties_api_router.get("/random/", response_model=Faculty)
def get_faculty_random(session: SessionDep):
    f = session.scalars(select(Faculty)).all()

    if not f:
        raise HTTPException(status_code=404, detail="No faculties found")

    random_faculty = random.choice(f)
    return random_faculty
