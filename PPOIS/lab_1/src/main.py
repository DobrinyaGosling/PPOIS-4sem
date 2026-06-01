import sys

from src.controller.cli_controller import CliController
from src.model.storage import JsonFileStorage
from src.settings import get_settings
from src.view.cli_view import CliView
from src.view.use_cases.department import VirtualDepartmentService


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    settings = get_settings()
    storage = JsonFileStorage(path=settings.state_file_path)
    service = VirtualDepartmentService(storage=storage)
    view = CliView(out=sys.stdout, err=sys.stderr)
    controller = CliController(service=service, view=view)
    return controller.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
