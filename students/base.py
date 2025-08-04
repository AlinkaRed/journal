from typing import Annotated

from fastapi import HTTPException, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlmodel import SQLModel, select

from db.base import SessionDep
from db.models import Student, Group


templates = Jinja2Templates(directory="templates")

students_router = APIRouter(prefix='/students', tags=['Students'])


@students_router.get("/", response_class=HTMLResponse)
def students(request: Request):
    return templates.TemplateResponse(
        request=request, name="students/students.html", context={}
    )


@students_router.get("/{student_id}/details/", response_class=HTMLResponse)
def student_details(request: Request, student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse(
        request=request, name="students/student_details.html", context={'student': student}
    )


@students_router.get("/{student_id}/edit/", response_class=HTMLResponse)
def student_edit(request: Request, student_id: int, session: SessionDep):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse(
        request=request, name="students/student_edit.html", context={'student': student}
    )


class StudentUpdate(SQLModel):
    name: str
    num: int


@students_router.post("/{student_id}/edit/", response_class=HTMLResponse)
def student_update(request: Request, student_id: int, session: SessionDep, student: Annotated[StudentUpdate, Form()]):
    """
    https://fastapi.tiangolo.com/tutorial/request-form-models/?h=form#forbid-extra-form-fields
    https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
    or
    https://sqlmodel.tiangolo.com/tutorial/update/#set-a-field-value
    """
    student_db = session.get(Student, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="Student not found")
    student_data = student.model_dump(exclude_unset=True)
    student_db.sqlmodel_update(student_data)
    session.add(student_db)
    session.commit()
    session.refresh(student_db)
    return templates.TemplateResponse(
        request=request, name="students/student_details.html", context={'student': student_db}
    )


class StudentCreate(SQLModel):
    first_name: str
    middle_name: str
    last_name: str
    date_of_birth: str
    inn: int
    gender: str
    groups_id: int


@students_router.get("/create/", response_class=HTMLResponse)
def student_add(request: Request, session: SessionDep):
    g = session.scalars(select(Group)).all()
    return templates.TemplateResponse(
        request=request, name="students/student_create.html",
        context={'groups': g}
    )


@students_router.post("/create/", response_class=HTMLResponse)
def create_student(
    request: Request,
    session: SessionDep,
    first_name: Annotated[str, Form()],
    middle_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    date_of_birth: Annotated[str, Form()],
    inn: Annotated[int, Form()],
    gender: Annotated[str, Form()],
    groups_id: Annotated[int, Form()],
):
    g = session.get(Group, groups_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")

    s = Student(first_name=first_name, middle_name=middle_name,
                last_name=last_name, date_of_birth=date_of_birth, inn=inn,
                gender=gender, groups_id=groups_id)
    session.add(s)
    session.commit()
    session.refresh(s)
    return templates.TemplateResponse(
        request=request,
        name="students/student_details.html",
        context={'student': s}
    )