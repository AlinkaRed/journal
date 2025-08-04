from typing import Annotated
import random

from fastapi import HTTPException, Query, Request, APIRouter
from pydantic import BaseModel
from sqlmodel import select

from db.base import SessionDep
from db.models import Group, Course, Faculty


groups_api_router = APIRouter(prefix='/api/groups', tags=['Groups API'])


@groups_api_router.post("/", response_model=Group)
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
    group_db = session.get(Group, group_id)
    if not group_db:
        raise HTTPException(status_code=404, detail="Group not found")
    group_data = group.model_dump(exclude_unset=True)
    group_db.sqlmodel_update(group_data)
    session.add(group_db)
    session.commit()
    session.refresh(group_db)
    return group_db


@groups_api_router.delete("/groups/{group_id}")
def delete_group(group_id: int, session: SessionDep):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    session.delete(group)
    session.commit()
    return {"ok": True}

