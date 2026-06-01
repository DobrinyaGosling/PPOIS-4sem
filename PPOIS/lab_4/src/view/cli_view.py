from dataclasses import dataclass
from typing import TextIO


@dataclass(slots=True)
class CliView:
    out: TextIO
    err: TextIO

    def info(self, message: str) -> None:
        self.out.write(message + "\n")

    def error(self, message: str) -> None:
        self.err.write(message + "\n")
