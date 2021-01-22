from datetime import datetime
from queue import Queue, Empty
from threading import Thread
from time import sleep
from typing import Any, Callable
from collections import defaultdict

from ..extention import Extention
from ..applog import AppLog

log = AppLog.get('event')

SYS_EVENT_TIMER = "timer"


class Event:
    def __init__(self, type: str, data: Any = None):
        self.type: str = type
        self.data: Any = data


class EventManager(Extention):
    def __init__(self, time_interval: int = 1):
        super(EventManager, self).__init__(name="EventManager")

        self._interval: int = time_interval
        self._queue: Queue = Queue()
        self._event_callbacks: defaultdict = defaultdict(list)
        self._regular_callbacks: list = []

        self._timer: Thread = None
        if time_interval != 0:
            self._timer = Thread(target=self.__timer)
            self._timer.start()

    def __del___(self):
        if self._timer != None and self._timer.is_alive():
            self._timer.join(self._interval*3)
            if self._timer.is_alive():
                print('timer has been blocked')
        if self.is_alive():
            self.join(3)
            if self.is_alive():
                print('event manager has been blocked')

    def __timer(self) -> None:
        while self._alive:
            sleep(1)
            now: datetime = datetime.now()
            if now.second % self._interval:
                self.put(Event(SYS_EVENT_TIMER, datetime.now()))

    def run(self) -> None:
        while self._alive:
            try:
                e: Event = self._queue.get(block=True, timeout=1)
                self._process(e)
            except Empty:
                pass

    def _process(self, e: Event) -> None:
        if e.type not in self._event_callbacks:
            return
        callbacks: list = self._event_callbacks[e.type]
        for f in callbacks:
            f(e.data)

    def register_callback(self, type: str, func: Callable):
        l: list = self._event_callbacks[type]
        if func not in l:
            l.append(func)

    def unregister_callback(self, type: str, func: Callable):
        l: list = self._event_callbacks[type]
        if func in l:
            l.remove(func)

    def put(self, e: Event):
        self._queue.put(e)
