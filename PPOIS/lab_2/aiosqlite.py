import asyncio
import sqlite3
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Any, Callable, Iterable, Optional, Sequence

# Re-export sqlite3 DB-API attributes expected by SQLAlchemy's sqlite+aiosqlite dialect.
Error = sqlite3.Error
DatabaseError = sqlite3.DatabaseError
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info

_STOP = object()


def connect(database: str, *args: Any, **kwargs: Any) -> "Connection":
    return Connection(database, args=args, kwargs=kwargs)


@dataclass(slots=True)
class Cursor:
    _conn: "Connection"
    _cursor: sqlite3.Cursor

    description: Any = None
    lastrowid: int = 0
    rowcount: int = -1

    async def execute(self, sql: str, parameters: Sequence[Any] | None = None) -> "Cursor":
        def _execute() -> tuple[Any, int, int]:
            if parameters is None:
                self._cursor.execute(sql)
            else:
                self._cursor.execute(sql, parameters)
            return self._cursor.description, int(self._cursor.lastrowid or 0), int(self._cursor.rowcount or 0)

        self.description, self.lastrowid, self.rowcount = await self._conn._call(_execute)
        return self

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Sequence[Any]]) -> "Cursor":
        def _executemany() -> tuple[Any, int, int]:
            self._cursor.executemany(sql, seq_of_parameters)
            return self._cursor.description, int(self._cursor.lastrowid or 0), int(self._cursor.rowcount or 0)

        self.description, self.lastrowid, self.rowcount = await self._conn._call(_executemany)
        return self

    async def fetchone(self):
        return await self._conn._call(self._cursor.fetchone)

    async def fetchmany(self, size: int | None = None):
        if size is None:
            return await self._conn._call(self._cursor.fetchmany)
        return await self._conn._call(self._cursor.fetchmany, size)

    async def fetchall(self):
        return await self._conn._call(self._cursor.fetchall)

    async def close(self) -> None:
        await self._conn._call(self._cursor.close)

    def __aiter__(self):
        return self

    async def __anext__(self):
        row = await self.fetchone()
        if row is None:
            raise StopAsyncIteration
        return row


class Connection:
    def __init__(self, database: str, args: tuple[Any, ...] = (), kwargs: dict[str, Any] | None = None) -> None:
        self._database = database
        self._args = args
        self._kwargs = dict(kwargs or {})
        self._kwargs.setdefault("check_same_thread", False)

        self._conn: sqlite3.Connection | None = None
        self._queue: Queue[object] = Queue()
        self._thread = Thread(target=self._thread_main, daemon=True)
        self._thread.start()

        self._open_lock = asyncio.Lock()

    def __await__(self):
        return self._open().__await__()

    async def __aenter__(self) -> "Connection":
        await self
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    def _thread_main(self) -> None:
        while True:
            item = self._queue.get()
            if item is _STOP:
                break

            func, args, kwargs, loop, future = item  # type: ignore[misc]
            try:
                result = func(*args, **kwargs)
            except BaseException as e:
                loop.call_soon_threadsafe(future.set_exception, e)
            else:
                loop.call_soon_threadsafe(future.set_result, result)

    def _submit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> "asyncio.Future[Any]":
        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        self._queue.put((func, args, kwargs, loop, future))
        return future

    async def _call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        return await self._submit(func, *args, **kwargs)

    async def _open(self) -> "Connection":
        if self._conn is not None:
            return self

        async with self._open_lock:
            if self._conn is not None:
                return self

            def _connect() -> None:
                self._conn = sqlite3.connect(self._database, *self._args, **self._kwargs)

            await self._call(_connect)
            return self

    @property
    def in_transaction(self) -> bool:
        return bool(getattr(self._conn, "in_transaction", False))

    async def cursor(self, *args: Any, **kwargs: Any) -> Cursor:
        kwargs.pop("server_side", None)
        await self._open()

        def _cursor() -> sqlite3.Cursor:
            assert self._conn is not None
            return self._conn.cursor(*args, **kwargs)

        raw = await self._call(_cursor)
        return Cursor(self, raw)

    async def execute(self, sql: str, parameters: Sequence[Any] | None = None) -> Cursor:
        cur = await self.cursor()
        return await cur.execute(sql, parameters)

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Sequence[Any]]) -> Cursor:
        cur = await self.cursor()
        return await cur.executemany(sql, seq_of_parameters)

    async def executescript(self, sql_script: str) -> Cursor:
        await self._open()

        def _executescript() -> sqlite3.Cursor:
            assert self._conn is not None
            cur = self._conn.cursor()
            cur.executescript(sql_script)
            return cur

        raw = await self._call(_executescript)
        return Cursor(self, raw)

    async def commit(self) -> None:
        await self._open()

        def _commit() -> None:
            assert self._conn is not None
            self._conn.commit()

        await self._call(_commit)

    async def rollback(self) -> None:
        await self._open()

        def _rollback() -> None:
            assert self._conn is not None
            self._conn.rollback()

        await self._call(_rollback)

    async def close(self) -> None:
        if self._conn is None:
            self._queue.put(_STOP)
            return

        def _close() -> None:
            assert self._conn is not None
            self._conn.close()
            self._conn = None

        await self._call(_close)
        self._queue.put(_STOP)

    def stop(self) -> None:
        conn = self._conn
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            self._conn = None
        self._queue.put(_STOP)

    async def create_function(
        self, name: str, num_params: int, func: Any, deterministic: bool | None = None
    ) -> None:
        await self._open()

        def _create_function() -> None:
            assert self._conn is not None
            if deterministic is None:
                self._conn.create_function(name, num_params, func)
            else:
                self._conn.create_function(name, num_params, func, deterministic=deterministic)

        await self._call(_create_function)

    async def set_trace_callback(self, trace_callback: Optional[Any]) -> None:
        await self._open()

        def _set_trace_callback() -> None:
            assert self._conn is not None
            self._conn.set_trace_callback(trace_callback)

        await self._call(_set_trace_callback)
