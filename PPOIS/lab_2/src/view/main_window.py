from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.model.entities import PatientRecord
from src.settings import DEFAULT_PAGE_SIZE


@dataclass
class _PaginationState:
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    total: int = 0
    current_count: int = 0

    @property
    def pages(self) -> int:
        if self.page_size <= 0:
            return 1
        return max(1, (self.total + self.page_size - 1) // self.page_size)


class MainWindow(QMainWindow):
    on_add: Optional[Callable[[], None]] = None
    on_search: Optional[Callable[[], None]] = None
    on_delete: Optional[Callable[[], None]] = None
    on_refresh: Optional[Callable[[], None]] = None
    on_export_xml: Optional[Callable[[Path], None]] = None
    on_import_xml: Optional[Callable[[Path, bool], None]] = None
    on_page_change: Optional[Callable[[], None]] = None
    on_page_size_change: Optional[Callable[[int], None]] = None

    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1100, 650)

        self._state = _PaginationState()

        self._stack = QStackedWidget()
        self._table = self._build_table()
        self._tree = self._build_tree()
        self._stack.addWidget(self._table)
        self._stack.addWidget(self._tree)

        self._pagination = self._build_pagination()

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(self._stack)
        layout.addLayout(self._pagination)
        self.setCentralWidget(root)

        self._build_menu_and_toolbar()
        self._set_view_mode("table")

    @property
    def page(self) -> int:
        return self._state.page

    def set_page(self, page: int) -> None:
        self._state.page = max(1, int(page))
        self._update_pagination_labels()

    def set_page_size(self, page_size: int) -> None:
        self._state.page_size = max(1, int(page_size))
        if self._page_size.value() != self._state.page_size:
            self._page_size.setValue(self._state.page_size)
        self._update_pagination_labels()

    def render_records(self, records: List[PatientRecord], total: int) -> None:
        self._state.total = int(total)
        self._state.current_count = len(records)
        self._render_table(records)
        self._render_tree(records)
        self._update_pagination_labels()

    def _build_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            ["ID", "ФИО пациента", "Адрес", "Дата рождения", "Дата приёма", "ФИО врача", "Заключение"]
        )
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _render_table(self, records: List[PatientRecord]) -> None:
        self._table.setRowCount(len(records))
        for i, r in enumerate(records):
            self._table.setItem(i, 0, QTableWidgetItem(str(r.id)))
            self._table.setItem(i, 1, QTableWidgetItem(r.patient_full_name))
            self._table.setItem(i, 2, QTableWidgetItem(r.address))
            self._table.setItem(i, 3, QTableWidgetItem(r.birth_date.isoformat()))
            self._table.setItem(i, 4, QTableWidgetItem(r.visit_date.isoformat()))
            self._table.setItem(i, 5, QTableWidgetItem(r.doctor_full_name))
            self._table.setItem(i, 6, QTableWidgetItem(r.conclusion))
        self._table.resizeColumnsToContents()

    def _build_tree(self) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderLabels(["Поле", "Значение"])
        tree.header().setStretchLastSection(True)
        return tree

    def _render_tree(self, records: List[PatientRecord]) -> None:
        self._tree.clear()
        for r in records:
            top = QTreeWidgetItem([f"Запись #{r.id}", ""])
            self._tree.addTopLevelItem(top)
            QTreeWidgetItem(top, ["ФИО пациента", r.patient_full_name])
            QTreeWidgetItem(top, ["Адрес", r.address])
            QTreeWidgetItem(top, ["Дата рождения", r.birth_date.isoformat()])
            QTreeWidgetItem(top, ["Дата приёма", r.visit_date.isoformat()])
            QTreeWidgetItem(top, ["ФИО врача", r.doctor_full_name])
            QTreeWidgetItem(top, ["Заключение", r.conclusion])
        self._tree.expandAll()

    def _build_pagination(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self._first = QPushButton("⏮")
        self._prev = QPushButton("◀")
        self._next = QPushButton("▶")
        self._last = QPushButton("⏭")
        for b in (self._first, self._prev, self._next, self._last):
            b.setFixedWidth(48)

        self._page_label = QLabel()
        self._page_count_label = QLabel()
        self._total_label = QLabel()

        self._page_size = QSpinBox()
        self._page_size.setRange(1, 500)
        self._page_size.setValue(self._state.page_size)
        self._page_size.setToolTip("Записей на странице")
        self._page_size.valueChanged.connect(lambda v: self.on_page_size_change and self.on_page_size_change(v))

        layout.addWidget(self._first)
        layout.addWidget(self._prev)
        layout.addWidget(self._next)
        layout.addWidget(self._last)
        layout.addSpacing(16)
        layout.addWidget(QLabel("На странице:"))
        layout.addWidget(self._page_size)
        layout.addSpacing(16)
        layout.addWidget(self._page_label)
        layout.addSpacing(16)
        layout.addWidget(self._page_count_label)
        layout.addSpacing(16)
        layout.addWidget(self._total_label)
        layout.addStretch(1)

        self._first.clicked.connect(self._go_first)
        self._prev.clicked.connect(self._go_prev)
        self._next.clicked.connect(self._go_next)
        self._last.clicked.connect(self._go_last)
        self._update_pagination_labels()
        return layout

    def _update_pagination_labels(self) -> None:
        pages = self._state.pages
        self._state.page = min(max(1, self._state.page), pages)
        self._page_label.setText(f"Страница {self._state.page} из {pages}")
        self._page_count_label.setText(f"На странице: {self._state.current_count}")
        self._total_label.setText(f"Всего записей: {self._state.total}")

        self._first.setEnabled(self._state.page > 1)
        self._prev.setEnabled(self._state.page > 1)
        self._next.setEnabled(self._state.page < pages)
        self._last.setEnabled(self._state.page < pages)

    def _go_first(self) -> None:
        self.set_page(1)
        if self.on_page_change:
            self.on_page_change()

    def _go_prev(self) -> None:
        self.set_page(self._state.page - 1)
        if self.on_page_change:
            self.on_page_change()

    def _go_next(self) -> None:
        self.set_page(self._state.page + 1)
        if self.on_page_change:
            self.on_page_change()

    def _go_last(self) -> None:
        self.set_page(self._state.pages)
        if self.on_page_change:
            self.on_page_change()

    def _build_menu_and_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        menu_file = self.menuBar().addMenu("Файл")
        menu_records = self.menuBar().addMenu("Записи")
        menu_view = self.menuBar().addMenu("Вид")

        def add_action(menu, text: str, callback) -> None:
            action = menu.addAction(text)
            action.triggered.connect(self._guard_ui_action(callback))
            toolbar.addAction(action)

        add_action(menu_file, "Экспорт в XML…", self._ui_export_xml)
        add_action(menu_file, "Импорт из XML…", self._ui_import_xml)
        menu_file.addSeparator()
        menu_file.addAction("Выход").triggered.connect(self.close)

        add_action(menu_records, "Добавить…", lambda: self.on_add and self.on_add())
        add_action(menu_records, "Поиск…", lambda: self.on_search and self.on_search())
        add_action(menu_records, "Удалить…", lambda: self.on_delete and self.on_delete())
        add_action(menu_records, "Обновить", lambda: self.on_refresh and self.on_refresh())

        add_action(menu_view, "Таблица", lambda: self._set_view_mode("table"))
        add_action(menu_view, "Дерево", lambda: self._set_view_mode("tree"))

    def _set_view_mode(self, mode: str) -> None:
        self._stack.setCurrentIndex(0 if mode == "table" else 1)

    def _ui_export_xml(self) -> None:
        if not self.on_export_xml:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить XML", filter="XML (*.xml)")
        if not filename:
            return
        self.on_export_xml(Path(filename))
        QMessageBox.information(self, "XML", "Экспорт выполнен.")

    def _ui_import_xml(self) -> None:
        if not self.on_import_xml:
            return
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть XML", filter="XML (*.xml)")
        if not filename:
            return
        reply = QMessageBox.question(
            self,
            "Импорт",
            "Заменить текущие записи? (Да — очистить БД, Нет — добавить к существующим)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        replace = reply == QMessageBox.StandardButton.Yes
        self.on_import_xml(Path(filename), replace)
        QMessageBox.information(self, "XML", "Импорт выполнен.")

    def _guard_ui_action(self, callback):
        def wrapped() -> None:
            try:
                callback()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"{type(e).__name__}: {e}")

        return wrapped
