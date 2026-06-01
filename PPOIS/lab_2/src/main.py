import asyncio
import sys

from PyQt6.QtWidgets import QApplication

from src.controller.gui_controller import GuiController
from src.model.db.init_db import init_db
from src.model.state import AppState
from src.settings import APP_TITLE, settings
from src.view.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    asyncio.run(init_db())
    state = AppState.load(settings.state_file_path)

    window = MainWindow(title=APP_TITLE)
    controller = GuiController(state=state, view=window)
    controller.bind()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
