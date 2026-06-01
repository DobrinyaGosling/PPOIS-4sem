import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.model.department import VirtualDepartment


@dataclass(slots=True)
class JsonFileStorage:
    path: Path

    def load(self) -> VirtualDepartment:
        if not self.path.exists():
            return VirtualDepartment()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("State file must contain a JSON object")
        return VirtualDepartment.from_dict(raw)

    def save(self, dept: VirtualDepartment) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = dept.to_dict()
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
