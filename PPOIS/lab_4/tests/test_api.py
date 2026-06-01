import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi.testclient import TestClient
from src.controller.app import create_app
from src.controller.api.deps import _default_service


@pytest.fixture(autouse=True)
def reset_service():
    _default_service.cache_clear()
    yield
    _default_service.cache_clear()


@pytest.fixture
def temp_state_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.json"
        yield state_file


@pytest.fixture
def client(temp_state_file, monkeypatch):
    monkeypatch.setenv("STATE_FILE", str(temp_state_file))
    app = create_app()
    return TestClient(app)


def unique_id():
    return str(uuid4())[:8]


class TestStudentEndpoints:
    def test_create_student(self, client):
        login = f"john_{unique_id()}"
        response = client.post(
            "/api/v1/students",
            json={"login": login, "name": "John Doe"}
        )
        assert response.status_code == 201
        assert response.json()["status"] == "success"
        assert response.json()["data"]["login"] == login

    def test_list_students(self, client):
        client.post("/api/v1/students", json={"login": f"jane_{unique_id()}", "name": "Jane"})
        response = client.get("/api/v1/students")
        assert response.status_code == 200
        assert "students" in response.json()["data"]
        assert len(response.json()["data"]["students"]) > 0

    def test_create_student_missing_field(self, client):
        response = client.post("/api/v1/students", json={"login": "test"})
        assert response.status_code == 422


class TestTeacherEndpoints:
    def test_create_teacher(self, client):
        login = f"prof_{unique_id()}"
        response = client.post(
            "/api/v1/teachers",
            json={"login": login, "name": "Professor"}
        )
        assert response.status_code == 201
        assert response.json()["status"] == "success"

    def test_list_teachers(self, client):
        client.post("/api/v1/teachers", json={"login": f"dr_{unique_id()}", "name": "Doctor"})
        response = client.get("/api/v1/teachers")
        assert response.status_code == 200
        assert "teachers" in response.json()["data"]


class TestMaterialEndpoints:
    def test_add_material(self, client):
        title = f"Intro_{unique_id()}"
        response = client.post(
            "/api/v1/materials",
            json={"title": title, "content": "Basic content"}
        )
        assert response.status_code == 201
        assert response.json()["data"]["title"] == title

    def test_list_materials(self, client):
        client.post("/api/v1/materials", json={"title": f"Ch1_{unique_id()}", "content": "Chapter 1"})
        response = client.get("/api/v1/materials")
        assert response.status_code == 200
        assert len(response.json()["data"]["materials"]) > 0


class TestAssignmentEndpoints:
    def test_add_assignment(self, client):
        title = f"HW_{unique_id()}"
        response = client.post(
            "/api/v1/assignments",
            json={"title": title, "description": "Homework 1"}
        )
        assert response.status_code == 201
        assert response.json()["data"]["title"] == title

    def test_list_assignments(self, client):
        client.post("/api/v1/assignments", json={"title": f"Ex1_{unique_id()}", "description": "Exercise"})
        response = client.get("/api/v1/assignments")
        assert response.status_code == 200


class TestSubmissionEndpoints:
    def test_submit_assignment(self, client):
        student = client.post(
            "/api/v1/students",
            json={"login": f"s1_{unique_id()}", "name": "Student"}
        ).json()["data"]

        assignment = client.post(
            "/api/v1/assignments",
            json={"title": f"Task_{unique_id()}", "description": "Do it"}
        ).json()["data"]

        response = client.post(
            "/api/v1/submissions",
            json={
                "assignment_id": assignment["assignment_id"],
                "student_id": student["student_id"],
                "answer": "Done"
            }
        )
        assert response.status_code == 201
        assert response.json()["data"]["submission_id"]

    def test_list_submissions(self, client):
        response = client.get("/api/v1/submissions")
        assert response.status_code == 200
        assert "submissions" in response.json()["data"]

    def test_grade_submission(self, client):
        student = client.post(
            "/api/v1/students",
            json={"login": f"s2_{unique_id()}", "name": "S2"}
        ).json()["data"]

        assignment = client.post(
            "/api/v1/assignments",
            json={"title": f"T2_{unique_id()}", "description": "T2"}
        ).json()["data"]

        submission = client.post(
            "/api/v1/submissions",
            json={
                "assignment_id": assignment["assignment_id"],
                "student_id": student["student_id"],
                "answer": "Answer"
            }
        ).json()["data"]

        response = client.patch(
            f"/api/v1/submissions/{submission['submission_id']}/grade",
            json={"grade": 90}
        )
        assert response.status_code == 200
        assert response.json()["data"]["grade"] == 90


