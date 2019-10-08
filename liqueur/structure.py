from datetime import datetime
import json


class _struct:
    __orderbook_id = ''
    __datetime = None

    @property
    def orderbook_id(self):
        return self.__orderbook_id

    @property
    def datetime(self):
        return self.__datetime

    @property
    def timestamp(self):
        return self.__datetime.timestamp()

    def __init__(self, orderbook_id, dt):
        assert(type(dt) != 'datetime')

        self.__orderbook_id = orderbook_id
        self.__datetime = dt

    def __gt__(self, other):
        if self.__datetime > other.__datetime:
            return True

        return False

    def __lt__(self, other):
        if self.__datetime < other.__datetime:
            return True

        return False

    def __eq__(self, other):
        if self.__datetime == other.__datetime:
            return True

        return False

    def __ne__(self, other):
        if self.__datetime != other.__datetime:
            return True

        return False

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def to_dict(self):
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, dict_data):
        raise NotImplementedError()


class Tick(_struct):
    __name = ''

    __bid = -1
    __ask = -1
    __close = -1
    __qty = -1
    __simulate = True

    @property
    def name(self):
        return self.__name

    @property
    def bid_price(self):
        return self.__bid

    @property
    def ask_price(self):
        return self.__ask

    @property
    def close_price(self):
        return self.__close

    @property
    def qty(self):
        return self.__qty

    @property
    def simulate(self):
        return self.__simulate

    def __init__(self, dt, orderbook_id, name, bid, ask, close, qty, simulate):
        super(Tick, self).__init__(orderbook_id, dt)

        self.__name = name
        self.__bid = bid
        self.__ask = ask
        self.__close = close
        self.__qty = qty
        self.__simulate = simulate

    def to_dict(self):
        return {'datetime': str(self.datetime),
                'timestamp': self.timestamp,
                'orderbook_id': self.orderbook_id,
                'name': self.__name,
                'bid': self.__bid,
                'ask': self.__ask,
                'close': self.__close,
                'qty': self.__qty,
                'simulate': self.__simulate}

    @classmethod
    def from_dict(cls, dict_data):
        dt = datetime.fromtimestamp(dict_data['timestamp'])

        return cls(dt,
                   dict_data['orderbook_id'],
                   dict_data['name'],
                   dict_data['bid'],
                   dict_data['ask'],
                   dict_data['close'],
                   dict_data['qty'],
                   dict_data['simulate'])

    @classmethod
    def from_tick(cls, date, time, us, orderbook_id, name, bid, ask, close, qty, simulate):
        _year = int(date / 10000)
        date %= 10000
        _mon = int(date / 100)
        _day = date % 100

        _hour = int(time / 10000)
        time %= 10000
        _min = int(time / 100)
        _sec = time % 100

        dt = datetime(_year, _mon, _day, _hour, _min, _sec, us)

        return cls(dt, orderbook_id, name, bid, ask, close, qty, simulate)


