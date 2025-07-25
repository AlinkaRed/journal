from fastapi.testclient import TestClient
from sqlalchemy import text, create_engine
from db import Faculty, Course, Group, Student
from main import app

from sqlalchemy import create_engine, select, Table, MetaData, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'students'
DB_USER = 'postgres'
DB_PASSWORD = 'root'

# ------------------------ var 1 --------------------------------
def test_root():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['Content-Type']


# ------------------------ var 2 --------------------------------

import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
from db import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_faculty(client: TestClient):
    response = client.post(
        "/api/faculty/", json={"name": "FA1", "num": 1}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "FA1"
    assert data["num"] == '1'
    assert data["id"] is not None


def test_create_course(client: TestClient):
    response = client.post(
        "/api/course/", json={"num": 1, "faculty_id": 1}
    )
    data = response.json()

    assert response.status_code == 200
    assert str(data["num"]) == '1'
    assert str(data["faculty_id"]) == '1'
    assert data["id"] is not None


def test_get_faculties(session: Session, client: TestClient):
    fa_1_data = dict(name="Fa1", num='1')
    fa_2_data = dict(name="Fa2", num='2')
    fa_1 = Faculty(**fa_1_data)
    fa_2 = Faculty(**fa_2_data)
    session.add(fa_1)
    session.add(fa_2)
    session.commit()

    response = client.get(
        "/api/faculties/",
    )
    data = response.json()

    assert response.status_code == 200
    assert 'data' in data
    assert isinstance(data['data'], list)
    faculty_data = data['data']
    assert len(faculty_data) == 2
    assert faculty_data[0]['name'] == fa_1.name
    assert isinstance(faculty_data[0].get('id'), int)
    assert faculty_data[1]['name'] == fa_2.name
    assert isinstance(faculty_data[1].get('id'), int)


def test_get_courses(session: Session, client: TestClient):
    c_1_data = dict(num='1', faculty_id='1')
    c_2_data = dict(num='2', faculty_id='2')
    c_1 = Course(**c_1_data)
    c_2 = Course(**c_2_data)
    session.add(c_1)
    session.add(c_2)
    session.commit()

    response = client.get(
        "/api/courses/",
    )
    data = response.json()

    assert response.status_code == 200
    assert 'data' in data
    assert isinstance(data['data'], list)
    c_data = data['data']
    assert len(c_data) == 2
    assert c_data[0]['num'] == c_1.num
    assert isinstance(c_data[0].get('id'), int)
    assert c_data[1]['num'] == c_2.num
    assert isinstance(c_data[1].get('id'), int)
