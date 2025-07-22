from typing import Annotated
import random
from fastapi import FastAPI, HTTPException, Query, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy import func

from db import (
    Course,
    Faculty,
    Group,
    Student,
    Teacher,
    SessionDep,
)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")

router = APIRouter()


# @app.get("/")
# def root(response_class=HTMLResponse):
#     return FileResponse("templates/index.html")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )


# --------------------------------Faculties---------------------------------------------

@app.get("/faculties/", response_class=HTMLResponse)
def faculties(request: Request):
    return templates.TemplateResponse(
        request=request, name="faculties.html", context={}
    )


@router.post("/faculty/", response_model=Faculty)
def create_faculty(request: Request, faculty: Faculty, session: SessionDep):
    session.add(faculty)
    session.commit()
    session.refresh(faculty)
    return faculty


class FacultiesDT(BaseModel):
    data: list[Faculty]


@router.get("/faculties/", response_model=FacultiesDT)
def get_faculties(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,

):
    faculties = session.scalars(select(Faculty).offset(offset).limit(limit)).all()
    return {'data': faculties}


@router.get("/faculties/{faculty_id}", response_model=Faculty)
def get_faculty(faculty_id: int, session: SessionDep):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty


@router.patch("/faculties/{faculty_id}", response_model=Faculty)
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


@router.delete("/faculties/{faculty_id}")
def delete_faculty(faculty_id: int, session: SessionDep):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    session.delete(faculty)
    session.commit()
    return {"ok": True}


@router.get("/faculties/random/", response_model=Faculty)
def get_faculty_random(session: SessionDep):
    f = session.scalars(select(Faculty)).all()

    if not f:
        raise HTTPException(status_code=404, detail="No faculties found")

    random_faculty = random.choice(f)
    return random_faculty

# --------------------------------Courses---------------------------------------------

@app.get("/courses/", response_class=HTMLResponse)
def courses(request: Request):
    return templates.TemplateResponse(
        request=request, name="courses.html", context={},
    )


@router.post("/course/", response_model=Course)
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


@router.get("/courses/", response_model=CoursesDT)
def get_courses(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    courses = session.scalars(select(Course).join(Faculty).offset(offset).limit(limit))
    return {'data': courses}


@router.get("/courses/{course_id}/", response_model=Course)
def get_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch("/courses/{course_id}/", response_model=Course)
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


@router.delete("/courses/{course_id}/")
def delete_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course)
    session.commit()
    return {"ok": True}

# --------------------------------Groups---------------------------------------------

@app.get("/groups/", response_class=HTMLResponse)
def groups(request: Request):
    return templates.TemplateResponse(
        request=request, name="groups.html", context={},
    )


@router.post("/group/", response_model=Group)
def create_group(group: Group, session: SessionDep):
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


class GroupItem(BaseModel):
    id: int
    num: int
    course: Course


class GroupsDT(BaseModel):
    data: list[GroupItem]


@router.get("/groups/", response_model=GroupsDT)
def get_groups(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    groups = session.scalars(select(Group).join(Course).offset(offset).limit(limit))
    return {'data': groups}


@router.get("/groups/{group_id}", response_model=Group)
def get_group(group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.patch("/groups/{group_id}", response_model=Group)
def update_group(group_id: int, group: Group, session: SessionDep):
    group_db = session.get(Group, group_id)
    if not group_db:
        raise HTTPException(status_code=404, detail="Group not found")
    group_data = group.model_dump(exclude_unset=True)
    group_db.sqlmodel_update(group_data)
    session.add(group_db)
    session.commit()
    session.refresh(group_db)
    return group_db


@router.delete("/groups/{group_id}")
def delete_group(group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    session.delete(group)
    session.commit()
    return {"ok": True}

# --------------------------------Students---------------------------------------------

@app.get("/students/", response_class=HTMLResponse)
def students(request: Request):
    return templates.TemplateResponse(
        request=request, name="students.html", context={},
    )


@router.post("/student/", response_model=Student)
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


@router.get("/students/", response_model=StudentDT)
def get_students(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    students = session.scalars(select(Student).join(Group).offset(offset).limit(limit))
    return {'data': students}


@router.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/students/{student_id}", response_model=Student)
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


@router.delete("/students/{student_id}")
def delete_student(student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    session.delete(student)
    session.commit()
    return {"ok": True}


@router.get("/students/random/", response_model=Student)
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


# --------------------------------Teachers---------------------------------------------

@app.get("/teachers/", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse(
        request=request, name="teachers.html", context={},
    )


@router.post("/teacher/", response_model=Teacher)
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


@router.get("/teachers/", response_model=teacherDT)
def get_teachers(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    teachers = session.scalars(select(Teacher).offset(offset).limit(limit))
    return {'data': teachers}


@router.get("/teachers/{teacher_id}", response_model=Teacher)
def get_teacher(teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="teacher not found")
    return teacher


@router.patch("/teachers/{teacher_id}", response_model=Teacher)
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


@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="teacher not found")
    session.delete(teacher)
    session.commit()
    return {"ok": True}


app.include_router(router, prefix="/api")
