
from sqlmodel import Field, SQLModel, Relationship


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

    groups: list["Group"] = Relationship(back_populates="course")

    def __repr__(self) -> str:
        return f"Course(id={self.id!r}, num={self.num!r}, faculty={self.faculty.name!r})"


class Group(SQLModel, table=True):
    __tablename__ = "groups"

    id: int | None = Field(default=None, primary_key=True)
    num: str = Field(index=True, unique=True)

    course_id: int | None = Field(default=None, foreign_key="course.id")
    course: Course | None = Relationship(back_populates="groups")

    students: list["Student"] = Relationship(back_populates="group")

    def __repr__(self) -> str:
        return f"Group(id={self.id!r}, num={self.num!r}, course={self.course.num!r})"


class Student(SQLModel, table=True):
    __tablename__ = "student"

    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field()
    middle_name: str | None = Field(default=None)
    last_name: str = Field()

    groups_id: int | None = Field(default=None, foreign_key="groups.id")
    group: Group | None = Relationship(back_populates="students")

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, first_name={self.first_name!r}, middle_name={self.middle_name!r}, last_name={self.last_name!r}, group={self.groups.num!r})"


class Teacher(SQLModel, table=True):
    __tablename__ = "teacher"

    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field()
    middle_name: str | None = Field(default=None)
    last_name: str = Field()

    def __repr__(self) -> str:
        return f"Teacher(id={self.id!r}, first_name={self.first_name!r}, middle_name={self.middle_name!r}, last_name={self.last_name!r}"
