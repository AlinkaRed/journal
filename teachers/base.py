from typing import Annotated

from fastapi import HTTPException, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlmodel import SQLModel

from db.base import SessionDep
from db.models import Teacher


templates = Jinja2Templates(directory="templates")

teachers_router = APIRouter(prefix='/teachers', tags=['Teachers'])


@teachers_router.get("/", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse(
        request=request, name="teachers/teachers.html", context={}
    )


@teachers_router.get("/{teacher_id}/details/", response_class=HTMLResponse)
def teacher_details(request: Request, teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return templates.TemplateResponse(
        request=request, name="teachers/teacher_details.html", context={'teacher': teacher}
    )


@teachers_router.get("/{teacher_id}/edit/", response_class=HTMLResponse)
def teacher_edit(request: Request, teacher_id: int, session: SessionDep):
    teacher = session.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return templates.TemplateResponse(
        request=request, name="teachers/teacher_edit.html", context={'teacher': teacher}
    )


class TeacherUpdate(SQLModel):
    first_name: str
    middle_name: str
    last_name: str


@teachers_router.post("/{teacher_id}/edit/", response_class=HTMLResponse)
def teacher_update(request: Request, teacher_id: int, session: SessionDep, teacher: Annotated[TeacherUpdate, Form()]):
    """
    https://fastapi.tiangolo.com/tutorial/request-form-models/?h=form#forbid-extra-form-fields
    https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
    or
    https://sqlmodel.tiangolo.com/tutorial/update/#set-a-field-value
    """
    teacher_db = session.get(Teacher, teacher_id)
    if not teacher_db:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher_data = teacher.model_dump(exclude_unset=True)
    teacher_db.sqlmodel_update(teacher_data)
    session.add(teacher_db)
    session.commit()
    session.refresh(teacher_db)
    return templates.TemplateResponse(
        request=request, name="teachers/teacher_details.html", context={'teacher': teacher_db}
    )


class TeacherCreate(SQLModel):
    first_name: str
    middle_name: str
    last_name: str
    date_of_birth: str
    inn: int


@teachers_router.get("/create/", response_class=HTMLResponse)
def teacher_add(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request=request, name="teachers/teacher_create.html"
    )


@teachers_router.post("/create/", response_class=HTMLResponse)
def create_teacher(
    request: Request,
    session: SessionDep,
    first_name: Annotated[str, Form()],
    middle_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    date_of_birth: Annotated[str, Form()],
    inn: Annotated[int, Form()]
):
    t = Teacher(first_name=first_name, middle_name=middle_name, last_name=last_name, date_of_birth=date_of_birth, inn=inn)
    session.add(t)
    session.commit()
    session.refresh(t)
    return templates.TemplateResponse(
        request=request,
        name="teachers/teacher_details.html",
        context={'teacher': t}
    )