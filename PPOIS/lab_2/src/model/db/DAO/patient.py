from typing import List, Sequence, Tuple

from sqlalchemy import and_, delete, func, select

from src.model.db.DAO.base import BaseDAO
from src.model.db.config import AsyncSessionShim
from src.model.db.models import Patient
from src.model.entities import PatientRecord, PatientRecordCreate, SearchCriteria
from src.model.exceptions import StorageError


class PatientDAO(BaseDAO):
    model = Patient

    @staticmethod
    def _to_record(row: Patient) -> PatientRecord:
        return PatientRecord(
            id=row.id,
            patient_full_name=row.patient_full_name,
            address=row.address,
            birth_date=row.birth_date,
            visit_date=row.visit_date,
            doctor_full_name=row.doctor_full_name,
            conclusion=row.conclusion,
        )

    @classmethod
    def _filters(cls, criteria: SearchCriteria) -> Sequence[object]:
        filters: List[object] = []
        if criteria.patient_surname:
            filters.append(cls.model.patient_full_name.ilike(criteria.patient_surname.strip() + "%"))
        if criteria.address:
            filters.append(cls.model.address.ilike("%" + criteria.address.strip() + "%"))
        if criteria.birth_date:
            filters.append(cls.model.birth_date == criteria.birth_date)
        if criteria.doctor_name:
            filters.append(cls.model.doctor_full_name.ilike("%" + criteria.doctor_name.strip() + "%"))
        if criteria.visit_date:
            filters.append(cls.model.visit_date == criteria.visit_date)
        return filters

    @classmethod
    async def add_record(cls, session: AsyncSessionShim, record: PatientRecordCreate) -> PatientRecord:
        instance = await cls.add(
            session,
            patient_full_name=record.patient_full_name.strip(),
            address=record.address.strip(),
            birth_date=record.birth_date,
            visit_date=record.visit_date,
            doctor_full_name=record.doctor_full_name.strip(),
            conclusion=record.conclusion.strip(),
        )
        await session.flush()
        await session.refresh(instance)
        return cls._to_record(instance)

    @classmethod
    async def add_many(cls, session: AsyncSessionShim, records: List[PatientRecordCreate]) -> int:
        if not records:
            return 0
        rows = [
            dict(
                patient_full_name=r.patient_full_name.strip(),
                address=r.address.strip(),
                birth_date=r.birth_date,
                visit_date=r.visit_date,
                doctor_full_name=r.doctor_full_name.strip(),
                conclusion=r.conclusion.strip(),
            )
            for r in records
        ]
        await cls.add_all(session, rows)
        await session.flush()
        return len(records)

    @classmethod
    async def list_page(cls, session: AsyncSessionShim, page: int, page_size: int) -> List[PatientRecord]:
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        offset = (page - 1) * page_size
        q = select(cls.model).order_by(cls.model.id.desc()).offset(offset).limit(page_size)
        result = await session.execute(q)
        return [cls._to_record(r) for r in result.scalars().all()]

    @classmethod
    async def list_all(cls, session: AsyncSessionShim) -> List[PatientRecord]:
        q = select(cls.model).order_by(cls.model.id.desc())
        result = await session.execute(q)
        return [cls._to_record(r) for r in result.scalars().all()]

    @classmethod
    async def count_all(cls, session: AsyncSessionShim) -> int:
        result = await session.execute(select(func.count(cls.model.id)))
        return int(result.scalar_one())

    @classmethod
    async def search_page(
        cls, session: AsyncSessionShim, criteria: SearchCriteria, page: int, page_size: int
    ) -> List[PatientRecord]:
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        offset = (page - 1) * page_size
        filters = list(cls._filters(criteria))
        where = and_(*filters) if filters else None
        q = select(cls.model)
        if where is not None:
            q = q.where(where)
        q = q.order_by(cls.model.id.desc()).offset(offset).limit(page_size)
        result = await session.execute(q)
        return [cls._to_record(r) for r in result.scalars().all()]

    @classmethod
    async def count_search(cls, session: AsyncSessionShim, criteria: SearchCriteria) -> int:
        filters = list(cls._filters(criteria))
        where = and_(*filters) if filters else None
        q = select(func.count(cls.model.id))
        if where is not None:
            q = q.where(where)
        result = await session.execute(q)
        return int(result.scalar_one())

    @classmethod
    async def delete_by_criteria(cls, session: AsyncSessionShim, criteria: SearchCriteria) -> int:
        filters = list(cls._filters(criteria))
        if not filters:
            raise StorageError("Нельзя удалять без условий.")
        q = delete(cls.model).where(and_(*filters))
        result = await session.execute(q)
        return int(result.rowcount or 0)

    @classmethod
    async def clear(cls, session: AsyncSessionShim) -> None:
        await session.execute(delete(cls.model))
