from threading import Thread

from .util import Attributes
from .applog import AppLog


log = AppLog.get('extention')


class Extention(Thread):
    _alive: bool = True

    def __init__(self, name: str):
        super(Extention, self).__init__(name=name)
        self.name: str = name

    def stop(self):
        self._alive = False


class ExtentionManager:
    _started = False
    _stop = False
    _extentions = Attributes({})

    def __init__(self):
        pass

    def __del__(self):
        if not self._stop:
            self.stop()
        for name, e in self._extentions.items():
            log.debug("delete %s" % name)
            del e

    def start(self):
        self._start = True
        for name, e in self._extentions.items():
            log.debug("start %s" % name)
            e.start()

    def stop(self):
        self._stop = True
        for name, e in self._extentions.items():
            log.debug("stop %s" % name)
            e.stop()

    def add(self, e: Extention):
        if not isinstance(e, Extention):
            raise TypeError
        self._extentions[e.name] = e
        if self._started:
            e.start()

    def remove(self, name):
        if name not in self._extentions:
            return
        e = self._extentions[name]
        if self._started:
            e.stop()
        del self._extentions[name]

    def wait(self):
        for name, e in self._extentions.items():
            log.debug("wait %s" % name)
            e.join()

    def get(self, name):
        return self._extentions.get(name)
