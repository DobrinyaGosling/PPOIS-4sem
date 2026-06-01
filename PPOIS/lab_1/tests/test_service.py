import pytest

from src.model.entities import Question
from src.model.exceptions import NotFoundError, ValidationError
from src.view.use_cases.department import VirtualDepartmentService


def test_create_student_and_teacher(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    t = service.create_teacher("petrov", "Petrov")
    assert s.login == "ivan"
    assert t.login == "petrov"


def test_create_student_duplicate(service: VirtualDepartmentService) -> None:
    service.create_student("ivan", "Ivan")
    with pytest.raises(ValidationError):
        service.create_student("ivan", "Ivan 2")


def test_create_student_validation(service: VirtualDepartmentService) -> None:
    with pytest.raises(ValidationError):
        service.create_student("", "X")
    with pytest.raises(ValidationError):
        service.create_student("ivan", "")


def test_materials(service: VirtualDepartmentService) -> None:
    assert service.list_materials() == []
    m = service.add_material("Intro", "Text")
    mats = service.list_materials()
    assert mats[0].material_id == m.material_id


def test_list_students_teachers(service: VirtualDepartmentService) -> None:
    assert service.list_students() == []
    assert service.list_teachers() == []
    s = service.create_student("ivan", "Ivan")
    t = service.create_teacher("petrov", "Petrov")
    assert service.list_students()[0].student_id == s.student_id
    assert service.list_teachers()[0].teacher_id == t.teacher_id


def test_add_material_validation(service: VirtualDepartmentService) -> None:
    with pytest.raises(ValidationError):
        service.add_material("", "x")
    with pytest.raises(ValidationError):
        service.add_material("t", "")


def test_assignment_submit_and_grade(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    a = service.add_assignment("Lab", "Do it")
    sub = service.submit_assignment(
        assignment_id=a.assignment_id, student_id=s.student_id, answer="Answer"
    )
    assert sub.assignment_id == a.assignment_id
    assert sub.student_id == s.student_id
    assert sub.answer == "Answer"
    assert sub.grade is None

    sub2 = service.grade_submission(submission_id=sub.submission_id, grade=100)
    assert sub2.grade == 100
    assert service.list_assignments()[0].assignment_id == a.assignment_id
    assert service.list_submissions()[0].submission_id == sub.submission_id


def test_submit_assignment_validation_and_not_found(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    a = service.add_assignment("Lab", "Do it")
    with pytest.raises(ValidationError):
        service.submit_assignment(assignment_id=a.assignment_id, student_id=s.student_id, answer="  ")
    with pytest.raises(NotFoundError):
        service.submit_assignment(assignment_id="missing", student_id=s.student_id, answer="x")
    with pytest.raises(NotFoundError):
        service.submit_assignment(assignment_id=a.assignment_id, student_id="missing", answer="x")


def test_grade_validation_and_not_found(service: VirtualDepartmentService) -> None:
    with pytest.raises(ValidationError):
        service.grade_submission(submission_id="x", grade=101)
    with pytest.raises(NotFoundError):
        service.grade_submission(submission_id="missing", grade=10)


def test_test_create_and_take(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    q = Question(prompt="2+2?", options=["3", "4"], correct_index=1)
    test = service.create_test("Quiz", [q])
    attempt = service.take_test(test_id=test.test_id, student_id=s.student_id, answers=[1])
    assert attempt.score == 1
    assert service.list_tests()[0].test_id == test.test_id
    assert service.list_attempts()[0].attempt_id == attempt.attempt_id


def test_test_invalid_answers(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    q = Question(prompt="2+2?", options=["3", "4"], correct_index=1)
    test = service.create_test("Quiz", [q])
    with pytest.raises(ValidationError):
        service.take_test(test_id=test.test_id, student_id=s.student_id, answers=[2])
    with pytest.raises(ValidationError):
        service.take_test(test_id=test.test_id, student_id=s.student_id, answers=[])


def test_test_not_found(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    q = Question(prompt="p", options=["a", "b"], correct_index=0)
    test = service.create_test("Quiz", [q])
    with pytest.raises(NotFoundError):
        service.take_test(test_id="missing", student_id=s.student_id, answers=[0])
    with pytest.raises(NotFoundError):
        service.take_test(test_id=test.test_id, student_id="missing", answers=[0])


def test_test_validation_error(service: VirtualDepartmentService) -> None:
    with pytest.raises(ValidationError):
        service.create_test("", [Question(prompt="p", options=["a", "b"], correct_index=0)])
    with pytest.raises(ValidationError):
        service.create_test("Quiz", [])


def test_question_validation_errors() -> None:
    with pytest.raises(ValueError):
        Question(prompt="", options=["a", "b"], correct_index=0).validate()
    with pytest.raises(ValueError):
        Question(prompt="p", options=["a"], correct_index=0).validate()
    with pytest.raises(ValueError):
        Question(prompt="p", options=["a", "b"], correct_index=2).validate()


def test_forum_thread_and_post(service: VirtualDepartmentService) -> None:
    s = service.create_student("ivan", "Ivan")
    thr = service.create_thread("Q&A")
    post = service.add_post(thread_id=thr.thread_id, author_id=s.student_id, content="Hello")
    assert post.author_id == s.student_id
    assert "T" in post.created_at
    assert service.list_threads()[0].thread_id == thr.thread_id


def test_forum_post_author_not_found(service: VirtualDepartmentService) -> None:
    thr = service.create_thread("Q&A")
    with pytest.raises(NotFoundError):
        service.add_post(thread_id=thr.thread_id, author_id="unknown", content="x")


def test_forum_validation_errors(service: VirtualDepartmentService) -> None:
    with pytest.raises(ValidationError):
        service.create_thread("  ")
    s = service.create_student("ivan", "Ivan")
    thr = service.create_thread("Q&A")
    with pytest.raises(ValidationError):
        service.add_post(thread_id=thr.thread_id, author_id=s.student_id, content=" ")
    with pytest.raises(NotFoundError):
        service.add_post(thread_id="missing", author_id="s1", content="x")


def test_lecture_workflow(service: VirtualDepartmentService) -> None:
    lec = service.schedule_lecture("SOLID")
    assert lec.is_live is False
    lec = service.start_lecture(lecture_id=lec.lecture_id)
    assert lec.is_live is True
    lec = service.end_lecture(lecture_id=lec.lecture_id)
    assert lec.is_live is False
    assert service.list_lectures()[0].lecture_id == lec.lecture_id
