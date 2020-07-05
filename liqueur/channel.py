from contextlib import contextmanager
from queue import PriorityQueue, Empty, Queue


class ChannelManager:
    next_priority = 0

    def __init__(self):
        self.queue = PriorityQueue()
        self.channels = []

    def put(self, channel, item, *args, **kwargs):
        self.queue.put((channel, item), *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.queue.get(*args, **kwargs)

    @contextmanager
    def select(self, ordering=None, default=False):
        if default:
            try:
                channel, item = self.get(block=False)
            except Empty:
                channel = 'default'
                item = None
        else:
            channel, item = self.get()
        yield channel, item

    def new_channel(self, name):
        channel = Channel(name, self.next_priority, self)
        self.channels.append(channel)
        self.next_priority += 1
        return channel


class Channel(object):
    def __init__(self, name, priority, manager):
        self.name = name
        self.priority = priority
        self.manager = manager

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.priority < other.priority

    def put(self, item):
        self.manager.put(self, item)

