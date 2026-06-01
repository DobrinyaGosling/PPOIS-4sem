from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from pathlib import Path

from src.controller.api.deps import get_service
from src.controller.schemas import (
    AddAssignmentRequest,
    AddMaterialRequest,
    AddPostRequest,
    CreateStudentRequest,
    CreateTeacherRequest,
    CreateTestRequest,
    CreateThreadRequest,
    GradeSubmissionRequest,
    ScheduleLectureRequest,
    SubmitAssignmentRequest,
    SuccessResponse,
    TakeTestRequest,
)
from src.view.use_cases.department import VirtualDepartmentService

router = APIRouter(prefix="/api/v1")


def _ok(data: dict, message: str | None = None) -> SuccessResponse:
    return SuccessResponse(data=data, message=message)


@router.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(
    req: CreateStudentRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    student = service.create_student(login=req.login, name=req.name)
    return _ok(
        {"student_id": student.student_id, "login": student.login, "name": student.name},
        "Student created",
    )


@router.get("/students")
def list_students(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    students = service.list_students()
    return _ok(
        {
            "students": [
                {"student_id": s.student_id, "login": s.login, "name": s.name} for s in students
            ]
        }
    )


@router.post("/teachers", status_code=status.HTTP_201_CREATED)
def create_teacher(
    req: CreateTeacherRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    teacher = service.create_teacher(login=req.login, name=req.name)
    return _ok(
        {"teacher_id": teacher.teacher_id, "login": teacher.login, "name": teacher.name},
        "Teacher created",
    )


@router.get("/teachers")
def list_teachers(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    teachers = service.list_teachers()
    return _ok(
        {"teachers": [{"teacher_id": t.teacher_id, "login": t.login, "name": t.name} for t in teachers]}
    )


@router.post("/materials", status_code=status.HTTP_201_CREATED)
def add_material(
    req: AddMaterialRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    material = service.add_material(title=req.title, content=req.content)
    return _ok({"material_id": material.material_id, "title": material.title}, "Material added")


@router.get("/materials")
def list_materials(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    materials = service.list_materials()
    return _ok(
        {"materials": [{"material_id": m.material_id, "title": m.title} for m in materials]}
    )


@router.post("/assignments", status_code=status.HTTP_201_CREATED)
def add_assignment(
    req: AddAssignmentRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    assignment = service.add_assignment(title=req.title, description=req.description)
    return _ok(
        {"assignment_id": assignment.assignment_id, "title": assignment.title},
        "Assignment added",
    )


@router.get("/assignments")
def list_assignments(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    assignments = service.list_assignments()
    return _ok(
        {"assignments": [{"assignment_id": a.assignment_id, "title": a.title} for a in assignments]}
    )


@router.get("/submissions")
def list_submissions(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    submissions = service.list_submissions()
    return _ok(
        {
            "submissions": [
                {
                    "submission_id": s.submission_id,
                    "assignment_id": s.assignment_id,
                    "student_id": s.student_id,
                    "answer": s.answer,
                    "grade": s.grade,
                }
                for s in submissions
            ]
        }
    )


@router.post("/submissions", status_code=status.HTTP_201_CREATED)
def submit_assignment(
    req: SubmitAssignmentRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    submission = service.submit_assignment(
        assignment_id=req.assignment_id, student_id=req.student_id, answer=req.answer
    )
    return _ok({"submission_id": submission.submission_id}, "Assignment submitted")


@router.patch("/submissions/{submission_id}/grade")
def grade_submission(
    submission_id: str,
    req: GradeSubmissionRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    submission = service.grade_submission(submission_id=submission_id, grade=req.grade)
    return _ok({"submission_id": submission.submission_id, "grade": submission.grade}, "Grade updated")


@router.post("/tests", status_code=status.HTTP_201_CREATED)
def create_test(
    req: CreateTestRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    from src.model.entities import Question

    questions = [Question(**q.model_dump()) for q in req.questions]
    test = service.create_test(title=req.title, questions=questions)
    return _ok({"test_id": test.test_id, "title": test.title}, "Test created")


@router.get("/tests")
def list_tests(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    tests = service.list_tests()
    return _ok({"tests": [{"test_id": t.test_id, "title": t.title} for t in tests]})


@router.post("/tests/{test_id}/take")
def take_test(
    test_id: str,
    req: TakeTestRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    attempt = service.take_test(test_id=test_id, student_id=req.student_id, answers=req.answers)
    return _ok({"attempt_id": attempt.attempt_id, "score": attempt.score}, "Test completed")


@router.get("/attempts")
def list_attempts(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    attempts = service.list_attempts()
    return _ok(
        {
            "attempts": [
                {
                    "attempt_id": a.attempt_id,
                    "test_id": a.test_id,
                    "student_id": a.student_id,
                    "score": a.score,
                }
                for a in attempts
            ]
        }
    )


@router.post("/threads", status_code=status.HTTP_201_CREATED)
def create_thread(
    req: CreateThreadRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    thread = service.create_thread(title=req.title)
    return _ok({"thread_id": thread.thread_id, "title": thread.title}, "Thread created")


@router.get("/threads")
def list_threads(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    threads = service.list_threads()
    return _ok(
        {
            "threads": [
                {"thread_id": t.thread_id, "title": t.title, "posts_count": len(t.posts)}
                for t in threads
            ]
        }
    )


@router.post("/threads/{thread_id}/posts", status_code=status.HTTP_201_CREATED)
def add_post(
    thread_id: str,
    req: AddPostRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    post = service.add_post(thread_id=thread_id, author_id=req.author_id, content=req.content)
    return _ok(
        {"author_id": post.author_id, "created_at": post.created_at, "content": post.content},
        "Post added",
    )


@router.post("/lectures", status_code=status.HTTP_201_CREATED)
def schedule_lecture(
    req: ScheduleLectureRequest,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    lecture = service.schedule_lecture(topic=req.topic)
    return _ok({"lecture_id": lecture.lecture_id, "topic": lecture.topic}, "Lecture scheduled")


@router.post("/lectures/{lecture_id}/start")
def start_lecture(
    lecture_id: str,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    lecture = service.start_lecture(lecture_id=lecture_id)
    return _ok({"lecture_id": lecture.lecture_id, "is_live": lecture.is_live}, "Lecture started")


@router.post("/lectures/{lecture_id}/end")
def end_lecture(
    lecture_id: str,
    service: VirtualDepartmentService = Depends(get_service),
) -> SuccessResponse:
    lecture = service.end_lecture(lecture_id=lecture_id)
    return _ok({"lecture_id": lecture.lecture_id, "is_live": lecture.is_live}, "Lecture ended")


@router.get("/lectures")
def list_lectures(service: VirtualDepartmentService = Depends(get_service)) -> SuccessResponse:
    lectures = service.list_lectures()
    return _ok(
        {
            "lectures": [
                {"lecture_id": l.lecture_id, "topic": l.topic, "is_live": l.is_live}
                for l in lectures
            ]
        }
    )

