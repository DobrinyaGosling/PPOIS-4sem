import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable, TypeVar

from pydantic import ValidationError
from PyQt6.QtWidgets import QDialog, QMessageBox

from src.model.entities import PatientRecordCreate, SearchCriteria
from src.model.db.DAO.patient import PatientDAO
from src.model.db.config import get_db_session
from src.model.exceptions import StorageError
from src.model.state import AppState
from src.model.xml_io import export_records_to_xml_dom, import_records_from_xml_sax
from src.settings import DEFAULT_PAGE_SIZE
from src.view.dialogs import AddDialog, DeleteDialog, SearchDialog
from src.view.main_window import MainWindow


T = TypeVar("T")


@dataclass(slots=True)
class GuiController:
    state: AppState
    view: MainWindow

    def bind(self) -> None:
        self.view.on_add = self.add_record
        self.view.on_search = self.open_search
        self.view.on_delete = self.open_delete
        self.view.on_refresh = self.refresh_main
        self.view.on_export_xml = self.export_xml
        self.view.on_import_xml = self.import_xml

        self.view.on_page_change = self.refresh_main
        self.view.on_page_size_change = self.on_page_size_change

        self.refresh_main()

    def on_page_size_change(self, page_size: int) -> None:
        self.state.page_size = max(1, int(page_size))
        self.state.save()
        self.view.set_page(1)
        self.refresh_main()

    def refresh_main(self) -> None:
        page_size = self.state.page_size or DEFAULT_PAGE_SIZE
        self.view.set_page_size(page_size)

        total = self._run_db(False, PatientDAO.count_all)
        pages = max(1, (total + page_size - 1) // page_size) if page_size else 1
        page = min(max(1, self.view.page), pages)
        self.view.set_page(page)
        records = self._run_db(False, lambda s: PatientDAO.list_page(s, page=page, page_size=page_size))
        self.view.render_records(records=records, total=total)

    def add_record(self) -> None:
        dialog = AddDialog(parent=self.view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            record = PatientRecordCreate(**dialog.result_data())
        except ValidationError as e:
            QMessageBox.warning(self.view, "Добавление", str(e))
            return
        self._run_db(True, lambda s: PatientDAO.add_record(s, record))
        self.refresh_main()

    def open_search(self) -> None:
        dialog = SearchDialog(parent=self.view)

        def run_search(criteria: SearchCriteria, page: int, page_size: int) -> None:
            total = self._run_db(False, lambda s: PatientDAO.count_search(s, criteria))
            rows = self._run_db(False, lambda s: PatientDAO.search_page(s, criteria, page=page, page_size=page_size))
            dialog.render_results(rows=rows, total=total)

        dialog.on_search = run_search
        dialog.exec()

    def open_delete(self) -> None:
        dialog = DeleteDialog(parent=self.view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            criteria = SearchCriteria(**dialog.criteria_data())
        except ValidationError as e:
            QMessageBox.warning(self.view, "Удаление", str(e))
            return
        try:
            deleted = self._run_db(True, lambda s: PatientDAO.delete_by_criteria(s, criteria))
        except StorageError as e:
            QMessageBox.warning(self.view, "Удаление", str(e))
            return
        else:
            QMessageBox.information(
                self.view,
                "Удаление",
                f"Удалено записей: {deleted}" if deleted else "Записей по условиям не найдено.",
            )
        self.refresh_main()

    def export_xml(self, path: Path) -> None:
        records = self._run_db(False, PatientDAO.list_all)
        export_records_to_xml_dom(path, records)

    def import_xml(self, path: Path, replace: bool) -> None:
        records = import_records_from_xml_sax(path)
        if replace:
            self._run_db(True, PatientDAO.clear)
        self._run_db(True, lambda s: PatientDAO.add_many(s, records))
        self.refresh_main()

    def _run_db(self, commit: bool, op: Callable[..., Awaitable[T]] | Callable[..., T]) -> T:
        async def runner() -> T:
            dep = get_db_session(commit)
            agen = dep()
            session = await agen.__anext__()
            try:
                result = op(session)
                if asyncio.iscoroutine(result):
                    result = await result  # type: ignore[assignment]
                try:
                    await agen.__anext__()  # run commit/close in dependency
                except StopAsyncIteration:
                    pass
                return result  # type: ignore[return-value]
            except Exception as e:
                try:
                    await agen.athrow(e)
                except StopAsyncIteration:
                    pass
                raise
            finally:
                await agen.aclose()

        return asyncio.run(runner())
