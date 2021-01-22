from threading import Thread
from queue import Queue, Empty
from typing import Any, Callable
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.engine.base import Engine

from ..extention import Extention
from ..applog import AppLog

log = AppLog.get('database')


SchemaBase = declarative_base()


class Transaction(Session):
    def __init__(self, bind):
        super(Transaction, self).__init__(bind=bind)

    def __del__(self):
        self.close()

    def create(self, v: Any) -> None:
        self.add(v)
        self.commit()

    def create_or_ignore(self, v: Any, **kwargs) -> bool:
        instance = self.query(type(v)).filter_by(**kwargs).first()

        if instance is None:
            self.add(v)
            self.commit()
            return True

        return False


class TaskCreate:
    def __init__(self, bind: Engine, v: SchemaBase) -> None:
        self.tx: Transaction = Transaction(bind)
        self.v: SchemaBase = v

    def __call__(self) -> Any:
        self.tx.create(self.v)


class TaskCreateOrIgnore:
    def __init__(self, bind: Engine, v: SchemaBase, **kw) -> None:
        self.tx: Transaction = Transaction(bind)
        self.v: SchemaBase = v
        self.kw: dict[str, Any] = kw

    def __call__(self) -> Any:
        self.tx.create_or_ignore(self.v, **self.kw)


class Database(Extention):
    def __init__(self, host: str, schema: DeclarativeMeta, **kw) -> None:
        super(Database, self).__init__(name='database')

        self._engine: Engine = create_engine(host, **kw)
        self._queue: Queue = Queue()

        schema.metadata.create_all(self._engine)

    def run(self) -> None:
        while self._alive:
            try:
                caller: Callable = self._queue.get_nowait()
                caller()
            except Empty:
                pass

    def stop(self) -> None:
        while not self._queue.empty():
            log.debug('wait: %d' % self._queue.qsize())
            sleep(1)

        super().stop()

    def async_create(self, v: Any) -> None:
        node: TaskCreate = TaskCreate(self._engine, v)
        self._queue.put(node)

    def async_create_or_ignore(self, model: type, **kwargs) -> None:
        node: TaskCreateOrIgnore = TaskCreateOrIgnore(self._engine, model, **kwargs)
        self._queue.put(node)

    def transaction(self) -> Transaction:
        return Transaction(self._engine)
