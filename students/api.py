from typing import Annotated, Optional
import random
from datetime import date

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy import exists

from db.base import SessionDep
from db.models import Group, Course, Faculty, Student


students_api_router = APIRouter(prefix='/api/students', tags=['Students API'])


@students_api_router.post("/", response_model=Student)
def create_student(student: Student, session: SessionDep):
    errors = {}

    inn_exists = session.query(
        exists().where(Student.inn == student.inn)
    ).scalar()

    if inn_exists:
        errors["inn"] = "Студент с таким ИНН уже существует"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {"first_name": student.first_name,
                              "middle_name": student.middle_name,
                              "last_name": student.last_name,
                              "date_of_birth": student.date_of_birth,
                              "inn": student.inn,
                              "gender": student.gender,
                              "groups_id": student.groups_id},
            }
        )

    session.add(student)
    session.commit()
    session.refresh(student)
    return student


class StudentItem(BaseModel):
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: str
    inn: int
    gender: Optional[str] = None
    group: Optional[dict] = None


class StudentDT(BaseModel):
    data: list[StudentItem]


@students_api_router.get("/", response_model=StudentDT)
def get_students(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
):
    statement = select(Student).join(Group, isouter=True).offset(offset).limit(limit)
    students = session.exec(statement).all()

    students_list = []
    for student in students:
        student_data = {
            "id": student.id,
            "first_name": student.first_name,
            "middle_name": student.middle_name,
            "last_name": student.last_name,
            "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else "",
            "inn": student.inn,
            "gender": student.gender,
            "group": {
                "id": student.group.id if student.group else None,
                "num": student.group.num if student.group else "Не указана"
            } if student.group else None
        }
        students_list.append(student_data)

    return {'data': students_list}


@students_api_router.get("/{student_id}", response_model=Student)
def get_student(student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@students_api_router.patch("/{student_id}", response_model=Student)
def update_student(student_id: int, student_data: dict, session: SessionDep):
    errors = {}

    student_db = session.get(Student, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="Student not found")

    if student_data.get('inn') is not None:
        if student_data['inn'] != student_db.inn:
            inn_exists = session.query(
                exists().where(Student.inn == student_data['inn'])
            ).scalar()

            if inn_exists:
                errors["inn"] = "Студент с таким ИНН уже существует"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
            }
        )

    for key, value in student_data.items():
        if hasattr(student_db, key) and value is not None:
            setattr(student_db, key, value)

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