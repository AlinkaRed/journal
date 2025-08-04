from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select

from db.base import SessionDep
from db.models import Course, Faculty


courses_api_router = APIRouter(prefix='/api/courses', tags=['Courses API'])


@courses_api_router.post("/", response_model=Course)
def create_course(course: Course, session: SessionDep):
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
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
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