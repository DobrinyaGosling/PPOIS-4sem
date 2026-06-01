from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, List, Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.model.entities import PatientRecord, SearchCriteria
from src.settings import DEFAULT_PAGE_SIZE


def _qdate_to_date(widget: QDateEdit) -> date:
    qd = widget.date()
    return date(qd.year(), qd.month(), qd.day())


@dataclass
class _Pager:
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    total: int = 0
    current_count: int = 0

    @property
    def pages(self) -> int:
        return max(1, (self.total + self.page_size - 1) // self.page_size) if self.page_size else 1


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")
        self.resize(520, 260)

        self.patient_full_name = QLineEdit()
        self.address = QLineEdit()
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("yyyy-MM-dd")
        self.visit_date = QDateEdit()
        self.visit_date.setCalendarPopup(True)
        self.visit_date.setDisplayFormat("yyyy-MM-dd")
        self.doctor_full_name = QLineEdit()
        self.conclusion = QLineEdit()

        form = QFormLayout()
        form.addRow("ФИО пациента:", self.patient_full_name)
        form.addRow("Адрес:", self.address)
        form.addRow("Дата рождения:", self.birth_date)
        form.addRow("Дата приёма:", self.visit_date)
        form.addRow("ФИО врача:", self.doctor_full_name)
        form.addRow("Заключение:", self.conclusion)

        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Отмена")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def result_data(self) -> Dict[str, object]:
        return {
            "patient_full_name": self.patient_full_name.text().strip(),
            "address": self.address.text().strip(),
            "birth_date": _qdate_to_date(self.birth_date),
            "visit_date": _qdate_to_date(self.visit_date),
            "doctor_full_name": self.doctor_full_name.text().strip(),
            "conclusion": self.conclusion.text().strip(),
        }


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удалить по условиям")
        self.resize(520, 220)

        self.patient_surname = QLineEdit()
        self.address = QLineEdit()
        self.birth_date_enabled = QCheckBox()
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("yyyy-MM-dd")
        self.birth_date.setEnabled(False)
        self.birth_date_enabled.toggled.connect(self.birth_date.setEnabled)

        self.doctor_name = QLineEdit()
        self.visit_date_enabled = QCheckBox()
        self.visit_date = QDateEdit()
        self.visit_date.setCalendarPopup(True)
        self.visit_date.setDisplayFormat("yyyy-MM-dd")
        self.visit_date.setEnabled(False)
        self.visit_date_enabled.toggled.connect(self.visit_date.setEnabled)

        birth_box = QWidget()
        birth_row = QHBoxLayout(birth_box)
        birth_row.setContentsMargins(0, 0, 0, 0)
        birth_row.addWidget(self.birth_date_enabled)
        birth_row.addWidget(self.birth_date)

        visit_box = QWidget()
        visit_row = QHBoxLayout(visit_box)
        visit_row.setContentsMargins(0, 0, 0, 0)
        visit_row.addWidget(self.visit_date_enabled)
        visit_row.addWidget(self.visit_date)

        form = QFormLayout()
        form.addRow("Фамилия пациента (с начала ФИО):", self.patient_surname)
        form.addRow("Адрес содержит:", self.address)
        form.addRow("Дата рождения (точно):", birth_box)
        form.addRow("ФИО врача содержит:", self.doctor_name)
        form.addRow("Дата приёма (точно):", visit_box)

        buttons = QHBoxLayout()
        ok = QPushButton("Удалить")
        cancel = QPushButton("Отмена")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def criteria_data(self) -> Dict[str, object]:
        return {
            "patient_surname": self.patient_surname.text().strip() or None,
            "address": self.address.text().strip() or None,
            "birth_date": _qdate_to_date(self.birth_date) if self.birth_date_enabled.isChecked() else None,
            "doctor_name": self.doctor_name.text().strip() or None,
            "visit_date": _qdate_to_date(self.visit_date) if self.visit_date_enabled.isChecked() else None,
        }


class SearchDialog(QDialog):
    on_search: Optional[Callable[[SearchCriteria, int, int], None]] = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск")
        self.resize(1100, 600)
        self._pager = _Pager()

        self.patient_surname = QLineEdit()
        self.address = QLineEdit()
        self.birth_date_enabled = QCheckBox()
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDisplayFormat("yyyy-MM-dd")
        self.birth_date.setEnabled(False)
        self.birth_date_enabled.toggled.connect(self.birth_date.setEnabled)

        self.doctor_name = QLineEdit()
        self.visit_date_enabled = QCheckBox()
        self.visit_date = QDateEdit()
        self.visit_date.setCalendarPopup(True)
        self.visit_date.setDisplayFormat("yyyy-MM-dd")
        self.visit_date.setEnabled(False)
        self.visit_date_enabled.toggled.connect(self.visit_date.setEnabled)

        birth_box = QWidget()
        birth_row = QHBoxLayout(birth_box)
        birth_row.setContentsMargins(0, 0, 0, 0)
        birth_row.addWidget(self.birth_date_enabled)
        birth_row.addWidget(self.birth_date)

        visit_box = QWidget()
        visit_row = QHBoxLayout(visit_box)
        visit_row.setContentsMargins(0, 0, 0, 0)
        visit_row.addWidget(self.visit_date_enabled)
        visit_row.addWidget(self.visit_date)

        form = QFormLayout()
        form.addRow("Фамилия пациента (с начала ФИО):", self.patient_surname)
        form.addRow("Адрес содержит:", self.address)
        form.addRow("Дата рождения (точно):", birth_box)
        form.addRow("ФИО врача содержит:", self.doctor_name)
        form.addRow("Дата приёма (точно):", visit_box)

        form_box = QWidget()
        form_box.setLayout(form)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО пациента", "Адрес", "Дата рождения", "Дата приёма", "ФИО врача", "Заключение"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.search_btn = QPushButton("Искать")
        self.search_btn.clicked.connect(self._run_search_first_page)

        criteria_row = QHBoxLayout()
        criteria_row.addWidget(self.search_btn)
        criteria_row.addStretch(1)

        self._first = QPushButton("⏮")
        self._prev = QPushButton("◀")
        self._next = QPushButton("▶")
        self._last = QPushButton("⏭")
        for b in (self._first, self._prev, self._next, self._last):
            b.setFixedWidth(48)

        self._page_size = QSpinBox()
        self._page_size.setRange(1, 500)
        self._page_size.setValue(self._pager.page_size)
        self._page_size.valueChanged.connect(self._on_page_size_changed)

        self._page_label = QLabel()
        self._page_count_label = QLabel()
        self._total_label = QLabel()

        pager = QHBoxLayout()
        pager.addWidget(self._first)
        pager.addWidget(self._prev)
        pager.addWidget(self._next)
        pager.addWidget(self._last)
        pager.addSpacing(16)
        pager.addWidget(QLabel("На странице:"))
        pager.addWidget(self._page_size)
        pager.addSpacing(16)
        pager.addWidget(self._page_label)
        pager.addSpacing(16)
        pager.addWidget(self._page_count_label)
        pager.addSpacing(16)
        pager.addWidget(self._total_label)
        pager.addStretch(1)

        self._first.clicked.connect(lambda: self._go_page(1))
        self._prev.clicked.connect(lambda: self._go_page(self._pager.page - 1))
        self._next.clicked.connect(lambda: self._go_page(self._pager.page + 1))
        self._last.clicked.connect(lambda: self._go_page(self._pager.pages))

        buttons = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(close_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(form_box)
        layout.addLayout(criteria_row)
        layout.addWidget(self.table)
        layout.addLayout(pager)
        layout.addLayout(buttons)

        self._update_labels()

    def _criteria(self) -> SearchCriteria:
        return SearchCriteria(
            patient_surname=self.patient_surname.text().strip() or None,
            address=self.address.text().strip() or None,
            birth_date=_qdate_to_date(self.birth_date) if self.birth_date_enabled.isChecked() else None,
            doctor_name=self.doctor_name.text().strip() or None,
            visit_date=_qdate_to_date(self.visit_date) if self.visit_date_enabled.isChecked() else None,
        )

    def _run_search_first_page(self) -> None:
        self._pager.page = 1
        self._run_search()

    def _run_search(self) -> None:
        if self.on_search:
            self.on_search(self._criteria(), self._pager.page, self._pager.page_size)

    def _go_page(self, page: int) -> None:
        self._pager.page = max(1, int(page))
        self._run_search()

    def _on_page_size_changed(self, value: int) -> None:
        self._pager.page_size = max(1, int(value))
        self._pager.page = 1
        self._run_search()

    def render_results(self, rows: List[PatientRecord], total: int) -> None:
        self._pager.total = int(total)
        self._pager.current_count = len(rows)
        self._pager.page = min(self._pager.page, self._pager.pages)

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(r.id)))
            self.table.setItem(i, 1, QTableWidgetItem(r.patient_full_name))
            self.table.setItem(i, 2, QTableWidgetItem(r.address))
            self.table.setItem(i, 3, QTableWidgetItem(r.birth_date.isoformat()))
            self.table.setItem(i, 4, QTableWidgetItem(r.visit_date.isoformat()))
            self.table.setItem(i, 5, QTableWidgetItem(r.doctor_full_name))
            self.table.setItem(i, 6, QTableWidgetItem(r.conclusion))
        self.table.resizeColumnsToContents()
        self._update_labels()

    def _update_labels(self) -> None:
        pages = self._pager.pages
        self._pager.page = min(max(1, self._pager.page), pages)
        self._page_label.setText(f"Страница {self._pager.page} из {pages}")
        self._page_count_label.setText(f"На странице: {self._pager.current_count}")
        self._total_label.setText(f"Всего найдено: {self._pager.total}")

        self._first.setEnabled(self._pager.page > 1)
        self._prev.setEnabled(self._pager.page > 1)
        self._next.setEnabled(self._pager.page < pages)
        self._last.setEnabled(self._pager.page < pages)
