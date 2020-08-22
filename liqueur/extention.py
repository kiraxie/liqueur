from .util import Attributes
from .applog import AppLog


log = AppLog.get('extention')


class Extention():
    _name = True

    @property
    def name(self):
        return self._name

    def __init__(self, name):
        self._name = name

    def on_quote(self):
        raise NotImplementedError


class ExtentionManager:
    _cleanup = False
    _extentions = Attributes({})

    def __init__(self):
        pass

    def __del__(self):
        if not self._cleanup:
            self.cleanup()

    def cleanup(self):
        self._cleanup = True
        for name, e in self._extentions.items():
            log.debug("delete %s" % name)
            del e

    def add(self, name, e):
        if not isinstance(e, Extention):
            raise TypeError
        self._extentions[name] = e

    def remove(self, name):
        if name not in self._extentions:
            return
        del self._extentions[name]

    def get(self, name):
        return getattr(self._extentions, name, None)

    def on_quote(self, v):
        for e in self._extentions.values():
            e.on_quote(v)
