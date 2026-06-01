import argparse

import json

from src.model.entities import Question
from src.model.exceptions import ValidationError
from src.view.cli_view import CliView
from src.view.use_cases.department import VirtualDepartmentService


def dispatch(args: argparse.Namespace, service: VirtualDepartmentService, view: CliView) -> int:
    cmd = args.cmd
    if cmd == "create-student":
        student = service.create_student(login=args.login, name=args.name)
        view.info(
            f"OK student_id={student.student_id} login={student.login} name={student.name}"
        )
        return 0
    if cmd == "create-teacher":
        teacher = service.create_teacher(login=args.login, name=args.name)
        view.info(
            f"OK teacher_id={teacher.teacher_id} login={teacher.login} name={teacher.name}"
        )
        return 0
    if cmd == "list-students":
        students = service.list_students()
        if not students:
            view.info("EMPTY")
            return 0
        for s in students:
            view.info(f"{s.student_id}\t{s.login}\t{s.name}")
        return 0
    if cmd == "list-teachers":
        teachers = service.list_teachers()
        if not teachers:
            view.info("EMPTY")
            return 0
        for t in teachers:
            view.info(f"{t.teacher_id}\t{t.login}\t{t.name}")
        return 0
    if cmd == "add-material":
        material = service.add_material(title=args.title, content=args.content)
        view.info(f"OK material_id={material.material_id} title={material.title}")
        return 0
    if cmd == "list-materials":
        materials = service.list_materials()
        if not materials:
            view.info("EMPTY")
            return 0
        for m in materials:
            view.info(f"{m.material_id}\t{m.title}")
        return 0
    if cmd == "add-assignment":
        assignment = service.add_assignment(title=args.title, description=args.description)
        view.info(f"OK assignment_id={assignment.assignment_id} title={assignment.title}")
        return 0
    if cmd == "list-assignments":
        assignments = service.list_assignments()
        if not assignments:
            view.info("EMPTY")
            return 0
        for a in assignments:
            view.info(f"{a.assignment_id}\t{a.title}")
        return 0
    if cmd == "list-submissions":
        submissions = service.list_submissions()
        if not submissions:
            view.info("EMPTY")
            return 0
        for s in submissions:
            grade = "" if s.grade is None else s.grade
            view.info(f"{s.submission_id}\t{s.assignment_id}\t{s.student_id}\t{grade}")
        return 0
    if cmd == "submit-assignment":
        submission = service.submit_assignment(
            assignment_id=args.assignment_id, student_id=args.student_id, answer=args.answer
        )
        view.info(f"OK submission_id={submission.submission_id}")
        return 0
    if cmd == "grade-submission":
        submission = service.grade_submission(submission_id=args.submission_id, grade=args.grade)
        view.info(f"OK submission_id={submission.submission_id} grade={submission.grade}")
        return 0
    if cmd == "create-test":
        try:
            raw = json.loads(args.questions_json)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid questions JSON: {e}") from e
        if not isinstance(raw, list):
            raise ValidationError("questions-json must be a JSON array")
        questions = [Question(**q) for q in raw]
        test = service.create_test(title=args.title, questions=questions)
        view.info(f"OK test_id={test.test_id} title={test.title}")
        return 0
    if cmd == "take-test":
        try:
            raw = json.loads(args.answers_json)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid answers JSON: {e}") from e
        if not isinstance(raw, list) or not all(isinstance(x, int) for x in raw):
            raise ValidationError("answers-json must be a JSON array of integers")
        attempt = service.take_test(test_id=args.test_id, student_id=args.student_id, answers=list(raw))
        view.info(f"OK attempt_id={attempt.attempt_id} score={attempt.score}")
        return 0
    if cmd == "list-tests":
        tests = service.list_tests()
        if not tests:
            view.info("EMPTY")
            return 0
        for t in tests:
            view.info(f"{t.test_id}\t{t.title}")
        return 0
    if cmd == "list-attempts":
        attempts = service.list_attempts()
        if not attempts:
            view.info("EMPTY")
            return 0
        for a in attempts:
            score = "" if a.score is None else a.score
            view.info(f"{a.attempt_id}\t{a.test_id}\t{a.student_id}\t{score}")
        return 0
    if cmd == "create-thread":
        thread = service.create_thread(title=args.title)
        view.info(f"OK thread_id={thread.thread_id} title={thread.title}")
        return 0
    if cmd == "post":
        post = service.add_post(thread_id=args.thread_id, author_id=args.author_id, content=args.content)
        view.info(f"OK author_id={post.author_id} created_at={post.created_at}")
        return 0
    if cmd == "list-threads":
        threads = service.list_threads()
        if not threads:
            view.info("EMPTY")
            return 0
        for t in threads:
            view.info(f"{t.thread_id}\t{t.title}\t{len(t.posts)}")
        return 0
    if cmd == "schedule-lecture":
        lecture = service.schedule_lecture(topic=args.topic)
        view.info(f"OK lecture_id={lecture.lecture_id} topic={lecture.topic}")
        return 0
    if cmd == "start-lecture":
        lecture = service.start_lecture(lecture_id=args.lecture_id)
        view.info(f"OK lecture_id={lecture.lecture_id} is_live={lecture.is_live}")
        return 0
    if cmd == "end-lecture":
        lecture = service.end_lecture(lecture_id=args.lecture_id)
        view.info(f"OK lecture_id={lecture.lecture_id} is_live={lecture.is_live}")
        return 0
    if cmd == "list-lectures":
        lectures = service.list_lectures()
        if not lectures:
            view.info("EMPTY")
            return 0
        for l in lectures:
            view.info(f"{l.lecture_id}\t{l.topic}\t{l.is_live}")
        return 0
    raise ValidationError(f"Unknown command: {cmd}")
