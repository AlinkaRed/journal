from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query

from sqlmodel import Field, Session, SQLModel, Relationship, create_engine, select


DB_HOST = 'localhost'
DB_PORT = 5437
DB_NAME = 'storefront'
DB_USER = 'storefront'
DB_PASSWORD = 'storefront'

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]



class Faculty(SQLModel, table=True):
    __tablename__ = "faculty"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    num: str = Field(index=True, unique=True)

    courses: list["Course"] = Relationship(back_populates="faculty")    # courses: Mapped[List["Course"]] = relationship(back_populates="faculty", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Faculty(id={self.id!r}, name={self.name!r}, num={self.num!r})"


class Course(SQLModel, table=True):
    __tablename__ = "course"

    id: int | None = Field(default=None, primary_key=True)
    num: str = Field(index=True, unique=True)

    faculty_id: int | None = Field(default=None, foreign_key="faculty.id")
    faculty: Faculty | None = Relationship(back_populates="courses")

    def __repr__(self) -> str:
        return f"Course(id={self.id!r}, num={self.num!r}, faculty={self.faculty.name!r})"

