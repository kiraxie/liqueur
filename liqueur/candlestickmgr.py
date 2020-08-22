from datetime import datetime, timedelta

from .util import Attributes
from .structure import Candlestick
from .applog import AppLog

log = AppLog.get('candlestick')


class CandlestickSet:
    datetime = None
    minutes = 0
    length = 0
    line = None
    ma = {}

    def __init__(self, dt, minutes, ma):
        self.datetime = dt
        self.minutes = minutes
        for v in ma:
            self.ma[v] = []

    def __del__(self):
        pass

    def _append(self, k):
        self.length += 1
        self.line.append(k)
        for r in self.ma.keys():
            self.ma[r].append(float(0))

    def append(self, oid, dt, price, qty):
        k = Candlestick(oid, dt, price, price, price, price, qty)

        if self.line is None:
            self.line = []
            k.timestamp = self.datetime.timestamp()
            self._append(k)
            return

        last = self.line[-1]

        if self.datetime > dt:
            last += k
        else:
            self.datetime += timedelta(minutes=self.minutes)
            k.timestamp = self.datetime.timestamp()
            self._append(k)

        self._ma()

    def _ma(self):
        line_len = len(self.line)
        for r, l in self.ma.items():
            if line_len < r:
                continue
            m = 0
            for k in self.line[-r:]:
                m += k.close

            self.ma[r][-1] = float(m)/r


class CandlestickMgr:
    bucket = None

    def __init__(self, market_open_dt, ma=[5]):
        self.bucket = Attributes({
            'one': CandlestickSet(market_open_dt+timedelta(minutes=1), 1, ma),
            'five': CandlestickSet(market_open_dt+timedelta(minutes=5), 5, ma),
            'fifteen': CandlestickSet(market_open_dt+timedelta(minutes=15), 15, ma),
            'thirty': CandlestickSet(market_open_dt+timedelta(minutes=30), 30, ma),
            'sixty': CandlestickSet(market_open_dt+timedelta(minutes=60), 60, ma),
        })

    def insert(self, t):
        dt = datetime.fromtimestamp(float(t.timestamp))
        if t.simulate:
            return
        for ins in self.bucket.values():
            ins.append(t.orderbook_id, dt, t.close, t.qty)

    def fetch(self, name):
        return self.bucket[name]
