import re
from io import StringIO

import pytest

from src.controller.cli_controller import CliController
from src.view.cli_view import CliView
from src.view.use_cases.department import VirtualDepartmentService


def _kv(text: str, key: str) -> str:
    m = re.search(rf"{re.escape(key)}=([^\s]+)", text)
    assert m, f"Missing {key} in: {text}"
    return m.group(1)


def test_controller_create_and_list_materials(
    controller: CliController, view: tuple[CliView, StringIO, StringIO]
) -> None:
    v, out, err = view
    rc = controller.run(["list-materials"])
    assert rc == 0
    assert out.getvalue().strip() == "EMPTY"
    assert err.getvalue() == ""

    out.truncate(0)
    out.seek(0)
    rc = controller.run(["add-material", "--title", "Intro", "--content", "Text"])
    assert rc == 0
    line = out.getvalue().strip()
    assert "OK material_id=" in line

    out.truncate(0)
    out.seek(0)
    rc = controller.run(["list-materials"])
    assert rc == 0
    assert "\tIntro" in out.getvalue()


def test_controller_list_students_teachers(controller: CliController, view) -> None:
    _, out, _ = view
    rc = controller.run(["list-students"])
    assert rc == 0
    assert out.getvalue().strip() == "EMPTY"

    out.truncate(0)
    out.seek(0)
    controller.run(["create-student", "--login", "ivan", "--name", "Ivan"])
    out.truncate(0)
    out.seek(0)
    rc = controller.run(["list-students"])
    assert rc == 0
    assert "ivan" in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["create-teacher", "--login", "petrov", "--name", "Petrov"])
    out.truncate(0)
    out.seek(0)
    rc = controller.run(["list-teachers"])
    assert rc == 0
    assert "petrov" in out.getvalue()


def test_controller_assignment_flow(controller: CliController, service: VirtualDepartmentService, view) -> None:
    _, out, _ = view
    controller.run(["create-student", "--login", "ivan", "--name", "Ivan"])
    student_id = _kv(out.getvalue(), "student_id")
    out.truncate(0)
    out.seek(0)
    controller.run(["add-assignment", "--title", "Lab", "--description", "Do it"])
    asg_id = _kv(out.getvalue(), "assignment_id")

    out.truncate(0)
    out.seek(0)
    controller.run(
        [
            "submit-assignment",
            "--assignment-id",
            asg_id,
            "--student-id",
            student_id,
            "--answer",
            "Ans",
        ]
    )
    sub_id = _kv(out.getvalue(), "submission_id")

    out.truncate(0)
    out.seek(0)
    controller.run(["grade-submission", "--submission-id", sub_id, "--grade", "90"])
    assert "grade=90" in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["list-assignments"])
    assert asg_id in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["list-submissions"])
    assert sub_id in out.getvalue()


def test_controller_test_flow(controller: CliController, view) -> None:
    _, out, _ = view
    controller.run(["create-student", "--login", "ivan", "--name", "Ivan"])
    student_id = _kv(out.getvalue(), "student_id")
    out.truncate(0)
    out.seek(0)
    rc = controller.run(
        [
            "create-test",
            "--title",
            "Quiz",
            "--questions-json",
            '[{"prompt":"2+2?","options":["3","4"],"correct_index":1}]',
        ]
    )
    assert rc == 0
    test_id = _kv(out.getvalue(), "test_id")

    out.truncate(0)
    out.seek(0)
    controller.run(
        ["take-test", "--test-id", test_id, "--student-id", student_id, "--answers-json", "[1]"]
    )
    assert "score=1" in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["list-tests"])
    assert test_id in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["list-attempts"])
    assert "att_" in out.getvalue()


def test_controller_forum_and_lecture(controller: CliController, view) -> None:
    _, out, _ = view
    controller.run(["create-teacher", "--login", "petrov", "--name", "Petrov"])
    teacher_id = _kv(out.getvalue(), "teacher_id")

    out.truncate(0)
    out.seek(0)
    controller.run(["create-thread", "--title", "Q&A"])
    thread_id = _kv(out.getvalue(), "thread_id")

    out.truncate(0)
    out.seek(0)
    controller.run(["post", "--thread-id", thread_id, "--author-id", teacher_id, "--content", "Hello"])
    assert f"OK author_id={teacher_id}" in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["schedule-lecture", "--topic", "SOLID"])
    lec_id = _kv(out.getvalue(), "lecture_id")

    out.truncate(0)
    out.seek(0)
    controller.run(["start-lecture", "--lecture-id", lec_id])
    assert "is_live=True" in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["end-lecture", "--lecture-id", lec_id])
    assert "is_live=False" in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["list-threads"])
    assert thread_id in out.getvalue()

    out.truncate(0)
    out.seek(0)
    controller.run(["list-lectures"])
    assert lec_id in out.getvalue()


def test_controller_errors(controller: CliController, view) -> None:
    _, out, err = view
    rc = controller.run(["create-test", "--title", "x", "--questions-json", "not-json"])
    assert rc == 2
    assert out.getvalue() == ""
    assert "Invalid questions JSON" in err.getvalue()


def test_controller_no_args_shows_help(controller: CliController, view) -> None:
    _, out, err = view
    import os

    os.environ["VDEPT_NO_REPL"] = "1"
    rc = controller.run([])
    os.environ.pop("VDEPT_NO_REPL", None)
    assert rc == 0
    assert "usage: vdept" in out.getvalue()
    assert err.getvalue() == ""


def test_controller_no_args_tty_enters_repl_and_exits(controller: CliController, view, monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    rc = controller.run([])
    assert rc == 0


def test_controller_create_test_questions_not_array(controller: CliController, view) -> None:
    _, out, err = view
    rc = controller.run(["create-test", "--title", "x", "--questions-json", "{}"])
    assert rc == 2
    assert out.getvalue() == ""
    assert "questions-json must be a JSON array" in err.getvalue()


def test_controller_answer_test_invalid_inputs(controller: CliController, view) -> None:
    _, out, err = view
    rc = controller.run(["take-test", "--test-id", "t1", "--student-id", "s1", "--answers-json", "not-json"])
    assert rc == 2
    assert out.getvalue() == ""
    assert "Invalid answers JSON" in err.getvalue()

    out.truncate(0)
    out.seek(0)
    err.truncate(0)
    err.seek(0)
    rc = controller.run(["take-test", "--test-id", "t1", "--student-id", "s1", "--answers-json", '["x"]'])
    assert rc == 2
    assert "answers-json must be a JSON array of integers" in err.getvalue()


def test_controller_unknown_command_branch(controller: CliController, view) -> None:
    import argparse

    from src.controller.routing import dispatch
    from src.model.exceptions import ValidationError

    _ = view
    with pytest.raises(ValidationError):
        dispatch(argparse.Namespace(cmd="unknown"), controller.service, controller.view)