class TestTestEndpoints:
    def test_create_test(self, client):
        response = client.post(
            "/api/v1/tests",
            json={
                "title": f"Quiz_{unique_id()}",
                "questions": [
                    {"prompt": "Q1?", "options": ["A", "B"], "correct_index": 0}
                ]
            }
        )
        assert response.status_code == 201
        assert response.json()["data"]["test_id"]

    def test_list_tests(self, client):
        client.post(
            "/api/v1/tests",
            json={
                "title": f"Test1_{unique_id()}",
                "questions": [{"prompt": "Q?", "options": ["Y", "N"], "correct_index": 1}]
            }
        )
        response = client.get("/api/v1/tests")
        assert response.status_code == 200

    def test_take_test(self, client):
        student = client.post(
            "/api/v1/students",
            json={"login": f"s3_{unique_id()}", "name": "S3"}
        ).json()["data"]

        test = client.post(
            "/api/v1/tests",
            json={
                "title": f"T1_{unique_id()}",
                "questions": [{"prompt": "Q", "options": ["A", "B"], "correct_index": 1}]
            }
        ).json()["data"]

        response = client.post(
            f"/api/v1/tests/{test['test_id']}/take",
            json={"student_id": student["student_id"], "answers": [1]}
        )
        assert response.status_code == 200
        assert "attempt_id" in response.json()["data"]

    def test_list_attempts(self, client):
        response = client.get("/api/v1/attempts")
        assert response.status_code == 200
        assert "attempts" in response.json()["data"]


class TestForumEndpoints:
    def test_create_thread(self, client):
        response = client.post(
            "/api/v1/threads",
            json={"title": f"Discussion_{unique_id()}"}
        )
        assert response.status_code == 201
        assert response.json()["data"]["thread_id"]

    def test_list_threads(self, client):
        client.post("/api/v1/threads", json={"title": f"Topic_{unique_id()}"})
        response = client.get("/api/v1/threads")
        assert response.status_code == 200

    def test_add_post(self, client):
        student = client.post(
            "/api/v1/students",
            json={"login": f"poster_{unique_id()}", "name": "Poster"}
        ).json()["data"]

        thread_resp = client.post(
            "/api/v1/threads",
            json={"title": f"Discussion_{unique_id()}"}
        )
        thread = thread_resp.json()["data"]

        response = client.post(
            f"/api/v1/threads/{thread['thread_id']}/posts",
            json={"author_id": student["student_id"], "content": "Great topic!"}
        )
        assert response.status_code == 201
        assert "author_id" in response.json()["data"]


class TestLectureEndpoints:
    def test_schedule_lecture(self, client):
        response = client.post(
            "/api/v1/lectures",
            json={"topic": f"Python Basics_{unique_id()}"}
        )
        assert response.status_code == 201
        assert response.json()["data"]["lecture_id"]

    def test_list_lectures(self, client):
        client.post("/api/v1/lectures", json={"topic": f"Topic1_{unique_id()}"})
        response = client.get("/api/v1/lectures")
        assert response.status_code == 200

    def test_start_lecture(self, client):
        lecture = client.post(
            "/api/v1/lectures",
            json={"topic": f"Live_{unique_id()}"}
        ).json()["data"]

        response = client.post(f"/api/v1/lectures/{lecture['lecture_id']}/start")
        assert response.status_code == 200
        assert response.json()["data"]["is_live"] is True

    def test_end_lecture(self, client):
        lecture = client.post(
            "/api/v1/lectures",
            json={"topic": f"Finish_{unique_id()}"}
        ).json()["data"]

        client.post(f"/api/v1/lectures/{lecture['lecture_id']}/start")
        response = client.post(f"/api/v1/lectures/{lecture['lecture_id']}/end")
        assert response.status_code == 200
        assert response.json()["data"]["is_live"] is False


class TestRootEndpoint:
    def test_root_returns_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "<!DOCTYPE html>" in response.text
        assert "Виртуальная кафедра" in response.text


class TestErrorHandling:
    def test_invalid_json(self, client):
        response = client.post(
            "/api/v1/students",
            json={"login": 123, "name": "Test"}
        )
        assert response.status_code == 422

    def test_grade_out_of_range(self, client):
        student = client.post(
            "/api/v1/students",
            json={"login": f"s4_{unique_id()}", "name": "S4"}
        ).json()["data"]

        assignment = client.post(
            "/api/v1/assignments",
            json={"title": f"T_{unique_id()}", "description": "D"}
        ).json()["data"]

        submission = client.post(
            "/api/v1/submissions",
            json={
                "assignment_id": assignment["assignment_id"],
                "student_id": student["student_id"],
                "answer": "A"
            }
        ).json()["data"]

        response = client.patch(
            f"/api/v1/submissions/{submission['submission_id']}/grade",
            json={"grade": 150}
        )
        assert response.status_code == 422

    def test_invalid_question_format(self, client):
        response = client.post(
            "/api/v1/tests",
            json={
                "title": f"Bad_{unique_id()}",
                "questions": [
                    {"prompt": "Q", "options": ["A"], "correct_index": 0}
                ]
            }
        )
        assert response.status_code == 422
