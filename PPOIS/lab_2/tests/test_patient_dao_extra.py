import asyncio
from datetime import date

import pytest

from src.model.db.DAO.patient import PatientDAO
from src.model.db.config import get_async_session_maker
from src.model.db.init_db import init_db
from src.model.entities import PatientRecordCreate, SearchCriteria
from src.model.exceptions import StorageError


def test_patient_dao_extra_paths():
    async def _run():
        await init_db()
        async with get_async_session_maker() as session:
            await PatientDAO.clear(session)
            await session.commit()

            empty_inserted = await PatientDAO.add_many(session, [])
            assert empty_inserted == 0

            inserted = await PatientDAO.add_many(
                session,
                [
                    PatientRecordCreate(
                        patient_full_name="Иванов Иван Иванович",
                        address="Минск",
                        birth_date=date(2000, 1, 2),
                        visit_date=date(2026, 3, 1),
                        doctor_full_name="Петров Пётр",
                        conclusion="ОК",
                    ),
                    PatientRecordCreate(
                        patient_full_name="Сидоров Сидор Сидорович",
                        address="Гродно",
                        birth_date=date(1999, 5, 6),
                        visit_date=date(2026, 4, 2),
                        doctor_full_name="Иванова Анна",
                        conclusion="Нормально",
                    ),
                ],
            )
            await session.commit()
            assert inserted == 2

            all_count = await PatientDAO.count_all(session)
            assert all_count == 2

            page = await PatientDAO.list_page(session, page=0, page_size=0)
            assert len(page) == 1

            all_rows = await PatientDAO.list_all(session)
            assert len(all_rows) == 2

            criteria_full = SearchCriteria(
                patient_surname="Иванов",
                address="Минск",
                birth_date=date(2000, 1, 2),
                doctor_name="Пётр",
                visit_date=date(2026, 3, 1),
            )
            assert len(PatientDAO._filters(criteria_full)) == 5

            assert await PatientDAO.count_search(session, SearchCriteria()) == 2
            assert await PatientDAO.count_search(session, criteria_full) == 1

            with pytest.raises(StorageError):
                await PatientDAO.delete_by_criteria(session, SearchCriteria())

    asyncio.run(_run())
