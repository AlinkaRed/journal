from typing import Annotated

from fastapi import HTTPException, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlmodel import SQLModel, select

from db.base import SessionDep
from db.models import Course, Faculty


templates = Jinja2Templates(directory="templates")

courses_router = APIRouter(prefix='/courses', tags=['Courses'])


@courses_router.get("/", response_class=HTMLResponse)
def courses(request: Request):
    return templates.TemplateResponse(
        request=request, name="courses/courses.html", context={}
    )


@courses_router.get("/{course_id}/details/", response_class=HTMLResponse)
def course_details(request: Request, course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return templates.TemplateResponse(
        request=request, name="courses/course_details.html", context={'course': course}
    )


@courses_router.get("/{course_id}/edit/", response_class=HTMLResponse)
def course_edit(request: Request, course_id: int, session: SessionDep):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return templates.TemplateResponse(
        request=request, name="courses/course_edit.html", context={'course': course}
    )


class CourseUpdate(SQLModel):
    name: str
    num: int


@courses_router.post("/{course_id}/edit/", response_class=HTMLResponse)
def course_update(request: Request, course_id: int, session: SessionDep, course: Annotated[CourseUpdate, Form()]):
    """
    https://fastapi.tiangolo.com/tutorial/request-form-models/?h=form#forbid-extra-form-fields
    https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
    or
    https://sqlmodel.tiangolo.com/tutorial/update/#set-a-field-value
    """
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    course_data = course.model_dump(exclude_unset=True)
    course_db.sqlmodel_update(course_data)
    session.add(course_db)
    session.commit()
    session.refresh(course_db)
    return templates.TemplateResponse(
        request=request, name="courses/course_details.html", context={'course': course_db}
    )


class CourseCreate(SQLModel):
    num: int
    faculty_id: int


@courses_router.get("/create/", response_class=HTMLResponse)
def course_add(request: Request, session: SessionDep):
    faculties = session.scalars(select(Faculty)).all()
    return templates.TemplateResponse(
        request=request,
        name="courses/course_create.html",
        context={'faculties': faculties}
    )


@courses_router.post("/create/", response_class=HTMLResponse)
def course_create(
        request: Request,
        session: SessionDep,
        num: Annotated[int, Form()],
        faculty_id: Annotated[int, Form()]
):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    c = Course(num=num, faculty_id=faculty_id)
    session.add(c)
    session.commit()
    session.refresh(c)
    return templates.TemplateResponse(
        request=request,
        name="courses/course_details.html",
        context={'course': c}
    )

