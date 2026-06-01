import runpy
import sys
import types
from datetime import date

from src.model.xml_io import import_records_from_xml_sax


def test_xml_sax_empty_text_branch(tmp_path):
    xml = """<?xml version="1.0" encoding="utf-8"?>
<patients>
  <patient>
    <patient_full_name>Иванов Иван</patient_full_name>
    <unused_tag></unused_tag>
    <address>Минск</address>
    <birth_date>2000-01-02</birth_date>
    <visit_date>2026-03-01</visit_date>
    <doctor_full_name>Петров</doctor_full_name>
    <conclusion>ОК</conclusion>
  </patient>
</patients>
"""
    path = tmp_path / "in.xml"
    path.write_text(xml, encoding="utf-8")
    rows = import_records_from_xml_sax(path)
    assert len(rows) == 1
    assert rows[0].address == "Минск"
    assert rows[0].birth_date == date(2000, 1, 2)


def _install_main_stubs(exec_code=7):
    qtwidgets = types.ModuleType("PyQt6.QtWidgets")

    class DummyQApplication:
        def __init__(self, argv):
            self.argv = argv
            self.app_name = None

        def setApplicationName(self, name):
            self.app_name = name

        def exec(self):
            return exec_code

    qtwidgets.QApplication = DummyQApplication
    pyqt6 = types.ModuleType("PyQt6")
    pyqt6.QtWidgets = qtwidgets

    gui_controller_module = types.ModuleType("src.controller.gui_controller")

    class DummyController:
        def __init__(self, state, view):
            self.state = state
            self.view = view
            self.bound = False

        def bind(self):
            self.bound = True

    gui_controller_module.GuiController = DummyController

    init_db_module = types.ModuleType("src.model.db.init_db")

    async def init_db():
        return None

    init_db_module.init_db = init_db

    state_module = types.ModuleType("src.model.state")

    class AppState:
        @staticmethod
        def load(path):
            return {"state_path": path}

    state_module.AppState = AppState

    settings_module = types.ModuleType("src.settings")
    settings_module.APP_TITLE = "Test App"
    settings_module.settings = types.SimpleNamespace(state_file_path="/tmp/state.json")

    view_module = types.ModuleType("src.view.main_window")

    class MainWindow:
        def __init__(self, title):
            self.title = title
            self.shown = False

        def show(self):
            self.shown = True

    view_module.MainWindow = MainWindow

    stubs = {
        "PyQt6": pyqt6,
        "PyQt6.QtWidgets": qtwidgets,
        "src.controller.gui_controller": gui_controller_module,
        "src.model.db.init_db": init_db_module,
        "src.model.state": state_module,
        "src.settings": settings_module,
        "src.view.main_window": view_module,
    }
    original = {name: sys.modules.get(name) for name in stubs}
    sys.modules.update(stubs)
    return original


def _restore_modules(original):
    for name, module in original.items():
        if module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module


def test_main_function_and_entrypoint():
    original = _install_main_stubs(exec_code=11)
    try:
        module = runpy.run_path("src/main.py", run_name="main_for_test")
        assert module["main"]() == 11
    finally:
        _restore_modules(original)


def test_main_dunder_main_raises_system_exit():
    original = _install_main_stubs(exec_code=13)
    try:
        try:
            runpy.run_path("src/main.py", run_name="__main__")
            assert False
        except SystemExit as exc:
            assert exc.code == 13
    finally:
        _restore_modules(original)
