from src.model.department import VirtualDepartment
from src.model.entities import Lecture
from src.model.exceptions import NotFoundError, ValidationError
from src.view.utils import new_id


def schedule_lecture(dept: VirtualDepartment, topic: str) -> Lecture:
    topic = topic.strip()
    if not topic:
        raise ValidationError("topic is required")
    lecture = Lecture(lecture_id=new_id("lec"), topic=topic, is_live=False)
    dept.lectures[lecture.lecture_id] = lecture
    return lecture


def start_lecture(dept: VirtualDepartment, lecture_id: str) -> Lecture:
    lecture = dept.lectures.get(lecture_id)
    if lecture is None:
        raise NotFoundError(f"Lecture '{lecture_id}' not found")
    lecture.is_live = True
    return lecture


def end_lecture(dept: VirtualDepartment, lecture_id: str) -> Lecture:
    lecture = dept.lectures.get(lecture_id)
    if lecture is None:
        raise NotFoundError(f"Lecture '{lecture_id}' not found")
    lecture.is_live = False
    return lecture


def list_lectures(dept: VirtualDepartment) -> list[Lecture]:
    return list(dept.lectures.values())
