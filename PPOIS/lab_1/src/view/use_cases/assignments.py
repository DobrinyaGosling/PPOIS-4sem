from src.model.department import VirtualDepartment
from src.model.entities import Assignment, Submission
from src.model.exceptions import NotFoundError, ValidationError
from src.view.utils import new_id


def add_assignment(dept: VirtualDepartment, title: str, description: str) -> Assignment:
    title = title.strip()
    description = description.strip()
    if not title or not description:
        raise ValidationError("title and description are required")
    assignment = Assignment(assignment_id=new_id("asg"), title=title, description=description)
    dept.assignments[assignment.assignment_id] = assignment
    return assignment


def submit_assignment(dept: VirtualDepartment, assignment_id: str, student_id: str, answer: str) -> Submission:
    assignment_id = assignment_id.strip()
    student_id = student_id.strip()
    answer = answer.strip()
    if student_id not in dept.students:
        raise NotFoundError(f"Student '{student_id}' not found")
    if assignment_id not in dept.assignments:
        raise NotFoundError(f"Assignment '{assignment_id}' not found")
    if not answer:
        raise ValidationError("answer is required")
    submission = Submission(
        submission_id=new_id("sub"),
        assignment_id=assignment_id,
        student_id=student_id,
        answer=answer,
        grade=None,
    )
    dept.submissions[submission.submission_id] = submission
    return submission


def grade_submission(dept: VirtualDepartment, submission_id: str, grade: int) -> Submission:
    if not (0 <= grade <= 100):
        raise ValidationError("grade must be between 0 and 100")
    submission = dept.submissions.get(submission_id)
    if submission is None:
        raise NotFoundError(f"Submission '{submission_id}' not found")
    submission.grade = grade
    return submission


def list_assignments(dept: VirtualDepartment) -> list[Assignment]:
    return list(dept.assignments.values())


def list_submissions(dept: VirtualDepartment) -> list[Submission]:
    return list(dept.submissions.values())
