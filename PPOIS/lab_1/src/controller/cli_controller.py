import os
from dataclasses import dataclass
from typing import Sequence

from src.controller.parsing import build_parser
from src.controller.repl import run_repl
from src.controller.routing import dispatch
from src.model.exceptions import DomainError
from src.view.cli_view import CliView
from src.view.use_cases.department import VirtualDepartmentService


@dataclass(slots=True)
class CliController:
    service: VirtualDepartmentService
    view: CliView

    def run(self, argv: Sequence[str]) -> int:
        if not list(argv):
            if os.getenv("VDEPT_NO_REPL", "").strip() == "1":
                parser = build_parser(out=self.view.out, err=self.view.err)
                parser.print_help(self.view.out)
                return 0
            return run_repl(self.service, self.view)

        parser = build_parser(out=self.view.out, err=self.view.err)
        try:
            args = parser.parse_args(list(argv))
        except SystemExit as e:
            return int(getattr(e, "code", 2) or 2)

        try:
            return dispatch(args, self.service, self.view)
        except DomainError as e:
            self.view.error(f"ERROR: {e}")
            return 2
