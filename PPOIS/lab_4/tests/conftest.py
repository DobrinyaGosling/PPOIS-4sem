import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import fastapi  # noqa: F401
except ModuleNotFoundError:
    venv_site = (
        PROJECT_ROOT
        / ".venv"
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    if venv_site.exists():
        sys.path.insert(0, str(venv_site))
from src.model.storage import JsonFileStorage
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
