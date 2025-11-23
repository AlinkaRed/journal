from typing import Annotated

from fastapi import HTTPException, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlmodel import SQLModel, select
from sqlalchemy import exists, and_

from db.base import SessionDep
from db.models import Group, Course, Student


templates = Jinja2Templates(directory="templates")

groups_router = APIRouter(prefix='/groups', tags=['Groups'])


@groups_router.get("/", response_class=HTMLResponse)
def groups(request: Request):
    return templates.TemplateResponse(
        request=request, name="groups/groups_all.html", context={}
    )


@groups_router.get("/{group_id}/details/", response_class=HTMLResponse)
def group_details(request: Request, group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return templates.TemplateResponse(
        request=request, name="groups/group_details.html", context={'group': group}
    )


@groups_router.get("/{group_id}/edit/", response_class=HTMLResponse)
def group_edit(request: Request, group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return templates.TemplateResponse(
        request=request, name="groups/group_edit.html", context={'group': group}
    )


class GroupUpdate(SQLModel):
    name: str
    num: int


@groups_router.post("/{group_id}/edit/", response_class=HTMLResponse)
def group_update(request: Request, group_id: int, session: SessionDep, group: Annotated[GroupUpdate, Form()]):
    """
    https://fastapi.tiangolo.com/tutorial/request-form-models/?h=form#forbid-extra-form-fields
    https://sqlmodel.tiangolo.com/tutorial/fastapi/update/
    or
    https://sqlmodel.tiangolo.com/tutorial/update/#set-a-field-value
    """
    group_db = session.get(Group, group_id)
    if not group_db:
        raise HTTPException(status_code=404, detail="Group not found")
    group_data = group.model_dump(exclude_unset=True)
    group_db.sqlmodel_update(group_data)
    session.add(group_db)
    session.commit()
    session.refresh(group_db)
    return templates.TemplateResponse(
        request=request, name="groups/group_details.html", context={'group': group_db}
    )


class GroupCreate(SQLModel):
    num: int
    course_id: int


@groups_router.get("/create/", response_class=HTMLResponse)
def group_add(request: Request, session: SessionDep):
    courses = session.scalars(select(Course)).all()
    return templates.TemplateResponse(
        request=request,
        name="groups/group_create.html",
        context={'courses': courses}
    )


@groups_router.post("/create/", response_class=HTMLResponse)
def group_create(
        request: Request,
        session: SessionDep,
        num: Annotated[int, Form()],
        course_id: Annotated[int, Form()],
):
    errors = {}

    group_exists = session.query(
        exists().where(and_(
            Group.num == num,
            Group.course_id == course_id
        ))
    ).scalar()

    if group_exists:
        errors["num"] = "Группа с таким номером уже существует для этого курса"
        errors["course_id"] = "Выберите другой курс или измените номер группы"

    if errors:
        courses = session.query(Course).all()
        return templates.TemplateResponse(
            request=request,
            name="groups/group_create.html",
            context={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {"num": num, "course_id": course_id},
                "courses": courses
            },
        )

    g = Group(num=num, course_id=course_id)
    session.add(g)
    session.commit()
    session.refresh(g)

    return templates.TemplateResponse(
        request=request,
        name="groups/group_details.html",
        context={'group': g}
    )