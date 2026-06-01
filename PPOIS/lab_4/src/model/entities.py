from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass(slots=True, frozen=True)
class Student:
    student_id: str
    login: str
    name: str


@dataclass(slots=True, frozen=True)
class Teacher:
    teacher_id: str
    login: str
    name: str


@dataclass(slots=True, frozen=True)
class Material:  # учебный материал
    material_id: str
    title: str
    content: str


@dataclass(slots=True, frozen=True)
class Assignment:  # задание
    assignment_id: str
    title: str
    description: str


@dataclass(slots=True)
class Submission:  # выполнение задание студентом
    submission_id: str
    assignment_id: str
    student_id: str
    answer: str | None = None
    grade: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "submission_id": self.submission_id,
            "assignment_id": self.assignment_id,
            "student_id": self.student_id,
            "answer": self.answer,
            "grade": self.grade,
        }

    @staticmethod
    def from_dict(v: dict[str, Any]) -> "Submission":
        return Submission(
            submission_id=v["submission_id"],
            assignment_id=v["assignment_id"],
            student_id=v["student_id"],
            answer=v.get("answer"),
            grade=v.get("grade"),
        )


@dataclass(slots=True, frozen=True)
class Question:  # вопрос в тесте
    prompt: str
    options: list[str]  # варианты ответа
    correct_index: int

    def validate(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Question prompt must be non-empty")
        if len(self.options) < 2:
            raise ValueError("Question must have at least 2 options")
        if not (0 <= self.correct_index < len(self.options)):
            raise ValueError("correct_index is out of range")


@dataclass(slots=True, frozen=True)
class Test:
    test_id: str
    title: str
    questions: list[Question]

    def validate(self) -> None:
        if not self.title.strip():
            raise ValueError("Test title must be non-empty")
        if not self.questions:
            raise ValueError("Test must contain questions")
        for q in self.questions:
            q.validate()

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "title": self.title,
            "questions": [
                {"prompt": q.prompt, "options": list(q.options), "correct_index": q.correct_index}
                for q in self.questions
            ],
        }

    @staticmethod
    def from_dict(v: dict[str, Any]) -> "Test":
        questions = [Question(**q) for q in v.get("questions", [])]
        return Test(test_id=v["test_id"], title=v["title"], questions=questions)


@dataclass(slots=True)
class TestAttempt:
    attempt_id: str
    test_id: str
    student_id: str
    answers: list[int] = field(default_factory=list)
    score: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_id": self.attempt_id,
            "test_id": self.test_id,
            "student_id": self.student_id,
            "answers": list(self.answers),
            "score": self.score,
        }

    @staticmethod
    def from_dict(v: dict[str, Any]) -> "TestAttempt":
        return TestAttempt(
            attempt_id=v["attempt_id"],
            test_id=v["test_id"],
            student_id=v["student_id"],
            answers=list(v.get("answers", [])),
            score=v.get("score"),
        )


@dataclass(slots=True, frozen=True)
class Post:
    author_id: str
    content: str
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class ForumThread:
    thread_id: str
    title: str
    posts: list[Post] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "posts": [
                {"author_id": p.author_id, "content": p.content, "created_at": p.created_at}
                for p in self.posts
            ],
        }

    @staticmethod
    def from_dict(v: dict[str, Any]) -> "ForumThread":
        posts = [Post(**p) for p in v.get("posts", [])]
        return ForumThread(thread_id=v["thread_id"], title=v["title"], posts=posts)


@dataclass(slots=True)
class Lecture:
    lecture_id: str
    topic: str
    is_live: bool = False
