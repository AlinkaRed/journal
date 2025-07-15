from fastapi.testclient import TestClient

from db import Faculty
from main import app


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


# --------------------------------- unittest --------------------------------------
from unittest import TestCase


class BaseTest(TestCase):

    def setUp(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        self.session = Session(engine)

        def get_session_override():
            return self.session

        app.dependency_overrides[get_session] = get_session_override

        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()


class TestFaculties(BaseTest):

    def setUp(self):
        super().setUp()

        with self.session as session:
            self.fa_1 = Faculty(name='AAA', num=1)
            self.fa_2 = Faculty(name='BBB', num=2)
            self.fa_3 = Faculty(name='CCC', num=3)

            session.add(self.fa_1)
            session.add(self.fa_2)
            session.add(self.fa_3)
            session.commit()
            session.refresh(self.fa_1)
            session.refresh(self.fa_2)
            session.refresh(self.fa_3)

    def assertJsonResponse(self, response):
        self.assertEqual(response.headers.get('content-type'), 'application/json')

    def assertResponse200(self, response):
        self.assertEqual(response.status_code, 200)

    def assertJsonResponseOK(self, response):
        self.assertJsonResponse(response)
        self.assertResponse200(response)

    def test_get_faculty(self) -> None:
        response = self.client.get('/api/faculties/1/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

    def test_get_wrong_faculty(self) -> None:
        response = self.client.get('/api/faculties/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_faculties(self) -> None:
        response = self.client.get('/api/faculties/')
        self.assertJsonResponseOK(response)
        json = response.json()
        self.assertIn('data', json)
        self.assertTrue(isinstance(json['data'], list))

        faculty_data = json['data']
        self.assertEqual(len(faculty_data), 3)

        self.assertEqual(faculty_data[0]['name'], self.fa_1.name)
        self.assertEqual(faculty_data[0]['num'], self.fa_1.num)
        self.assertTrue(isinstance(faculty_data[0].get('id'), int))

        self.assertEqual(faculty_data[1]['name'], self.fa_2.name)
        self.assertEqual(faculty_data[1]['num'], self.fa_2.num)
        self.assertTrue(isinstance(faculty_data[1].get('id'), int))

        self.assertEqual(faculty_data[2]['name'], self.fa_3.name)
        self.assertEqual(faculty_data[2]['num'], self.fa_3.num)
        self.assertTrue(isinstance(faculty_data[2].get('id'), int))
