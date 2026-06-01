from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional
from xml.dom import minidom
from xml.sax import handler, make_parser

from src.model.entities import PatientRecord, PatientRecordCreate


def export_records_to_xml_dom(path: Path, records: List[PatientRecord]) -> None:
    doc = minidom.Document()
    root = doc.createElement("patients")
    doc.appendChild(root)

    for record in records:
        node = doc.createElement("patient")
        node.setAttribute("id", str(record.id))

        def add_text(tag: str, value: str) -> None:
            el = doc.createElement(tag)
            el.appendChild(doc.createTextNode(value))
            node.appendChild(el)

        add_text("patient_full_name", record.patient_full_name)
        add_text("address", record.address)
        add_text("birth_date", record.birth_date.isoformat())
        add_text("visit_date", record.visit_date.isoformat())
        add_text("doctor_full_name", record.doctor_full_name)
        add_text("conclusion", record.conclusion)
        root.appendChild(node)

    path.write_text(doc.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8"), encoding="utf-8")


@dataclass
class _SaxPatient:
    patient_full_name: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    visit_date: Optional[date] = None
    doctor_full_name: Optional[str] = None
    conclusion: Optional[str] = None

    def to_create(self) -> PatientRecordCreate:
        return PatientRecordCreate(
            patient_full_name=self.patient_full_name or "",
            address=self.address or "",
            birth_date=self.birth_date or date.today(),
            visit_date=self.visit_date or date.today(),
            doctor_full_name=self.doctor_full_name or "",
            conclusion=self.conclusion or "",
        )


class _PatientsSaxHandler(handler.ContentHandler):
    def __init__(self) -> None:
        super().__init__()
        self.records: List[PatientRecordCreate] = []
        self._current: Optional[_SaxPatient] = None
        self._current_tag: Optional[str] = None
        self._buffer: List[str] = []

    def startElement(self, name: str, attrs) -> None:  # noqa: N802
        if name == "patient":
            self._current = _SaxPatient()
        self._current_tag = name
        self._buffer = []

    def characters(self, content: str) -> None:  # noqa: N802
        if self._current is None or self._current_tag is None:
            return
        self._buffer.append(content)

    def endElement(self, name: str) -> None:  # noqa: N802
        if self._current is None:
            return
        text = "".join(self._buffer).strip()
        if name == "patient":
            self.records.append(self._current.to_create())
            self._current = None
            self._current_tag = None
            self._buffer = []
            return

        if not text:
            self._current_tag = None
            self._buffer = []
            return

        if name == "patient_full_name":
            self._current.patient_full_name = text
        elif name == "address":
            self._current.address = text
        elif name == "birth_date":
            self._current.birth_date = date.fromisoformat(text)
        elif name == "visit_date":
            self._current.visit_date = date.fromisoformat(text)
        elif name == "doctor_full_name":
            self._current.doctor_full_name = text
        elif name == "conclusion":
            self._current.conclusion = text

        self._current_tag = None
        self._buffer = []


def import_records_from_xml_sax(path: Path) -> List[PatientRecordCreate]:
    parser = make_parser()
    sax_handler = _PatientsSaxHandler()
    parser.setContentHandler(sax_handler)
    with path.open("r", encoding="utf-8") as f:
        parser.parse(f)
    return sax_handler.records
