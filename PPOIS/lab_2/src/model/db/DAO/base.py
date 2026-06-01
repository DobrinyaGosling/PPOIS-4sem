from sqlalchemy import delete, select, text, update
from sqlalchemy.orm import Session, selectinload

from src.model.db.config import AsyncSessionShim


class BaseDAO:
    model = None

    @classmethod
    async def find_by_id(cls, session: AsyncSessionShim, model_id: str):
        query = select(cls.model).filter_by(id=model_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSessionShim, options=None, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        if options:
            query = query.options(*options)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(
        cls,
        session: AsyncSessionShim,
        offset: int | None = None,
        limit: int | None = None,
        order_by=None,
        **filter_by
    ):
        query = select(cls.model).filter_by(**filter_by).options(selectinload("*"))
        if order_by is not None:
            query = query.order_by(order_by)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add(cls, session: AsyncSessionShim, **data):
        instance = cls.model(**data)
        session.add(instance)
        return instance

    @classmethod
    async def add_all(cls, session: AsyncSessionShim, rows: list[dict]):
        instances = [cls.model(**row) for row in rows]
        session.add_all(instances)
        return instances

    @classmethod
    async def update(cls, session: AsyncSessionShim, id: str, **data):
        data = {key: value for key, value in data.items() if value is not None}

        query = (
            update(cls.model)
            .filter_by(id=id)
            .values(**data)
            .returning(cls.model)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)

        updated_instance = result.scalar_one_or_none()
        if updated_instance:
            await session.refresh(updated_instance)
        return updated_instance

    @classmethod
    async def delete(cls, session: AsyncSessionShim, **data):
        query = delete(cls.model).filter_by(**data)
        await session.execute(query)

    @classmethod
    async def truncate(cls, session: AsyncSessionShim):
        """Truncate the table, removing all rows"""
        table_name = cls.model.__table__.name
        query = text(f'TRUNCATE TABLE "{table_name}" CASCADE')
        await session.execute(query)

    @classmethod
    def add_sync(cls, session: Session, **data):
        """Synchronous version of add method"""
        instance = cls.model(**data)
        session.add(instance)
        return instance

    @classmethod
    def update_sync(cls, session: Session, id: str, **data) -> None:
        instance = session.get(cls.model, id)
        for key, value in data.items():
            setattr(instance, key, value)

    @classmethod
    def find_by_id_sync(cls, session: Session, id: str):
        """Synchronous version of find_by_id method"""
        return session.get(cls.model, id)
