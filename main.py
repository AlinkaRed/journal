from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import select

from db import (
    Course,
    Faculty,
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


@router.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.patch("/courses/{course_id}", response_model=Course)
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


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course)
    session.commit()
    return {"ok": True}


app.include_router(router, prefix="/api")
