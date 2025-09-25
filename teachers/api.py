from typing import Annotated
import random
from datetime import date

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy import exists

from db.base import SessionDep
from db.models import Teacher


teachers_api_router = APIRouter(prefix='/api/teachers', tags=['Teachers API'])


@teachers_api_router.post("/", response_model=Teacher)
def create_teacher(teacher: Teacher, session: SessionDep):
    errors = {}

    inn_exists = session.query(
        exists().where(Teacher.inn == teacher.inn)
    ).scalar()

    if inn_exists:
        errors["inn"] = "Преподаватель с таким ИНН уже существует"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {"first_name": teacher.first_name,
                              "middle_name": teacher.middle_name,
                              "last_name": teacher.middle_name,
                              "date_of_birth": teacher.date_of_birth,
                              "inn": teacher.inn},
            }
        )

    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


class teacherItem(BaseModel):
    id: int
    first_name: str
    middle_name: str | None
    last_name: str
    date_of_birth: str
    inn: int


class teacherDT(BaseModel):
    data: list[teacherItem]


@teachers_api_router.get("/", response_model=teacherDT)
def get_teachers(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    teachers = session.scalars(select(Teacher).offset(offset).limit(limit))

    teachers_list = []
    for teacher in teachers:
        teacher_dict = teacher.__dict__.copy()
        if isinstance(teacher_dict.get('date_of_birth'), date):
            teacher_dict['date_of_birth'] = teacher_dict['date_of_birth'].isoformat()
        teachers_list.append(teacher_dict)

    return {'data': teachers_list}


@teachers_api_router.get("/{teacher_id}", response_model=Teacher)
def get_teacher(teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="teacher not found")
    return teacher


@teachers_api_router.patch("/{teacher_id}", response_model=Teacher)
def update_teacher(teacher_id: int, teacher: Teacher, session: SessionDep):
    errors = {}

    teacher_db = session.get(Teacher, teacher_id)
    if not teacher_db:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.inn is not None:
        if teacher.inn != teacher_db.inn:
            inn_exists = session.query(
                exists().where(Teacher.inn == teacher.inn)
            ).scalar()

            if inn_exists:
                errors["inn"] = "Преподаватель с таким ИНН уже существует"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {
                    "first_name": teacher.first_name if teacher.first_name is not None else teacher_db.first_name,
                    "middle_name": teacher.middle_name if teacher.middle_name is not None else teacher_db.middle_name,
                    "last_name": teacher.last_name if teacher.last_name is not None else teacher_db.last_name,
                    "date_of_birth": teacher.date_of_birth if teacher.date_of_birth is not None else teacher_db.date_of_birth,
                    "inn": teacher.inn if teacher.inn is not None else teacher_db.inn
                },
            }
        )

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

