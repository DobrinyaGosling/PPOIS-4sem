import json
from dataclasses import dataclass
from pathlib import Path

from src.settings import DEFAULT_PAGE_SIZE


@dataclass(slots=True)
class AppState:
    state_path: Path
    page_size: int = DEFAULT_PAGE_SIZE

    @classmethod
    def load(cls, state_path: Path) -> "AppState":
        state_path.parent.mkdir(parents=True, exist_ok=True)
        if not state_path.exists():
            state = cls(state_path=state_path, page_size=DEFAULT_PAGE_SIZE)
            state.save()
            return state
        data = json.loads(state_path.read_text(encoding="utf-8") or "{}")
        page_size = int(data.get("page_size") or DEFAULT_PAGE_SIZE)
        return cls(state_path=state_path, page_size=page_size)

    def save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"page_size": int(self.page_size)}
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
