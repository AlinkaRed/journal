from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy import exists, and_
from sqlalchemy import delete

from db.base import SessionDep
from db.models import Group, Course, Faculty, Student


groups_api_router = APIRouter(prefix='/api/groups', tags=['Groups API'])


@groups_api_router.post("/", response_model=Group)
def create_group(group: Group, session: SessionDep):
    errors = {}

    group_exists = session.query(
        exists().where(and_(
            Group.num == group.num,
            Group.course_id == group.course_id
        ))
    ).scalar()

    if group_exists:
        errors["num"] = "Группа с таким номером уже существует для этого курса"
        errors["course_id"] = "Выберите другой курс или измените номер группы"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {"num": group.num, "course_id": group.course_id},
            }
        )

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


@groups_api_router.get("/", response_model=GroupsDT)
def get_groups(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    groups = session.scalars(select(Group).join(Course).offset(offset).limit(limit))
    return {'data': groups}


@groups_api_router.get("/{group_id}", response_model=Group)
def get_group(group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@groups_api_router.patch("/{group_id}", response_model=Group)
def update_group(group_id: int, group: Group, session: SessionDep):
    errors = {}

    group_db = session.get(Group, group_id)
    if not group_db:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.num and group.course_id is not None:
        if group.num != group_db.num and group.course_id != group_db.course_id:
            group_exists = session.query(
                exists().where(and_(
                    Group.num == group.num,
                    Group.course_id == group.course_id
                ))
            ).scalar()
            if group_exists:
                errors["num"] = "Группа с таким номером уже существует для этого курса"
                errors["course_id"] = "Выберите другой курс или измените номер группы"

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Невалидные данные",
                "field_errors": errors,
                "form_data": {
                    "num": group.num if group.num is not None else group_db.num,
                    "course_id": group.course_id if group.course_id is not None else group_db.course_id,
                },
            }
        )

    group_data = group.model_dump(exclude_unset=True)
    group_db.sqlmodel_update(group_data)
    session.add(group_db)
    session.commit()
    session.refresh(group_db)
    return group_db


@groups_api_router.delete("/{group_id}")
def delete_group(group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    session.exec(delete(Student).where(Student.groups_id == group_id))

    session.delete(group)
    session.commit()

    return {"ok": True}

