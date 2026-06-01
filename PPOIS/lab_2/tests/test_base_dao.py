import asyncio
from datetime import date
from types import SimpleNamespace

from sqlalchemy.orm import selectinload

from src.model.db.DAO.base import BaseDAO
from src.model.db.config import get_async_session_maker
from src.model.db.init_db import init_db
from src.model.db.models import Patient


class DummyModel:
    __table__ = SimpleNamespace(name="dummy")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class DummyDAO(BaseDAO):
    model = Patient


class DummyAsyncResult:
    def __init__(self, one=None, rows=None):
        self._one = one
        self._rows = rows if rows is not None else []

    def scalar_one_or_none(self):
        return self._one

    def scalars(self):
        return SimpleNamespace(all=lambda: self._rows)


class DummyAsyncSession:
    def __init__(self):
        self.executed = []
        self.results = []
        self.added = []
        self.added_all = []
        self.refreshed = []

    async def execute(self, query):
        self.executed.append(query)
        return self.results.pop(0)

    def add(self, instance):
        self.added.append(instance)

    def add_all(self, instances):
        self.added_all.append(instances)

    async def refresh(self, instance):
        self.refreshed.append(instance)


def test_base_dao_async_paths():
    async def _run():
        await init_db()
        async with get_async_session_maker() as session:
            await session.execute(Patient.__table__.delete())
            await session.commit()

            created = await DummyDAO.add(
                session,
                patient_full_name="A",
                address="Minsk",
                birth_date=date(2000, 1, 1),
                visit_date=date(2026, 1, 1),
                doctor_full_name="D",
                conclusion="C",
            )
            await session.commit()
            await session.refresh(created)

            found = await DummyDAO.find_by_id(session, str(created.id))
            assert found is not None

            found2 = await DummyDAO.find_one_or_none(session, id=created.id)
            assert found2 is not None
            found3 = await DummyDAO.find_one_or_none(session, options=[selectinload("*")], id=created.id)
            assert found3 is not None

            rows = await DummyDAO.find_all(session, offset=0, limit=10, order_by=Patient.id, id=created.id)
            assert len(rows) == 1

            instances = await DummyDAO.add_all(
                session,
                [
                    dict(
                        patient_full_name="B",
                        address="Grodno",
                        birth_date=date(2001, 1, 1),
                        visit_date=date(2026, 2, 1),
                        doctor_full_name="E",
                        conclusion="OK",
                    )
                ],
            )
            assert len(instances) == 1
            await session.commit()

            updated = await DummyDAO.update(session, id=str(created.id), patient_full_name="A2")
            assert updated is not None and updated.patient_full_name == "A2"

            assert await DummyDAO.update(session, id="999999", patient_full_name="none") is None

            await DummyDAO.delete(session, id=created.id)
            await session.commit()
            assert await DummyDAO.find_by_id(session, str(created.id)) is None

    asyncio.run(_run())


def test_base_dao_sync_paths():
    class DummySyncSession:
        def __init__(self):
            self.added = []
            self._objects = {"1": DummyModel(id="1", patient_full_name="old")}

        def add(self, instance):
            self.added.append(instance)

        def get(self, model, id_):
            return self._objects[id_]

    session = DummySyncSession()
    created = DummyDAO.add_sync(
        session,
        patient_full_name="new",
        address="Minsk",
        birth_date=date(2000, 1, 1),
        visit_date=date(2026, 1, 1),
        doctor_full_name="Dr",
        conclusion="Ok",
    )
    assert created in session.added

    DummyDAO.update_sync(session, "1", patient_full_name="updated")
    assert session.get(DummyModel, "1").patient_full_name == "updated"

    found = DummyDAO.find_by_id_sync(session, "1")
    assert found.id == "1"


def test_base_dao_truncate_query():
    class DummyTruncateSession:
        def __init__(self):
            self.query = None

        async def execute(self, query):
            self.query = str(query)
            return None

    async def _run():
        session = DummyTruncateSession()
        await DummyDAO.truncate(session)
        assert 'TRUNCATE TABLE "patients" CASCADE' in session.query

    asyncio.run(_run())
