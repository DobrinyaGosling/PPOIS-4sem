from io import StringIO
from pathlib import Path

import pytest

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.controller.cli_controller import CliController
from src.model.storage import JsonFileStorage
from src.view.cli_view import CliView
from src.view.use_cases.department import VirtualDepartmentService


@pytest.fixture()
def state_path(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


@pytest.fixture()
def storage(state_path: Path) -> JsonFileStorage:
    return JsonFileStorage(path=state_path)


@pytest.fixture()
def service(storage: JsonFileStorage) -> VirtualDepartmentService:
    return VirtualDepartmentService(storage=storage)


@pytest.fixture()
def view() -> tuple[CliView, StringIO, StringIO]:
    out = StringIO()
    err = StringIO()
    return CliView(out=out, err=err), out, err


@pytest.fixture()
def controller(service: VirtualDepartmentService, view: tuple[CliView, StringIO, StringIO]) -> CliController:
    v, _, _ = view
    return CliController(service=service, view=v)
