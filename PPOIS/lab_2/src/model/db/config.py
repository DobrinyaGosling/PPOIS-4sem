from functools import lru_cache
from typing import AsyncGenerator, Callable

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.settings import settings


@lru_cache
def get_engine() -> Engine:
    url = settings.database_url
    kwargs: dict[str, object] = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


@lru_cache
def _get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(get_engine(), expire_on_commit=False)


class AsyncSessionShim:
    def __init__(self, session: Session) -> None:
        self._session = session

    async def __aenter__(self) -> "AsyncSessionShim":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._session.close()

    def __getattr__(self, name: str):
        return getattr(self._session, name)

    async def execute(self, *args, **kwargs):
        return self._session.execute(*args, **kwargs)

    async def commit(self) -> None:
        self._session.commit()

    async def rollback(self) -> None:
        self._session.rollback()

    async def close(self) -> None:
        self._session.close()

    async def flush(self) -> None:
        self._session.flush()

    async def refresh(self, instance) -> None:
        self._session.refresh(instance)


def get_async_session_maker() -> AsyncSessionShim:
    return AsyncSessionShim(_get_session_factory()())


def get_db_session(commit: bool) -> Callable[[], AsyncGenerator[AsyncSessionShim, None]]:
    async def dependency() -> AsyncGenerator[AsyncSessionShim, None]:
        async with get_async_session_maker() as session:
            try:
                yield session
                if commit:
                    await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return dependency
