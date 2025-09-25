from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy import delete
from sqlalchemy import exists, and_

from db.base import SessionDep
from db.models import Course, Faculty, Group, Student


courses_api_router = APIRouter(prefix='/api/courses', tags=['Courses API'])


@courses_api_router.post("/", response_model=Course)
def create_course(course: Course, session: SessionDep):
    errors = {}

    course_exists = session.query(
        exists().where(and_(
            Course.num == course.num,
            Course.faculty_id == course.faculty_id
        ))
    ).scalar()

    if course_exists:
        errors["num"] = "Курс с таким номером уже существует для этого факультета"
        errors["faculty_id"] = "Выберите другой факультет или измените номер курса"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {"num": course.num, "faculty_id": course.faculty_id},
            }
        )

    session.add(course)
    session.commit()
    session.refresh(course)
    return course


class CourseItem(BaseModel):
    id: int
    num: int
    faculty: Faculty


class CoursesDT(BaseModel):
    data: list[CourseItem]


@courses_api_router.get("/", response_model=CoursesDT)
def get_courses(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    courses = session.scalars(select(Course).join(Faculty).offset(offset).limit(limit))
    return {'data': courses}


@courses_api_router.get("/{course_id}/", response_model=Course)
def get_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@courses_api_router.patch("/{course_id}/", response_model=Course)
def update_course(course_id: int, course: Course, session: SessionDep):
    errors = {}

    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.num and course.faculty_id is not None:
        if course.num != course_db.num and course.faculty_id != course_db.faculty_id:
            course_exists = session.query(
                exists().where(and_(
                    Course.num == course.num,
                    Course.faculty_id == course.faculty_id
                ))
            ).scalar()

            if course_exists:
                errors["num"] = "Курс с таким номером уже существует для этого факультета"
                errors["faculty_id"] = "Выберите другой факультет или измените номер курса"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {
                    "num": course.num if course.num is not None else course_db.num,
                    "faculty_id": course.faculty_id if course.faculty_id is not None else course_db.faculty_id,
                },
            }
        )

    course_data = course.model_dump(exclude_unset=True)
    course_db.sqlmodel_update(course_data)
    session.add(course_db)
    session.commit()
    session.refresh(course_db)
    return course_db


@courses_api_router.delete("/{course_id}/")
def delete_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    group_ids = [group.id for group in course.groups]

    if group_ids:
        session.execute(
            delete(Student).where(Student.groups_id.in_(group_ids))
        )

        session.execute(
            delete(Group).where(Group.course_id == course_id)
        )

    session.delete(course)
    session.commit()

    return {"ok": True}


@courses_api_router.get("/random/", response_model=Course)
def get_faculty_random(session: SessionDep):
    f = session.scalars(select(Course)).all()

    if not f:
        raise HTTPException(status_code=404, detail="No courses found")

    random_course = random.choice(f)
    return random_course