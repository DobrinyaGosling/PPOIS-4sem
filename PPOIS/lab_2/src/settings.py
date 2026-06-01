from functools import lru_cache
import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"] = "DEV"

    HOST: str = ""
    PORT: str = ""

    DB_NAME: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_USER: str = ""
    DB_PASS: str = ""

    DATA_DIR: str = str(BASE_DIR / "data")
    STATE_FILE: str = "state.json"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def database_url(self) -> str:
        if self.MODE == "TEST":
            sqlite_path = os.getenv("TEST_SQLITE_PATH", "")
            if sqlite_path:
                path = Path(sqlite_path).expanduser().resolve()
                return f"sqlite+pysqlite:///{path.as_posix()}"
            return "sqlite+pysqlite:///:memory:"

        data_dir = Path(self.DATA_DIR).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = (data_dir / "patients.sqlite3").resolve()
        return f"sqlite+pysqlite:///{path.as_posix()}"

    @property
    def state_file_path(self) -> Path:
        data_dir = Path(self.DATA_DIR).expanduser()
        state_file = Path(self.STATE_FILE).expanduser()
        if not state_file.is_absolute():
            state_file = data_dir / state_file
        return state_file


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"

DEFAULT_PAGE_SIZE = 10
APP_TITLE = "lab_2 — Пациенты (вариант 5)"
