from functools import lru_cache
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

    DATA_DIR: str = "data"
    STATE_FILE: str = "state.json"

    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

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
