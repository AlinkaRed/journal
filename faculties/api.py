from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy import exists
from sqlalchemy import delete

from db.base import SessionDep
from db.models import Faculty, Course, Student, Group


faculties_api_router = APIRouter(prefix='/api/faculties', tags=['Faculties API'])


@faculties_api_router.post("/", response_model=Faculty)
def create_faculty(request: Request, faculty: Faculty, session: SessionDep):
    errors = {}

    name_exists = session.query(
        exists().where(Faculty.name == faculty.name)
    ).scalar()

    num_exists = session.query(
        exists().where(Faculty.num == faculty.num)
    ).scalar()

    if name_exists:
        errors["name"] = "Факультет с таким названием уже существует"

    if num_exists:
        errors["num"] = "Факультет с таким номером уже существует"

    if int(faculty.num) < 0:
        errors["num"] = "Номер факультета не может быть отрицательным"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {"name": faculty.name, "num": faculty.num},
            }
        )

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
    errors = {}

    faculty_db = session.get(Faculty, faculty_id)
    if not faculty_db:
        raise HTTPException(status_code=404, detail="Faculty not found")

    if faculty.name is not None:
        if faculty.name != faculty_db.name:
            name_exists = session.query(
                exists().where(Faculty.name == faculty.name)
            ).scalar()
            if name_exists:
                errors["name"] = "Факультет с таким названием уже существует"

    if faculty.num is not None:
        if faculty.num != faculty_db.num:
            num_exists = session.query(
                exists().where(Faculty.num == faculty.num)
            ).scalar()
            if num_exists:
                errors["num"] = "Факультет с таким номером уже существует"
        if faculty.num < 0:
            errors["num"] = "Номер факультета не может быть отрицательным"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {
                    "name": faculty.name if faculty.name is not None else faculty_db.name,
                    "num": faculty.num if faculty.num is not None else faculty_db.num
                },
            }
        )

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

    course_ids = [course.id for course in faculty.courses]

    if course_ids:
        for i in course_ids:
            course = session.get(Course, i)
            group_ids = [group.id for group in course.groups]
            session.execute(
                delete(Student).where(Student.groups_id.in_(group_ids))
            )

            session.execute(
                delete(Group).where(Group.course_id == i)
            )
        session.execute(
            delete(Course).where(Course.faculty_id == faculty_id)
        )

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
