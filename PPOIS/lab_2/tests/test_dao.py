import asyncio
from datetime import date

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.model.db.DAO.patient import PatientDAO
from src.model.db.config import get_async_session_maker
from src.model.db.init_db import init_db
from src.model.entities import PatientRecordCreate, SearchCriteria


async def _run() -> None:
    await init_db()
    async with get_async_session_maker() as session:
        await PatientDAO.clear(session)
        await session.commit()

        await PatientDAO.add_record(
            session,
            PatientRecordCreate(
                patient_full_name="Иванов Иван Иванович",
                address="Минск",
                birth_date=date(2000, 1, 2),
                visit_date=date(2026, 3, 1),
                doctor_full_name="Петров Пётр",
                conclusion="ОК",
            ),
        )
        await session.commit()

        assert await PatientDAO.count_all(session) == 1
        rows = await PatientDAO.search_page(session, SearchCriteria(patient_surname="Иванов"), page=1, page_size=10)
        assert rows and rows[0].address == "Минск"

        deleted = await PatientDAO.delete_by_criteria(session, SearchCriteria(address="Минск"))
        await session.commit()
        assert deleted == 1


def test_dao_smoke():
    try:
        asyncio.run(_run())
    except (SQLAlchemyError, ModuleNotFoundError) as e:
        pytest.skip(f"PostgreSQL недоступен для теста: {e}")
