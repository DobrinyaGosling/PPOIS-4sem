from src.model.department import VirtualDepartment
from src.model.entities import Question, Test, TestAttempt
from src.model.exceptions import NotFoundError, ValidationError
from src.view.utils import new_id


def create_test(dept: VirtualDepartment, title: str, questions: list[Question]) -> Test:
    title = title.strip()
    test = Test(test_id=new_id("tst"), title=title, questions=questions)
    try:
        test.validate()
    except ValueError as e:
        raise ValidationError(str(e)) from e
    dept.tests[test.test_id] = test
    return test


def take_test(dept: VirtualDepartment, test_id: str, student_id: str, answers: list[int]) -> TestAttempt:
    if student_id not in dept.students:
        raise NotFoundError(f"Student '{student_id}' not found")
    test = dept.tests.get(test_id)
    if test is None:
        raise NotFoundError(f"Test '{test_id}' not found")
    if len(answers) != len(test.questions):
        raise ValidationError("answers count must match questions count")
    for idx, ans in enumerate(answers):
        if not (0 <= ans < len(test.questions[idx].options)):
            raise ValidationError(f"answer index out of range for question {idx}")
    score = sum(1 for q, a in zip(test.questions, answers, strict=True) if q.correct_index == a)
    attempt = TestAttempt(
        attempt_id=new_id("att"),
        test_id=test_id,
        student_id=student_id,
        answers=list(answers),
        score=score,
    )
    dept.attempts[attempt.attempt_id] = attempt
    return attempt


def list_tests(dept: VirtualDepartment) -> list[Test]:
    return list(dept.tests.values())


def list_attempts(dept: VirtualDepartment) -> list[TestAttempt]:
    return list(dept.attempts.values())
