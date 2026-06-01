from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

from src.model.entities import (
    Assignment,
    ForumThread,
    Lecture,
    Material,
    Student,
    Submission,
    Teacher,
    Test,
    TestAttempt,
)


@dataclass(slots=True)
class VirtualDepartment:
    students: dict[str, Student] = field(default_factory=dict)
    teachers: dict[str, Teacher] = field(default_factory=dict)
    materials: dict[str, Material] = field(default_factory=dict)
    assignments: dict[str, Assignment] = field(default_factory=dict)
    submissions: dict[str, Submission] = field(default_factory=dict)
    tests: dict[str, Test] = field(default_factory=dict)
    attempts: dict[str, TestAttempt] = field(default_factory=dict)
    threads: dict[str, ForumThread] = field(default_factory=dict)
    lectures: dict[str, Lecture] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def dump(value: Any) -> Any:
            if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
                return value.to_dict()
            if is_dataclass(value):
                return asdict(value)
            return value

        return {
            "students": {k: dump(v) for k, v in self.students.items()},
            "teachers": {k: dump(v) for k, v in self.teachers.items()},
            "materials": {k: dump(v) for k, v in self.materials.items()},
            "assignments": {k: dump(v) for k, v in self.assignments.items()},
            "submissions": {k: dump(v) for k, v in self.submissions.items()},
            "tests": {k: dump(v) for k, v in self.tests.items()},
            "attempts": {k: dump(v) for k, v in self.attempts.items()},
            "threads": {k: dump(v) for k, v in self.threads.items()},
            "lectures": {k: dump(v) for k, v in self.lectures.items()},
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "VirtualDepartment":
        dept = VirtualDepartment()
        dept.students = {
            k: Student(
                student_id=v["student_id"],
                login=v.get("login", v["student_id"]),
                name=v["name"],
            )
            for k, v in data.get("students", {}).items()
        }
        dept.teachers = {
            k: Teacher(
                teacher_id=v["teacher_id"],
                login=v.get("login", v["teacher_id"]),
                name=v["name"],
            )
            for k, v in data.get("teachers", {}).items()
        }
        dept.materials = {k: Material(**v) for k, v in data.get("materials", {}).items()}
        dept.assignments = {k: Assignment(**v) for k, v in data.get("assignments", {}).items()}
        dept.submissions = {
            k: Submission.from_dict(v) for k, v in data.get("submissions", {}).items()
        }
        dept.tests = {k: Test.from_dict(v) for k, v in data.get("tests", {}).items()}
        dept.attempts = {
            k: TestAttempt.from_dict(v) for k, v in data.get("attempts", {}).items()
        }
        dept.threads = {
            k: ForumThread.from_dict(v) for k, v in data.get("threads", {}).items()
        }
        dept.lectures = {k: Lecture(**v) for k, v in data.get("lectures", {}).items()}
        return dept