class QuoteData(_struct):
    __name = ''

    __high_price = -1
    __open_price = -1
    __low_price = -1
    __close_price = -1

    __bid_price = -1
    __bid_qty = -1
    __ask_price = -1
    __ask_qty = -1

    __buy_qty = -1
    __sell_qty = -1

    __tick_qty = -1
    __total_qty = -1
    __ref_qty = -1
    __ref_price = -1

    __up_price = -1
    __down_price = -1

    __simulate = True

    @property
    def name(self):
        return self.__name

    @property
    def high_price(self):
        return self.__high_price

    @property
    def open_price(self):
        return self.__open_price

    @property
    def low_price(self):
        return self.__low_price

    @property
    def close_price(self):
        return self.__close_price

    @property
    def bid_price(self):
        return self.__bid_price

    @property
    def bid_qty(self):
        return self.__bid_qty

    @property
    def ask_price(self):
        return self.__ask_price

    @property
    def ask_qty(self):
        return self.__ask_qty

    @property
    def buy_qty(self):
        return self.__buy_qty

    @property
    def sell_qty(self):
        return self.__sell_qty

    @property
    def tick_qty(self):
        return self.__tick_qty

    @property
    def total_qty(self):
        return self.__total_qty

    @property
    def ref_price(self):
        return self.__ref_price

    @property
    def ref_qty(self):
        return self.__ref_qty

    @property
    def up_price(self):
        return self.__up_price

    @property
    def down_price(self):
        return self.__down_price

    @property
    def simulate(self):
        return self.__simulate

    def __init__(self, dt, *args, **kwargs):

        super(QuoteData, self).__init__(kwargs['orderbook_id'], dt)

        self.__name = kwargs['name']

        self.__high_price = kwargs['high_price']
        self.__open_price = kwargs['open_price']
        self.__low_price = kwargs['low_price']
        self.__close_price = kwargs['close_price']

        self.__bid_price = kwargs['bid_price']
        self.__bid_qty = kwargs['bid_qty']
        self.__ask_price = kwargs['ask_price']
        self.__ask_qty = kwargs['ask_qty']

        self.__buy_qty = kwargs['buy_qty']
        self.__sell_qty = kwargs['sell_qty']

        self.__tick_qty = kwargs['tick_qty']
        self.__total_qty = kwargs['total_qty']
        self.__ref_qty = kwargs['ref_qty']
        self.__ref_price = kwargs['ref_price']

        self.__up_price = kwargs['up_price']
        self.__down_price = kwargs['down_price']

        self.__simulate = kwargs['simulate']

    def to_dict(self):
        return {'datetime': str(self.datetime),
                'timestamp': self.timestamp,
                'orderbook_id': self.orderbook_id,
                'name': self.__name,
                'high_price': self.__high_price,
                'open_price': self.__open_price,
                'low_price': self.__low_price,
                'close_price': self.__close_price,
                'bid_price': self.__bid_price,
                'bid_qty': self.__bid_qty,
                'ask_price': self.__ask_price,
                'ask_qty': self.__ask_qty,
                'buy_qty': self.__buy_qty,
                'sell_qty': self.__sell_qty,
                'tick_qty': self.__tick_qty,
                'total_qty': self.__total_qty,
                'ref_qty': self.__ref_qty,
                'ref_price': self.__ref_price,
                'up_price': self.__up_price,
                'down_price': self.__down_price,
                'simulate': self.__simulate}

    @classmethod
    def from_dict(cls, dict_data):
        dt = datetime.fromtimestamp(dict_data['timestamp'])

        return cls(dt, **dict_data)

    @classmethod
    def from_quote(cls,
                   orderbook_id, name,
                   high_price, open_price, low_price, close_price,
                   bid_price, bid_qty, ask_price, ask_qty,
                   buy_qty, sell_qty,
                   tick_qty, total_qty,
                   ref_qty, ref_price,
                   up_price, down_price,
                   simulate):
        kwargs = {'orderbook_id': orderbook_id,
                  'name': name,
                  'high_price': high_price,
                  'open_price': open_price,
                  'low_price': low_price,
                  'close_price': close_price,
                  'bid_price': bid_price,
                  'bid_qty': bid_qty,
                  'ask_price': ask_price,
                  'ask_qty': ask_qty,
                  'buy_qty': buy_qty,
                  'sell_qty': sell_qty,
                  'tick_qty': tick_qty,
                  'total_qty': total_qty,
                  'ref_qty': ref_qty,
                  'ref_price': ref_price,
                  'up_price': up_price,
                  'down_price': down_price,
                  'simulate': simulate}

        return cls(datetime.now(), **kwargs)


