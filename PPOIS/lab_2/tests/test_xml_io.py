from datetime import date

from src.model.entities import PatientRecord
from src.model.xml_io import export_records_to_xml_dom, import_records_from_xml_sax


def test_export_import_roundtrip(tmp_path):
    path = tmp_path / "patients.xml"
    export_records_to_xml_dom(
        path,
        [
            PatientRecord(
                id=1,
                patient_full_name="Иванов Иван",
                address="Минск",
                birth_date=date(2000, 1, 2),
                visit_date=date(2026, 3, 1),
                doctor_full_name="Петров",
                conclusion="ОК",
            )
        ],
    )
    imported = import_records_from_xml_sax(path)
    assert len(imported) == 1
    assert imported[0].patient_full_name == "Иванов Иван"
