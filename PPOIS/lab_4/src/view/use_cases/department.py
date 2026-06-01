from dataclasses import dataclass

from src.model.department import VirtualDepartment
from src.model.entities import Question
from src.model.storage import JsonFileStorage
from src.view.use_cases import (
    assignments,
    forum,
    lectures,
    materials,
    quizzes,
    students,
)


@dataclass(slots=True)
class VirtualDepartmentService:
    storage: JsonFileStorage

    def load(self) -> VirtualDepartment:
        return self.storage.load()

    def save(self, dept: VirtualDepartment) -> None:
        self.storage.save(dept)

    def create_student(self, login: str, name: str):
        dept = self.load()
        student = students.create_student(dept, login=login, name=name)
        self.save(dept)
        return student

    def create_teacher(self, login: str, name: str):
        dept = self.load()
        teacher = students.create_teacher(dept, login=login, name=name)
        self.save(dept)
        return teacher

    def add_material(self, title: str, content: str):
        dept = self.load()
        material = materials.add_material(dept, title=title, content=content)
        self.save(dept)
        return material

    def list_materials(self):
        dept = self.load()
        return materials.list_materials(dept)

    def list_students(self):
        dept = self.load()
        return students.list_students(dept)

    def list_teachers(self):
        dept = self.load()
        return students.list_teachers(dept)

    def add_assignment(self, title: str, description: str):
        dept = self.load()
        assignment = assignments.add_assignment(dept, title=title, description=description)
        self.save(dept)
        return assignment

    def submit_assignment(self, assignment_id: str, student_id: str, answer: str):
        dept = self.load()
        submission = assignments.submit_assignment(
            dept, assignment_id=assignment_id, student_id=student_id, answer=answer
        )
        self.save(dept)
        return submission

    def grade_submission(self, submission_id: str, grade: int):
        dept = self.load()
        submission = assignments.grade_submission(dept, submission_id=submission_id, grade=grade)
        self.save(dept)
        return submission

    def list_assignments(self):
        dept = self.load()
        return assignments.list_assignments(dept)

    def list_submissions(self):
        dept = self.load()
        return assignments.list_submissions(dept)

    def create_test(self, title: str, questions: list[Question]):
        dept = self.load()
        test = quizzes.create_test(dept, title=title, questions=questions)
        self.save(dept)
        return test

    def take_test(self, test_id: str, student_id: str, answers: list[int]):
        dept = self.load()
        attempt = quizzes.take_test(dept, test_id=test_id, student_id=student_id, answers=answers)
        self.save(dept)
        return attempt

    def list_tests(self):
        dept = self.load()
        return quizzes.list_tests(dept)

    def list_attempts(self):
        dept = self.load()
        return quizzes.list_attempts(dept)

    def create_thread(self, title: str):
        dept = self.load()
        thread = forum.create_thread(dept, title=title)
        self.save(dept)
        return thread

    def add_post(self, thread_id: str, author_id: str, content: str):
        dept = self.load()
        post = forum.add_post(dept, thread_id=thread_id, author_id=author_id, content=content)
        self.save(dept)
        return post

    def list_threads(self):
        dept = self.load()
        return forum.list_threads(dept)

    def schedule_lecture(self, topic: str):
        dept = self.load()
        lecture = lectures.schedule_lecture(dept, topic=topic)
        self.save(dept)
        return lecture

    def start_lecture(self, lecture_id: str):
        dept = self.load()
        lecture = lectures.start_lecture(dept, lecture_id=lecture_id)
        self.save(dept)
        return lecture

    def end_lecture(self, lecture_id: str):
        dept = self.load()
        lecture = lectures.end_lecture(dept, lecture_id=lecture_id)
        self.save(dept)
        return lecture

    def list_lectures(self):
        dept = self.load()
        return lectures.list_lectures(dept)
