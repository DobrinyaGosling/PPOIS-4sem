import importlib
from pathlib import Path

from src import settings as settings_module


def _reload_settings() -> None:
    settings_module.get_settings.cache_clear()
    importlib.reload(settings_module)


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.delenv("STATE_FILE", raising=False)
    _reload_settings()
    s = settings_module.get_settings()
    assert s.DATA_DIR == "data"
    assert s.STATE_FILE == "state.json"
    assert s.state_file_path == Path("data") / "state.json"


def test_settings_env_absolute_state_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "x.json"))
    _reload_settings()
    s = settings_module.get_settings()
    assert s.state_file_path == tmp_path / "x.json"


def test_settings_env_relative_state_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("STATE_FILE", "rel.json")
    _reload_settings()
    s = settings_module.get_settings()
    assert s.state_file_path == tmp_path / "rel.json"


def test_database_url(monkeypatch) -> None:
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASS", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "db")
    _reload_settings()
    s = settings_module.get_settings()
    assert s.database_url == "postgresql+asyncpg://u:p@h:5432/db"


def test_settings_cached_instance(monkeypatch) -> None:
    _reload_settings()
    a = settings_module.get_settings()
    b = settings_module.get_settings()
    assert a is b
