from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select

from db.base import SessionDep
from db.models import Teacher


teachers_api_router = APIRouter(prefix='/api/teachers', tags=['Teachers API'])


@teachers_api_router.post("/", response_model=Teacher)
def create_teacher(teacher: Teacher, session: SessionDep):
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


class teacherItem(BaseModel):
    id: int
    first_name: str
    middle_name: str | None
    last_name: str


class teacherDT(BaseModel):
    data: list[teacherItem]


@teachers_api_router.get("/", response_model=teacherDT)
def get_teachers(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    teachers = session.scalars(select(Teacher).offset(offset).limit(limit))
    return {'data': teachers}


@teachers_api_router.get("/{teacher_id}", response_model=Teacher)
def get_teacher(teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="teacher not found")
    return teacher


@teachers_api_router.patch("/{teacher_id}", response_model=Teacher)
def update_teacher(teacher_id: int, teacher: Teacher, session: SessionDep):
    teacher_db = session.get(Teacher, teacher_id)
    if not teacher_db:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher_data = teacher.model_dump(exclude_unset=True)
    teacher_db.sqlmodel_update(teacher_data)
    session.add(teacher_db)
    session.commit()
    session.refresh(teacher_db)
    return teacher_db


@teachers_api_router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="teacher not found")
    session.delete(teacher)
    session.commit()
    return {"ok": True}

