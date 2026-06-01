from src.model.department import VirtualDepartment
from src.model.entities import Student, Teacher
from src.model.exceptions import ValidationError
from src.view.utils import new_id


def create_student(dept: VirtualDepartment, login: str, name: str) -> Student:
    login = login.strip()
    name = name.strip()
    if not login or not name:
        raise ValidationError("login and name are required")
    if any(s.login == login for s in dept.students.values()):
        raise ValidationError(f"Student login '{login}' already exists")
    student_id = new_id("stu")
    student = Student(student_id=student_id, login=login, name=name)
    dept.students[student_id] = student
    return student


def create_teacher(dept: VirtualDepartment, login: str, name: str) -> Teacher:
    login = login.strip()
    name = name.strip()
    if not login or not name:
        raise ValidationError("login and name are required")
    if any(t.login == login for t in dept.teachers.values()):
        raise ValidationError(f"Teacher login '{login}' already exists")
    teacher_id = new_id("tea")
    teacher = Teacher(teacher_id=teacher_id, login=login, name=name)
    dept.teachers[teacher_id] = teacher
    return teacher


def list_students(dept: VirtualDepartment) -> list[Student]:
    return list(dept.students.values())


def list_teachers(dept: VirtualDepartment) -> list[Teacher]:
    return list(dept.teachers.values())
