from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean
from uuid import uuid4

SchemaBase = declarative_base()


class Candlestick(SchemaBase):
    __tablename__ = 'candlesticks'
    id = Column(UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)
    orderbook_id = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    _up_shadow = 0
    _down_shadow = 0
    _bar = 0
    _head = 0
    _foot = 0

    @property
    def up_shadow(self):
        return self._up_shadow

    @property
    def down_shadow(self):
        return self._down_shadow

    @property
    def bar(self):
        return self._bar

    @property
    def head(self):
        return self._head

    @property
    def foot(self):
        return self._foot

    def _update_props(self):
        if self.open == self.close:
            self._up_shadow = self.high - self.open
            self._down_shadow = self.open - self.low
            self._bar = 0
            self._head = self.open
            self._foot = self.open
        elif self.open < self.close:
            self._up_shadow = self.high - self.close
            self._down_shadow = self.open - self.low
            self._bar = self.close - self.open
            self._head = self.close
            self._foot = self.open
        else:
            self._up_shadow = self.high - self.open
            self._down_shadow = self.close - self.low
            self._bar = self.open - self.close
            self._head = self.open
            self._foot = self.close

    def __init__(self, orderbook_id, created_at, open, high, low, close, quantity):
        self.id = uuid4()
        self.orderbook_id = orderbook_id
        self.created_at = created_at
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.quantity = quantity

        self._update_props()

    def __repr__(self):
        return "candlesticks('{}','{}' '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.orderbook_id,
            self.created_at,
            self.open,
            self.high,
            self.low,
            self.close,
            self.quantity)

    def create(self, session) -> None:
        session.add(self)
        session.commit()

    def first_or_create(self, session):
        instance = session.query(Candlestick).filter(
            orderbook_id=self.orderbook_id,
            created_at=self.created_at).first()

        if instance:
            return instance

        session.add(self)
        session.commit()

        return self


class Tick(SchemaBase):
    __tablename__ = 'ticks'
    id = Column(UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)
    orderbook_id = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False, primary_key=True)
    bid = Column(Float, nullable=False)
    ask = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    simulate = Column(Boolean, nullable=False)

    def __init__(self, orderbook_id, created_at, bid, ask, close, quantity, simulate):
        self.id = uuid4()
        self.orderbook_id = orderbook_id
        self.created_at = created_at
        self.bid = bid
        self.ask = ask
        self.close = close
        self.quantity = quantity
        self.simulate = simulate

    def __repr__(self):
        return "ticks('{}','{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.orderbook_id,
            self.created_at,
            self.bid,
            self.ask,
            self.close,
            self.quantity,
            self.simulate)

    def create(self, session) -> None:
        session.add(self)
        session.commit()

    def first_or_create(self, session):
        instance = session.query(Tick).filter(
            orderbook_id=self.orderbook_id,
            created_at=self.created_at,
            close=self.close,
            quantity=self.quantity).first()

        if instance:
            return instance

        session.add(self)
        session.commit()

        return self
