from unittest import TestCase, mock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, exists
from sqlmodel import SQLModel, Session, select
from sqlmodel.pool import StaticPool

from db import Faculty, Course, Group, Student, Teacher
from db import get_session
from main import app


DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'students'
DB_USER = 'postgres'
DB_PASSWORD = 'root'


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

    def assertJsonResponse(self, response):
        self.assertEqual(response.headers.get('content-type'), 'application/json')

    def assertResponse200(self, response):
        self.assertEqual(response.status_code, 200)

    def assertJsonResponseOK(self, response):
        self.assertJsonResponse(response)
        self.assertResponse200(response)


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

    def test_get_faculty(self) -> None:
        response = self.client.get(f'/api/faculties/{self.fa_1.id}/')
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

    def test_delete_faculty(self) -> None:
        with self.session as session:
            result = session.scalar(select(exists(Faculty).where(Faculty.id==self.fa_1.id)))
        self.assertTrue(result)

        response = self.client.delete(f'/api/faculties/{self.fa_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            result = session.scalar(select(exists(Faculty).where(Faculty.id == self.fa_1.id)))
        self.assertFalse(result)

    def test_update_faculty(self) -> None:
        fa_4 = Faculty(name='DDD', num=4)

        with self.session as session:
            session.add(fa_4)
            session.commit()
            session.refresh(fa_4)

        update_data = {"name": "Updated DDD", "num": 5}
        response = self.client.patch(
            '/api/faculties/4',
            json=update_data
        )
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            faculty = session.get(Faculty, 4)
            self.assertIsNotNone(faculty)
            self.assertEqual(faculty.name, "Updated DDD")
            self.assertEqual(int(faculty.num), 5)


class TestCourses(BaseTest):

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

            self.c_1 = Course(num=1, faculty=self.fa_1)
            self.c_2 = Course(num=2, faculty=self.fa_2)
            self.c_3 = Course(num=3, faculty=self.fa_1)

            session.add(self.c_1)
            session.add(self.c_2)
            session.add(self.c_3)
            session.commit()
            session.refresh(self.c_1)
            session.refresh(self.c_2)
            session.refresh(self.c_3)

    def test_get_course(self) -> None:
        response = self.client.get(f'/api/courses/{self.c_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

    def test_get_wrong_course(self) -> None:
        response = self.client.get('/api/courses/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_courses(self) -> None:
        response = self.client.get('/api/courses/')
        self.assertJsonResponseOK(response)
        json = response.json()
        self.assertIn('data', json)
        self.assertTrue(isinstance(json['data'], list))

        c_data = json['data']
        print(c_data)
        self.assertEqual(len(c_data), 3)

        self.assertEqual(c_data[0]['num'], int(self.c_1.num))
        self.assertEqual(c_data[0]['faculty']['id'], int(self.c_1.faculty_id))
        self.assertTrue(isinstance(c_data[0].get('id'), int))

        self.assertEqual(c_data[1]['num'], int(self.c_2.num))
        self.assertEqual(c_data[1]['faculty']['id'], int(self.c_2.faculty_id))
        self.assertTrue(isinstance(c_data[1].get('id'), int))

        self.assertEqual(c_data[2]['num'], int(self.c_3.num))
        self.assertEqual(c_data[2]['faculty']['id'], int(self.c_3.faculty_id))
        self.assertTrue(isinstance(c_data[2].get('id'), int))

    def test_delete_course(self) -> None:
        with self.session as session:
            result = session.scalar(select(exists(Course).where(Course.id==self.c_1.id)))
        self.assertTrue(result)

        response = self.client.delete(f'/api/courses/{self.c_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            result = session.scalar(select(exists(Course).where(Course.id==self.c_1.id)))
        self.assertFalse(result)

    def test_update_course(self) -> None:
        c_4 = Course(num=4, faculty=self.fa_1)

        with self.session as session:
            session.add(c_4)
            session.commit()
            session.refresh(c_4)

        update_data = {"num": 5}
        response = self.client.patch(
            '/api/courses/4',
            json=update_data
        )
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            c = session.get(Course, 4)
            self.assertIsNotNone(c)
            self.assertEqual(c.faculty_id, 1)
            self.assertEqual(int(c.num), 5)


class TestGroups(BaseTest):

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

            self.c_1 = Course(num=1, faculty=self.fa_1)
            self.c_2 = Course(num=2, faculty=self.fa_2)
            self.c_3 = Course(num=3, faculty=self.fa_3)

            session.add(self.c_1)
            session.add(self.c_2)
            session.add(self.c_3)
            session.commit()
            session.refresh(self.c_1)
            session.refresh(self.c_2)
            session.refresh(self.c_3)

            self.g_1 = Group(num=1, course=self.c_1)
            self.g_2 = Group(num=2, course=self.c_2)
            self.g_3 = Group(num=3, course=self.c_3)

            session.add(self.g_1)
            session.add(self.g_2)
            session.add(self.g_3)
            session.commit()
            session.refresh(self.g_1)
            session.refresh(self.g_2)
            session.refresh(self.g_3)

    def test_get_group(self) -> None:
        response = self.client.get(f'/api/groups/{self.g_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

    def test_get_wrong_group(self) -> None:
        response = self.client.get('/api/groups/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_groups(self) -> None:
        response = self.client.get('/api/groups/')
        self.assertJsonResponseOK(response)
        json = response.json()
        self.assertIn('data', json)
        self.assertTrue(isinstance(json['data'], list))

        g_data = json['data']
        self.assertEqual(len(g_data), 3)

        self.assertEqual(g_data[0]['num'], int(self.g_1.num))
        self.assertEqual(g_data[0]['course']['id'], int(self.g_1.course_id))
        self.assertTrue(isinstance(g_data[0].get('id'), int))

        self.assertEqual(g_data[1]['num'], int(self.g_2.num))
        self.assertEqual(g_data[1]['course']['id'], int(self.g_2.course_id))
        self.assertTrue(isinstance(g_data[1].get('id'), int))

        self.assertEqual(g_data[2]['num'], int(self.g_3.num))
        self.assertEqual(g_data[2]['course']['id'], int(self.g_3.course_id))
        self.assertTrue(isinstance(g_data[2].get('id'), int))

    def test_delete_group(self) -> None:
        with self.session as session:
            result = session.scalar(select(exists(Group).where(Group.id==self.g_1.id)))
        self.assertTrue(result)

        response = self.client.delete(f'/api/groups/{self.g_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            result = session.scalar(select(exists(Group).where(Group.id==self.g_1.id)))
        self.assertFalse(result)

    def test_update_group(self) -> None:
        g_4 = Group(num=4, course=self.c_1)

        with self.session as session:
            session.add(g_4)
            session.commit()
            session.refresh(g_4)

        update_data = {"num": 5}
        response = self.client.patch(
            '/api/groups/4',
            json=update_data
        )
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            g = session.get(Group, 4)
            self.assertIsNotNone(g)
            self.assertEqual(g.course_id, 1)
            self.assertEqual(int(g.num), 5)


class TestStudent(BaseTest):

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

            self.c_1 = Course(num=1, faculty=self.fa_1)
            self.c_2 = Course(num=2, faculty=self.fa_2)
            self.c_3 = Course(num=3, faculty=self.fa_3)

            session.add(self.c_1)
            session.add(self.c_2)
            session.add(self.c_3)
            session.commit()
            session.refresh(self.c_1)
            session.refresh(self.c_2)
            session.refresh(self.c_3)

            self.g_1 = Group(num=1, course=self.c_1)
            self.g_2 = Group(num=2, course=self.c_2)
            self.g_3 = Group(num=3, course=self.c_3)

            session.add(self.g_1)
            session.add(self.g_2)
            session.add(self.g_3)
            session.commit()
            session.refresh(self.g_1)
            session.refresh(self.g_2)
            session.refresh(self.g_3)

            self.s_1 = Student(first_name='Иван', middle_name='Сергеевич',
                               last_name='Иванов', group=self.g_1)
            self.s_2 = Student(first_name='Мария', middle_name='Александровна',
                               last_name='Ильина', group=self.g_2)
            self.s_3 = Student(first_name='Павел', middle_name='Петрович',
                               last_name='Москвин', group=self.g_3)

            session.add(self.s_1)
            session.add(self.s_2)
            session.add(self.s_3)
            session.commit()
            session.refresh(self.s_1)
            session.refresh(self.s_2)
            session.refresh(self.s_3)

    def test_get_student(self) -> None:
        response = self.client.get(f'/api/students/{self.s_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

    def test_get_wrong_student(self) -> None:
        response = self.client.get('/api/students/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_students(self) -> None:
        response = self.client.get('/api/students/')
        self.assertJsonResponseOK(response)
        json = response.json()
        self.assertIn('data', json)
        self.assertTrue(isinstance(json['data'], list))

        s_data = json['data']
        self.assertEqual(len(s_data), 3)

        self.assertEqual(s_data[0]['first_name'], self.s_1.first_name)
        self.assertEqual(s_data[0]['middle_name'], self.s_1.middle_name)
        self.assertEqual(s_data[0]['last_name'], self.s_1.last_name)
        self.assertEqual(s_data[0]['group']['id'], int(self.s_1.groups_id))
        self.assertTrue(isinstance(s_data[0].get('id'), int))

        self.assertEqual(s_data[1]['first_name'], self.s_2.first_name)
        self.assertEqual(s_data[1]['middle_name'], self.s_2.middle_name)
        self.assertEqual(s_data[1]['last_name'], self.s_2.last_name)
        self.assertEqual(s_data[1]['group']['id'], int(self.s_2.groups_id))
        self.assertTrue(isinstance(s_data[1].get('id'), int))

        self.assertEqual(s_data[2]['first_name'], self.s_3.first_name)
        self.assertEqual(s_data[2]['middle_name'], self.s_3.middle_name)
        self.assertEqual(s_data[2]['last_name'], self.s_3.last_name)
        self.assertEqual(s_data[2]['group']['id'], int(self.s_3.groups_id))
        self.assertTrue(isinstance(s_data[2].get('id'), int))

    def test_delete_student(self) -> None:
        with self.session as session:
            result = session.scalar(select(exists(Student).where(Student.id==self.s_1.id)))
        self.assertTrue(result)

        response = self.client.delete(f'/api/students/{self.s_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            result = session.scalar(select(exists(Student).where(Student.id==self.s_1.id)))
        self.assertFalse(result)

    def test_update_student(self) -> None:
        s_4 = Student(first_name='Артем', middle_name='Сергеевич',
                           last_name='Данилов', group=self.g_1)

        with self.session as session:
            session.add(s_4)
            session.commit()
            session.refresh(s_4)

        update_data = {"first_name" : 'Михаил'}
        response = self.client.patch(
            '/api/students/4',
            json=update_data
        )
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            s = session.get(Student, 4)
            self.assertIsNotNone(s)
            self.assertEqual(s.groups_id, 1)
            self.assertEqual(s.first_name, 'Михаил')

    def test_random_student_by_all(self) -> None:
        response = self.client.get(
            '/api/students/random/',
            params={
                'faculty_id': 1,
                'course_id': 1,
                'group_id': 1,
            }
        )
        self.assertJsonResponseOK(response)

        json = response.json()

        self.assertTrue(isinstance(json, dict))
        self.assertEqual(json['first_name'], self.s_1.first_name)
        self.assertEqual(json['middle_name'], self.s_1.middle_name)
        self.assertEqual(json['last_name'], self.s_1.last_name)

    def test_random_student_by_faculty(self) -> None:
        response = self.client.get(
            '/api/students/random/',
            params={
                'faculty_id': 2
            }
        )
        self.assertJsonResponseOK(response)

        json = response.json()

        self.assertTrue(isinstance(json, dict))
        self.assertEqual(json['first_name'], self.s_2.first_name)
        self.assertEqual(json['middle_name'], self.s_2.middle_name)
        self.assertEqual(json['last_name'], self.s_2.last_name)

    def test_random_student_by_course_and_group(self) -> None:
        response = self.client.get(
            '/api/students/random/',
            params={
                'course_id': 3,
                'group_id': 3
            }
        )
        self.assertJsonResponseOK(response)

        json = response.json()

        self.assertTrue(isinstance(json, dict))
        self.assertEqual(json['first_name'], self.s_3.first_name)
        self.assertEqual(json['middle_name'], self.s_3.middle_name)
        self.assertEqual(json['last_name'], self.s_3.last_name)

    def test_random_student_wrong(self) -> None:
        response = self.client.get(
            '/api/students/random/',
            params={
                'course_id': 1,
                'group_id': 2
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_random_student(self) -> None:
        arr = set()
        for i in range(10):
            response = self.client.get(
                '/api/students/random/'
            )
            self.assertJsonResponseOK(response)

            student = response.json()
            arr.add(student['id'])

        self.assertTrue(len(arr) > 1)

    def test_random_student_mock(self) -> None:
        with mock.patch('random.choice', return_value=self.s_2):
            response = self.client.get(
                '/api/students/random/'
            )
        self.assertJsonResponseOK(response)
        student = response.json()
        self.assertEqual(student['id'], self.s_2.id)


class TestTeacher(BaseTest):

    def setUp(self):
        super().setUp()

        with self.session as session:
            self.t_1 = Teacher(first_name='Иван', middle_name='Сергеевич',
                               last_name='Иванов')
            self.t_2 = Teacher(first_name='Мария', middle_name='Александровна',
                               last_name='Ильина')
            self.t_3 = Teacher(first_name='Павел', middle_name='Петрович',
                               last_name='Москвин')

            session.add(self.t_1)
            session.add(self.t_2)
            session.add(self.t_3)
            session.commit()
            session.refresh(self.t_1)
            session.refresh(self.t_2)
            session.refresh(self.t_3)

    def test_get_teacher(self) -> None:
        response = self.client.get(f'/api/teachers/{self.t_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

    def test_get_wrong_teacher(self) -> None:
        response = self.client.get('/api/teachers/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_teachers(self) -> None:
        response = self.client.get('/api/teachers/')
        self.assertJsonResponseOK(response)
        json = response.json()
        self.assertIn('data', json)
        self.assertTrue(isinstance(json['data'], list))

        s_data = json['data']
        self.assertEqual(len(s_data), 3)

        self.assertEqual(s_data[0]['first_name'], self.t_1.first_name)
        self.assertEqual(s_data[0]['middle_name'], self.t_1.middle_name)
        self.assertEqual(s_data[0]['last_name'], self.t_1.last_name)
        self.assertTrue(isinstance(s_data[0].get('id'), int))

        self.assertEqual(s_data[1]['first_name'], self.t_2.first_name)
        self.assertEqual(s_data[1]['middle_name'], self.t_2.middle_name)
        self.assertEqual(s_data[1]['last_name'], self.t_2.last_name)
        self.assertTrue(isinstance(s_data[1].get('id'), int))

        self.assertEqual(s_data[2]['first_name'], self.t_3.first_name)
        self.assertEqual(s_data[2]['middle_name'], self.t_3.middle_name)
        self.assertEqual(s_data[2]['last_name'], self.t_3.last_name)
        self.assertTrue(isinstance(s_data[2].get('id'), int))

    def test_delete_teacher(self) -> None:
        with self.session as session:
            result = session.scalar(select(exists(Teacher).where(Teacher.id==self.t_1.id)))
        self.assertTrue(result)

        response = self.client.delete(f'/api/teachers/{self.t_1.id}/')
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            result = session.scalar(select(exists(Teacher).where(Teacher.id==self.t_1.id)))
        self.assertFalse(result)

    def test_update_teachar(self) -> None:
        t_4 = Teacher(id=4, first_name='Артем', middle_name='Сергеевич',
                      last_name='Данилов')

        with self.session as session:
            session.add(t_4)
            session.commit()
            session.refresh(t_4)

        update_data = {"first_name" : "Михаил"}
        response = self.client.patch(
            f'/api/teachers/4',
            json=update_data
        )
        self.assertJsonResponseOK(response)
        self.assertEqual(response.status_code, 200)

        with self.session as session:
            t = session.get(Teacher, 4)
            self.assertIsNotNone(t)
            self.assertEqual(t.first_name, 'Михаил')