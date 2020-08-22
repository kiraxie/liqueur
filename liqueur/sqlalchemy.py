from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from .extention import Extention
from .applog import AppLog
from .codes import subscribe_type

base = declarative_base()
log = AppLog.get('db')


class TableCandlestick(base):
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


class TableTick(base):
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


class TableQuote(base):
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


class LiqueurSqlAlchemy(Extention):
    app = None
    _engine = None
    subscriber = None
    _session = None

    def __init__(self, app, subscriber, conf):
        super(LiqueurSqlAlchemy, self).__init__(name="SqlAlchemy")
        self.app = app
        self.subscriber = subscriber
        self._engine = create_engine(conf.host, echo=conf.echo)
        base.metadata.create_all(self._engine)
        maker = sessionmaker(bind=self._engine)
        self._session = maker()

    def __del__(self):
        self._session.close()

    def on_quote(self, v):
        if v.category == subscribe_type.tick:
            if self._session.query(TableTick).filter_by(
                    id=v.orderbook_id).filter_by(
                    datatime=datetime.fromtimestamp(v.timestamp)).first():
                return
            self._session.add(TableTick(v.orderbook_id, datetime.fromtimestamp(
                v.timestamp), v.bid, v.ask, v.close, v.qty, v.simulate))
        elif v.category == subscribe_type.candlestick:
            if self._session.query(TableCandlestick).filter_by(
                    id=v.orderbook_id).filter_by(
                    datatime=datetime.fromtimestamp(v.timestamp)).first():
                return
            self._session.add(
                TableCandlestick(
                    v.orderbook_id, datetime.fromtimestamp(v.timestamp),
                    v.open, v.high, v.low, v.close, v.qty))
