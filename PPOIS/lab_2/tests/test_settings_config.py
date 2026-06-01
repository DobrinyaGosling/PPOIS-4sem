import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.model.db import config as db_config
from src.settings import Settings, get_settings


def test_settings_database_url_test_mode_with_file(monkeypatch, tmp_path):
    sqlite_path = tmp_path / "db.sqlite3"
    monkeypatch.setenv("TEST_SQLITE_PATH", str(sqlite_path))
    settings = Settings(MODE="TEST")
    assert settings.database_url == f"sqlite+pysqlite:///{sqlite_path.resolve().as_posix()}"


def test_settings_database_url_test_mode_memory(monkeypatch):
    monkeypatch.delenv("TEST_SQLITE_PATH", raising=False)
    settings = Settings(MODE="TEST")
    assert settings.database_url == "sqlite+pysqlite:///:memory:"


def test_settings_database_url_dev_creates_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    settings = Settings(MODE="DEV", DATA_DIR=str(data_dir))
    assert settings.database_url.endswith("/patients.sqlite3")
    assert data_dir.exists()


def test_settings_state_file_path_relative_and_absolute(tmp_path):
    settings_rel = Settings(DATA_DIR=str(tmp_path), STATE_FILE="state.json")
    assert settings_rel.state_file_path == tmp_path / "state.json"

    absolute = tmp_path / "custom.json"
    settings_abs = Settings(DATA_DIR=str(tmp_path), STATE_FILE=str(absolute))
    assert settings_abs.state_file_path == absolute


def test_get_settings_cache():
    a = get_settings()
    b = get_settings()
    assert a is b


def test_get_engine_sqlite_kwargs(monkeypatch):
    db_config.get_engine.cache_clear()
    monkeypatch.setattr(db_config, "settings", SimpleNamespace(database_url="sqlite+pysqlite:///x.db"))
    captured = {}

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(db_config, "create_engine", fake_create_engine)
    db_config.get_engine()
    assert captured["url"].startswith("sqlite")
    assert captured["kwargs"]["connect_args"]["check_same_thread"] is False


def test_get_engine_non_sqlite_kwargs(monkeypatch):
    db_config.get_engine.cache_clear()
    monkeypatch.setattr(db_config, "settings", SimpleNamespace(database_url="postgresql://u:p@h:1/db"))
    captured = {}

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(db_config, "create_engine", fake_create_engine)
    db_config.get_engine()
    assert captured["url"].startswith("postgresql")
    assert captured["kwargs"] == {}


def test_async_session_shim_methods():
    class DummySession:
        def __init__(self):
            self.closed = 0
            self.commits = 0
            self.rollbacks = 0
            self.flushes = 0
            self.refreshed = None
            self.executed = None
            self.foo = "bar"

        def execute(self, *args, **kwargs):
            self.executed = (args, kwargs)
            return 123

        def commit(self):
            self.commits += 1

        def rollback(self):
            self.rollbacks += 1

        def close(self):
            self.closed += 1

        def flush(self):
            self.flushes += 1

        def refresh(self, instance):
            self.refreshed = instance

    async def _run():
        base = DummySession()
        shim = db_config.AsyncSessionShim(base)
        async with shim as session:
            assert session.foo == "bar"
            assert await session.execute("select 1") == 123
            await session.commit()
            await session.rollback()
            await session.flush()
            marker = object()
            await session.refresh(marker)
            await session.close()
        assert base.commits == 1
        assert base.rollbacks == 1
        assert base.flushes == 1
        assert base.refreshed is marker
        assert base.closed == 2

    asyncio.run(_run())


def test_get_db_session_commit_path(monkeypatch):
    class DummySession:
        def __init__(self):
            self.committed = 0
            self.rolled_back = 0
            self.closed = 0

        async def commit(self):
            self.committed += 1

        async def rollback(self):
            self.rolled_back += 1

        async def close(self):
            self.closed += 1

    class DummyFactory:
        def __init__(self):
            self.session = DummySession()

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(db_config, "get_async_session_maker", lambda: DummyFactory())

    async def _run():
        dep = db_config.get_db_session(commit=True)
        agen = dep()
        session = await agen.__anext__()
        assert session is not None
        with pytest.raises(StopAsyncIteration):
            await agen.__anext__()
        assert session.committed == 1
        assert session.rolled_back == 0
        assert session.closed == 1

    asyncio.run(_run())


def test_get_db_session_rollback_path(monkeypatch):
    class DummySession:
        def __init__(self):
            self.committed = 0
            self.rolled_back = 0
            self.closed = 0

        async def commit(self):
            self.committed += 1

        async def rollback(self):
            self.rolled_back += 1

        async def close(self):
            self.closed += 1

    class DummyFactory:
        def __init__(self):
            self.session = DummySession()

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(db_config, "get_async_session_maker", lambda: DummyFactory())

    async def _run():
        dep = db_config.get_db_session(commit=False)
        agen = dep()
        session = await agen.__anext__()
        with pytest.raises(RuntimeError):
            await agen.athrow(RuntimeError("boom"))
        assert session.committed == 0
        assert session.rolled_back == 1
        assert session.closed == 1

    asyncio.run(_run())
