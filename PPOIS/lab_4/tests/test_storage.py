import json
from pathlib import Path

from src.model.department import VirtualDepartment
from src.model.entities import Assignment, Material, Student
from src.model.storage import JsonFileStorage


def test_storage_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    storage = JsonFileStorage(path=path)
    dept = VirtualDepartment()
    dept.students["s1"] = Student(student_id="s1", login="ivan", name="Ivan")
    dept.materials["m1"] = Material(material_id="m1", title="T", content="C")
    dept.assignments["a1"] = Assignment(assignment_id="a1", title="A", description="D")
    storage.save(dept)

    loaded = storage.load()
    assert loaded.students["s1"].name == "Ivan"
    assert loaded.materials["m1"].title == "T"
    assert loaded.assignments["a1"].description == "D"

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)


def test_storage_load_missing_file(tmp_path: Path) -> None:
    storage = JsonFileStorage(path=tmp_path / "nope.json")
    state = storage.load()
    assert state.students == {}


def test_storage_rejects_non_object_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('["not-an-object"]', encoding="utf-8")
    storage = JsonFileStorage(path=path)
    try:
        storage.load()
        raise AssertionError("Expected ValueError")
    except ValueError as e:
        assert "JSON object" in str(e)
