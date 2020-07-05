from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
import logging
from threading import Thread
from queue import Queue, Empty


Base = declarative_base()
_WAIT_DEFAULT_TIMEOUT = 1
_WAIT_MAX_TIMEOUT = 60


class OrderCandlestick(Base):
    __tablename__ = 'candlestick'
    id = Column(String(10), nullable=False, primary_key=True)
    datatime = Column(DateTime, nullable=False, primary_key=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __init__(self, id, datatime, open_price, high_price, low_price, close_price, quantity):
        self.id = id
        self.datatime = datatime
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.quantity = quantity

    def __repr__(self):
        return "candlestick('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.datatime,
            self.open_price,
            self.high_price,
            self.low_price,
            self.close_price,
            self.quantity)


class OrderTick(Base):
    __tablename__ = 'tick'
    id = Column(String(10), nullable=False, primary_key=True)
    datatime = Column(DateTime, nullable=False, primary_key=True)
    bid_price = Column(Float, nullable=False)
    ask_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    simulate = Column(Boolean, nullable=False)

    def __init__(self, id, datatime, bid_price, ask_price, close_price, quantity, simulate):
        self.id = id
        self.datatime = datatime
        self.bid_price = bid_price
        self.ask_price = ask_price
        self.close_price = close_price
        self.quantity = quantity
        self.simulate = simulate

    def __repr__(self):
        return "tick('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.datatime,
            self.bid_price,
            self.ask_price,
            self.close_price,
            self.quantity,
            self.simulate)


class OrderQuote(Base):
    __tablename__ = 'quote'
    id = Column(String(10), nullable=False, primary_key=True)
    datatime = Column(DateTime, nullable=False, primary_key=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    simulate = Column(Boolean, nullable=False)

    def __init__(self, id, datatime, price, quantity, simulate):
        self.id = id
        self.datatime = datatime
        self.price = price
        self.quantity = quantity
        self.simulate = simulate

    def __repr__(self):
        return "quote('{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.datatime,
            self.price,
            self.quantity,
            self.simulate)


class LiqueurSqlAlchemy(Thread):
    app = None
    _engine = None
    __queue = None
    __timeout = _WAIT_DEFAULT_TIMEOUT
    __alive = True
    log = logging.getLogger('liqueur.sql')

    def __init__(self, app, conf):
        super(LiqueurSqlAlchemy, self).__init__(name="SqlAlchemy")
        self.app = app
        self.__queue = Queue(conf['queue_size'])
        self._engine = create_engine(conf['host'], echo=conf['echo'])

    def __del(self):
        self.__session.close()

    def on_tick(self, t):
        self.__queue.put(t.to_dict())

    def on_candlestick(self, c):
        self.__queue.put(c.to_dict())

    def on_quote(self, q):
        self.__queue.put(q.to_dict())

    def stop(self):
        self.__alive = False

    def run(self):
        Base.metadata.create_all(self._engine)
        maker = sessionmaker(bind=self._engine)
        session = maker()

        while self.__alive:
            try:
                v = self.__queue.get(block=False, timeout=self.__timeout)
                self.__timeout = _WAIT_DEFAULT_TIMEOUT
                obj = None

                if v['type'] == 'Tick':
                    obj = OrderTick(
                        v['orderbook_id'],
                        v['datetime'],
                        v['bid'],
                        v['ask'],
                        v['close'],
                        v['qty'],
                        v['simulate'])
                    if session.query(OrderTick).filter_by(
                            id=v['orderbook_id']).filter_by(
                            datatime=v['datetime']).first():
                        continue

                elif v['type'] == 'Candlestick':
                    obj = OrderCandlestick(
                        v['orderbook_id'],
                        v['datetime'],
                        v['open_price'],
                        v['high_price'],
                        v['low_price'],
                        v['close_price'],
                        v['qty'])
                elif v['type'] == 'Quote':
                    obj = OrderQuote(v['orderbook_id'], v['datetime'], v['close_price'], v['qty'], v['simulate'])
                else:
                    self.log.warning(v)
                    continue

                session.add(obj)
                if self.__queue.empty():
                    session.commit()
            except Empty:
                if self.__timeout < _WAIT_MAX_TIMEOUT:
                    self.__timeout += 1

        session.close()