class KBar(_struct):
    __red_kbar = 1
    __cross_kbar = 0
    __black_kbar = -1

    __open_price = -1
    __high_price = -1
    __low_price = -1
    __close_price = -1
    __qty = -1

    __bar = -1
    __up_shadow = -1
    __down_shadow = -1
    __head = -1
    __foot = -1
    __pattern = None

    @classmethod
    def red_kbar(cls):
        return cls.__red_kbar

    @classmethod
    def cross_kbar(cls):
        return cls.__cross_kbar

    @classmethod
    def black_kbar(cls):
        return cls.__black_kbar

    @property
    def open_price(self):
        return self.__open_price

    @property
    def high_price(self):
        return self.__high_price

    @property
    def low_price(self):
        return self.__low_price

    @property
    def close_price(self):
        return self.__close_price

    @property
    def qty(self):
        return self.__qty

    @property
    def bar(self):
        return self.__bar

    @property
    def up_shadow(self):
        return self.__up_shadow

    @property
    def down_shadow(self):
        return self.__down_shadow

    @property
    def head(self):
        return self.__head

    @property
    def foot(self):
        return self.__foot

    @property
    def pattern(self):
        return self.__pattern

    def __update_props(self):
        if self.__open_price == self.__close_price:
            self.__pattern = KBar.cross_kbar
            self.__up_shadow = self.__high_price - self.__open_price
            self.__down_shadow = self.__open_price - self.__low_price
            self.__bar = 0
            self.__head = self.__open_price
            self.__foot = self.__open_price
        elif self.__open_price < self.__close_price:
            self.__pattern = KBar.red_kbar
            self.__up_shadow = self.__high_price - self.__close_price
            self.__down_shadow = self.__open_price - self.__low_price
            self.__bar = self.__close_price - self.__open_price
            self.__head = self.__close_price
            self.__foot = self.__open_price
        else:
            self.__pattern = KBar.black_kbar
            self.__up_shadow = self.__high_price - self.__open_price
            self.__down_shadow = self.__close_price - self.__low_price
            self.__bar = self.__open_price - self.__close_price
            self.__head = self.__open_price
            self.__foot = self.__close_price

    def __init__(self, orderbook_id, dt, open_price, high_price, low_price, close_price, qty):
        super(KBar, self).__init__(orderbook_id, dt)

        self.__open_price = float(open_price)
        self.__high_price = float(high_price)
        self.__low_price = float(low_price)
        self.__close_price = float(close_price)
        self.__qty = int(qty)

        self.__update_props()

    # Close price comparison
    def __gt__(self, other):
        if self.__close_price < other.__close_price:
            return False

        return True

    def __lt__(self, other):
        if self.__close_price > other.__close_price:
            return False

        return True

    # Compute other lind of K line
    def __iadd__(self, other):
        self.__timestamp = other.__timestamp
        self.__high_price = max(self.__high_price, other.high_price)
        self.__low_price = min(self.__low_price, other.low_price)
        self.__close_price = other.close_price
        self.__qty += other.qty

        self.__update_props()

    def to_dict(self, detail=False):
        d = {}
        b = {'orderbook_id': str(self.orderbook_id),
             'datetime': str(self.datetime),
             'timestamp': self.timestamp,
             'open_price': self.__open_price,
             'high_price': self.__high_price,
             'low_price': self.__low_price,
             'close_price': self.__close_price,
             'qty': self.__qty}

        if detail:
            d = {'bar': self.__bar,
                 'up_shadow': self.__up_shadow,
                 'down_shadow': self.__down_shadow,
                 'head': self.__head,
                 'foot': self.__foot,
                 'pattern': self.__pattern}

        return {**b, **d}

    @classmethod
    def from_dict(cls, dict_data):
        dt = datetime.fromtimestamp(dict_data['timestamp'])

        return cls(dict_data['orderbook_id'],
                   dt,
                   dict_data['open_price'],
                   dict_data['high_price'],
                   dict_data['low_price'],
                   dict_data['close_price'],
                   dict_data['qty'])

    @classmethod
    def from_kbar(cls, orderbook_id, time_string, open_price, high_price, low_price, close_price, qty):
        if len(time_string) > 10:
            dt = datetime.strptime(time_string, '%Y/%m/%d %H:%M')
        else:
            dt = datetime.strptime(time_string, '%Y/%m/%d')

        return cls(orderbook_id, dt, open_price, high_price, low_price, close_price, qty)

    @classmethod
    def from_kbar_string(cls, orderbook_id, string_data):
        [time_string, open_price, high_price, low_price, close_price, qty] = string_data.split(',')
        if len(time_string) > 10:
            dt = datetime.strptime(time_string, '%Y/%m/%d %H:%M')
        else:
            dt = datetime.strptime(time_string, '%Y/%m/%d')

        return cls(orderbook_id, dt, open_price, high_price, low_price, close_price, qty)


class PriceQty():
    __price = -1
    __qty = -1

    @property
    def price(self):
        return self.__price

    @property
    def qty(self):
        return self.__qty

    def __init__(self, price=-1, qty=-1):
        self.__price = price
        self.__qty = qty

    def to_dict(self):
        return {'price': self.__price, 'qty': self.__qty}

    @classmethod
    def from_dict(cls, dict_data):
        return cls(dict_data['price'], dict_data['qty'])


class BestFivePrice(_struct):
    __bid = [PriceQty(), PriceQty(), PriceQty(), PriceQty(), PriceQty()]
    __ask = [PriceQty(), PriceQty(), PriceQty(), PriceQty(), PriceQty()]

    @property
    def bid(self):
        return self.__bid

    @property
    def ask(self):
        return self.__ask

    def __init__(self, orderbook_id, dt, bid_py, ask_py):
        super(BestFivePrice, self).__init__(orderbook_id, dt)

        self.update(bid_py, ask_py)

    def update(self, bid_py, ask_py):
        assert(type(bid_py) != 'list')
        assert(type(ask_py) != 'list')

        for i in range(5):
            self.__bid[i] = bid_py[i]
            self.__ask[i] = ask_py[i]

    def to_dict(self):
        d = {'orderbook_id': str(self.orderbook_id),
             'datetime': str(self.datetime),
             'timestamp': self.timestamp,
             'bid': [],
             'ask': []}

        for i in range(5):
            d['bid'].append(self.__bid[i].to_dict())
            d['ask'].append(self.__ask[i].to_dict())

        return d

    @classmethod
    def from_dict(cls, dict_data):
        dt = datetime.fromtimestamp(dict_data['timestamp'])
        bid_py = []
        ask_py = []

        for i in range(5):
            bid_py.append(PriceQty.from_dict(dict_data['bid'][i]))
            ask_py.append(PriceQty.from_dict(dict_data['ask'][i]))

        return cls(dict_data['orderbook_id'], dt, bid_py, ask_py)

    @classmethod
    def from_best_five(cls, orderbook_id, bid_py, ask_py):
        return cls(orderbook_id, datetime.now(), bid_py, ask_py)
