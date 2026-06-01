from io import StringIO
from pathlib import Path

from src import main
from src import settings as settings_module


def test_main_runs_list_materials(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("STATE_FILE", "state.json")
    settings_module.get_settings.cache_clear()
    out = StringIO()
    err = StringIO()
    monkeypatch.setattr(main.sys, "stdout", out)
    monkeypatch.setattr(main.sys, "stderr", err)
    rc = main.main(["list-materials"])
    assert rc == 0
    assert out.getvalue().strip() == "EMPTY"
    assert err.getvalue() == ""
