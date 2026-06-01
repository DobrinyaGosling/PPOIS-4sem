import shlex

from src.controller.parsing import build_parser
from src.model.exceptions import DomainError
from src.view.cli_view import CliView
from src.view.use_cases.department import VirtualDepartmentService
from src.controller.routing import dispatch


def run_repl(service: VirtualDepartmentService, view: CliView):
    parser = build_parser(out=view.out, err=view.err)
    while True:
        try:
            line = input("vdept> ").strip()
        except (EOFError, KeyboardInterrupt):
            view.info("")
            return 0

        if not line:
            continue
        if line in {"exit", "quit"}:
            return 0
        if line == "help":
            parser.print_help(view.out)
            continue

        try:
            argv = shlex.split(line)
            args = parser.parse_args(argv)

            dispatch(args, service, view)
        except SystemExit:
            continue
        except DomainError as e:
            view.error(f"ERROR: {e}")
            continue
