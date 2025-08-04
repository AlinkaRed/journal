from typing import Annotated

from fastapi import HTTPException, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlmodel import SQLModel

from db.base import SessionDep
from db.models import Faculty


templates = Jinja2Templates(directory="templates")

faculties_router = APIRouter(prefix='/faculties', tags=['Faculties'])


@faculties_router.get("/", response_class=HTMLResponse)
def faculties(request: Request):
    return templates.TemplateResponse(
        request=request, name="faculties/faculties.html", context={}
    )


@faculties_router.get("/{faculty_id}/details/", response_class=HTMLResponse)
def faculty_details(request: Request, faculty_id: int, session: SessionDep):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return templates.TemplateResponse(
        request=request, name="faculties/faculty_details.html", context={'faculty': faculty}
    )


@faculties_router.get("/{faculty_id}/edit/", response_class=HTMLResponse)
def faculty_edit(request: Request, faculty_id: int, session: SessionDep):
    faculty = session.get(Faculty, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return templates.TemplateResponse(
        request=request, name="faculties/faculty_edit.html", context={'faculty': faculty}
    )


class FacultyUpdate(SQLModel):
    name: str
    num: int


@faculties_router.post("/{faculty_id}/edit/", response_class=HTMLResponse)
def faculty_update(request: Request, faculty_id: int, session: SessionDep, faculty: Annotated[FacultyUpdate, Form()]):
    """
    https://fastapi.tiangolo.com/tutorial/request-form-models/?h=form#forbid-extra-form-fields
    https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
    or
    https://sqlmodel.tiangolo.com/tutorial/update/#set-a-field-value
    """
    faculty_db = session.get(Faculty, faculty_id)
    if not faculty_db:
        raise HTTPException(status_code=404, detail="Faculty not found")
    faculty_data = faculty.model_dump(exclude_unset=True)
    faculty_db.sqlmodel_update(faculty_data)
    session.add(faculty_db)
    session.commit()
    session.refresh(faculty_db)
    return templates.TemplateResponse(
        request=request, name="faculties/faculty_details.html", context={'faculty': faculty_db}
    )


class FacultyCreate(SQLModel):
    name: str
    num: int


@faculties_router.get("/create/", response_class=HTMLResponse)
def faculty_add(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request=request, name="faculties/faculty_create.html"
    )


@faculties_router.post("/create/", response_class=HTMLResponse)
def faculty_create(
    request: Request,
    session: SessionDep,
    name: Annotated[str, Form()],
    num: Annotated[int, Form()]
):
    faculty = Faculty(name=name, num=num)
    session.add(faculty)
    session.commit()
    session.refresh(faculty)
    return templates.TemplateResponse(
        request=request,
        name="faculties/faculty_details.html",
        context={'faculty': faculty}
    )
