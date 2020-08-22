from datetime import datetime
from .util import Attributes
from .codes import subscribe_type


class BaseAttrs(Attributes):
    def __init__(self, category, orderbook_id, dt):
        super(BaseAttrs, self).__init__({
            'category': category,
            'orderbook_id': orderbook_id,
            'timestamp': dt.timestamp(),
        })

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.timestamp)

    def __gt__(self, other):
        if self.timestamp > other.timestamp:
            return True
        return False

    def __lt__(self, other):
        if self.timestamp < other.timestamp:
            return True
        return False

    def __eq__(self, other):
        if self.timestamp == other.timestamp:
            return True
        return False

    def __ne__(self, other):
        if self.timestamp != other.timestamp:
            return True
        return False


class Tick(BaseAttrs):
    def __init__(self, orderbook_id, dt, name, bid, ask, close, qty, simulate):
        super(Tick, self).__init__(subscribe_type.tick, orderbook_id, dt)
        self.update({
            'name': name,
            'bid': bid,
            'ask': ask,
            'close': close,
            'qty': qty,
            'simulate': simulate,
        })


class Candlestick(BaseAttrs):
    __up_shadow = 0
    __down_shadow = 0
    __bar = 0
    __head = 0
    __foot = 0

    @property
    def up_shadow(self):
        return self.__up_shadow

    @property
    def down_shadow(self):
        return self.__down_shadow

    @property
    def bar(self):
        return self.__bar

    @property
    def head(self):
        return self.__head

    @property
    def foot(self):
        return self.__foot

    def __init__(self, orderbook_id, dt, open, high, low, close, qty):
        super(Candlestick, self).__init__(subscribe_type.candlestick, orderbook_id, dt)
        self.update({
            'open': float(open),
            'high': float(high),
            'low': float(low),
            'close': float(close),
            'qty': int(qty),
        })
        self._update_props()

    def _update_props(self):
        if self.open == self.close:
            # self.__pattern = KBar.cross_kbar
            self.__up_shadow = self.high - self.open
            self.__down_shadow = self.open - self.low
            self.__bar = 0
            self.__head = self.open
            self.__foot = self.open
        elif self.open < self.close:
            # self.__pattern = KBar.red_kbar
            self.__up_shadow = self.high - self.close
            self.__down_shadow = self.open - self.low
            self.__bar = self.close - self.open
            self.__head = self.close
            self.__foot = self.open
        else:
            # self.__pattern = KBar.black_kbar
            self.__up_shadow = self.high - self.open
            self.__down_shadow = self.close - self.low
            self.__bar = self.open - self.close
            self.__head = self.open
            self.__foot = self.close

    def __iadd__(self, other):
        self.high = max(self.high, other.high)
        self.low = min(self.low, other.low)
        self.close = other.close
        self.qty += other.qty

        self._update_props()


class Quotation(BaseAttrs):
    def __init__(self, orderbook_id, dt, bid, ask):
        super(Quotation, self).__init__(subscribe_type.quotation, orderbook_id, dt)
        self.update({
            'bid': bid,
            'ask': ask,
        })


class Trade(Attributes):
    def __init__(self, price, qty):
        super().__init__({
            'price': price,
            'qty': qty,
        })
