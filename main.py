from typing import Annotated
import random
from fastapi import FastAPI, HTTPException, Query, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import select

from db.base import SessionDep
from db.models import (
    Course,
    Faculty,
    Group,
    Student,
    Teacher,
)
from faculties import faculties_router, faculties_api_router
from courses import courses_router, courses_api_router
from groups import groups_router, groups_api_router
from students import students_router, students_api_router
from teachers import teachers_router, teachers_api_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")

router = APIRouter()


# --------------------------------Base---------------------------------------------

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )


app.include_router(router, prefix="/api")
app.include_router(faculties_router)
app.include_router(faculties_api_router)

app.include_router(router, prefix="/api")
app.include_router(courses_router)
app.include_router(courses_api_router)

app.include_router(router, prefix="/api")
app.include_router(groups_router)
app.include_router(groups_api_router)

app.include_router(router, prefix="/api")
app.include_router(students_router)
app.include_router(students_api_router)

app.include_router(router, prefix="/api")
app.include_router(teachers_router)
app.include_router(teachers_api_router)
