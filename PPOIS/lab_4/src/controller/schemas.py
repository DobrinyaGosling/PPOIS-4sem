from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SuccessResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    data: dict


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
    message: str
    details: Optional[dict] = None


# === Request Models ===
class CreateStudentRequest(BaseModel):
    login: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)


class CreateTeacherRequest(BaseModel):
    login: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)


class AddMaterialRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class AddAssignmentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)


class SubmitAssignmentRequest(BaseModel):
    assignment_id: str
    student_id: str
    answer: str = Field(..., min_length=1)


class GradeSubmissionRequest(BaseModel):
    grade: int = Field(..., ge=0, le=100)  # int, не float!

class QuestionIn(BaseModel):
    prompt: str = Field(..., min_length=1)
    options: list[str] = Field(..., min_length=2)
    correct_index: int = Field(..., ge=0)

    @field_validator("options")
    @classmethod
    def _validate_options(cls, v: list[str]) -> list[str]:
        if any(not isinstance(x, str) or not x.strip() for x in v):
            raise ValueError("options must be non-empty strings")
        if len(v) < 2:
            raise ValueError("options must contain at least 2 items")
        return v

    @field_validator("correct_index")
    @classmethod
    def _validate_correct_index(cls, v: int, info) -> int:
        options = info.data.get("options") if info and hasattr(info, "data") else None
        if isinstance(options, list) and not (0 <= v < len(options)):
            raise ValueError("correct_index out of range")
        return v


class CreateTestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    questions: list[QuestionIn] = Field(..., min_length=1)


class TakeTestRequest(BaseModel):
    student_id: str
    answers: list[int] = Field(..., min_length=1)

    @field_validator("answers")
    @classmethod
    def _validate_answers(cls, v: list[int]) -> list[int]:
        if any(not isinstance(x, int) for x in v):
            raise ValueError("answers must be integers")
        return v


class CreateThreadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class AddPostRequest(BaseModel):
    author_id: str
    content: str = Field(..., min_length=1)


class ScheduleLectureRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)


class LectureActionRequest(BaseModel): ...
