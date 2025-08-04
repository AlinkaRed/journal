from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select

from db.base import SessionDep
from db.models import Group, Course, Faculty, Student


students_api_router = APIRouter(prefix='/api/students', tags=['Students API'])


@students_api_router.post("/", response_model=Student)
def create_student(student: Student, session: SessionDep):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


class StudentItem(BaseModel):
    id: int
    first_name: str
    middle_name: str | None
    last_name: str
    group: Group


class StudentDT(BaseModel):
    data: list[StudentItem]


@students_api_router.get("/", response_model=StudentDT)
def get_students(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    students = session.scalars(select(Student).join(Group).offset(offset).limit(limit))
    return {'data': students}


@students_api_router.get("/{student_id}", response_model=Student)
def get_student(student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@students_api_router.patch("/{student_id}", response_model=Student)
def update_student(student_id: int, student: Student, session: SessionDep):
    student_db = session.get(Student, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="Student not found")
    student_data = student.model_dump(exclude_unset=True)
    student_db.sqlmodel_update(student_data)
    session.add(student_db)
    session.commit()
    session.refresh(student_db)
    return student_db


@students_api_router.delete("/{student_id}")
def delete_student(student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    session.delete(student)
    session.commit()
    return {"ok": True}


@students_api_router.get("/random/", response_model=Student)
def get_random_student(session: SessionDep,
                       faculty_id: int = None,
                       course_id: int = None,
                       group_id: int = None):
    query = select(Student).join(Group).join(Course).join(Faculty)

    if faculty_id is not None:
        query = query.where(Faculty.id == faculty_id)
    if course_id is not None:
        query = query.where(Course.id == course_id)
    if group_id is not None:
        query = query.where(Group.id == group_id)

    s = session.scalars(query).all()

    if not s:
        raise HTTPException(status_code=404, detail="No students found")

    random_student = random.choice(s)
    return random_student
