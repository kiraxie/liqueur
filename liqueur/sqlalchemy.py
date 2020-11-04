from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from queue import Queue, Empty

from .extention import Extention
from .applog import AppLog
from .schema import SchemaBase

log = AppLog.get('db')


class LiqueurSqlAlchemy(Extention):
    app = None
    _engine = None
    _queue = Queue()

    def __init__(self, app, conf):
        super(LiqueurSqlAlchemy, self).__init__(name="SqlAlchemy")
        self.app = app
        self._engine = create_engine(conf.host, echo=False)
        SchemaBase.metadata.create_all(self._engine)

    def __del__(self):
        pass

    def run(self):
        maker = sessionmaker(bind=self._engine)
        session = maker()
        while self._alive:
            try:
                v = self._queue.get_nowait()
                v.create(session)
            except Empty:
                pass
        session.close()

    def stop(self) -> None:
        super().stop()
        if self._alive:
            self._queue.task_done()

    def on_quote(self, v) -> None:
        self._queue.put(v)
