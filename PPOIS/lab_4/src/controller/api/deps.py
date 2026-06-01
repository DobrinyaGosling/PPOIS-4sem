from functools import lru_cache

from src.model.storage import JsonFileStorage
from src.settings import get_settings
from src.view.use_cases.department import VirtualDepartmentService


@lru_cache(maxsize=1)
def _default_service() -> VirtualDepartmentService:
    settings = get_settings()
    storage = JsonFileStorage(path=settings.state_file_path)
    return VirtualDepartmentService(storage=storage)


def get_service() -> VirtualDepartmentService:
    return _default_service()

