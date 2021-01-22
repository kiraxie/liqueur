import math

from datetime import datetime, MINYEAR
from decimal import Decimal

from .codes import err_codes, candlestick_type, candlestick_output_type, candlestick_trade_session, subscribe_type
from .applog import AppLog
from .schema import Tick, Candlestick
from .event import EventManager, Event

log = AppLog.get('marketboard')

MARKET_QUOTE: str = 'market_quote'
market_orderbook_list: str = 'market_orderbook_list'
market_event: str = 'market_event'
heartbeat: str = 'heartbeat'


class MarketBoard:
    app = None

    def __init__(self, eventmgr: EventManager, app, cfg):
        self._eventmgr: EventManager = eventmgr
        self.app = app

        def timer_print(dt: datetime):
            log.debug(datetime.combine(datetime.now(), dt.time()))
        self._eventmgr.register_callback(heartbeat, timer_print)

        def market_event_handler(t):
            if t == err_codes.subject_connection_connected:
                log.info('Session...established')
            elif t == err_codes.subject_connection_disconnect:
                log.warn('Session...disconnect')
            elif t == err_codes.subject_connection_stocks_ready:
                log.info('Session...ready')
                self.app.send_heartbeat()
                self.subscribe(cfg.subscription)
            elif t == err_codes.subject_connection_fail:
                log.error('Connection failure')
                self.app.stop()
            else:
                self.app.corelog(t)
        self._eventmgr.register_callback(market_event, market_event_handler)

    def __del__(self):
        pass

    def subscribe(self, orderbooks):
        for t, val in orderbooks.items():
            if t == subscribe_type.tick:
                if isinstance(val, list):
                    for v in val:
                        (pg, err) = self.app.subscribe_tick(-1, v)
                        self.app.corelog(err)
                else:
                    (pg, err) = self.app.subscribe_tick(-1, val)
                    self.app.corelog(err)
            elif t == subscribe_type.candlestick:
                for oid, typ in val.items():
                    self.app.corelog(
                        self.app.subscribe_candlestick(
                            oid, candlestick_type[typ],
                            candlestick_output_type.new,
                            candlestick_trade_session.daylight))

    def OnNotifyServerTime(self, sHour, sMinute, sSecond, nTotal):
        dt: datetime = datetime.combine(datetime.now(), datetime(MINYEAR, 1, 1, sHour, sMinute, sSecond, 0).time())
        self._eventmgr.put(Event(heartbeat, dt))

        if dt.second % 10 != 0:
            self.app.send_heartbeat()

    def OnConnection(self, nKind, nCode):
        if self.app.corelog(nCode):
            self.stop()
            return
        self._eventmgr.put(Event(market_event, nKind))

    def _on_notify_tick(
            self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
        (p_stock, err) = self.app.get_profile(sMarketNo, sIndex)
        if self.app.corelog(err):
            return

        _year = int(nDate / 10000)
        nDate %= 10000
        _mon = int(nDate / 100)
        _day = nDate % 100
        _hour = int(nTimehms / 10000)
        nTimehms %= 10000
        _min = int(nTimehms / 100)
        _sec = nTimehms % 100
        dt = datetime(_year, _mon, _day, _hour, _min, _sec, nTimemillismicros)

        orderbook_id = p_stock.bstrStockNo
        cardinal_num = math.pow(10, p_stock.sDecimal)
        bid = Decimal(nBid / cardinal_num)
        ask = Decimal(nAsk / cardinal_num)
        close = Decimal(nClose / cardinal_num)

        tick = Tick(orderbook_id, dt, bid, ask, close, nQty, nSimulate)
        self._eventmgr.put(Event(MARKET_QUOTE, tick))

    def OnNotifyTicks(
            self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
        return self._on_notify_tick(
            sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)

    def OnNotifyHistoryTicks(
            self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
        return self._on_notify_tick(
            sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)

    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        if bstrData[:len('1989/00/14')] == '1989/00/14':
            return

        [time_string, open_price, high_price, low_price, close_price, qty] = bstrData.split(',')
        if len(time_string) > 10:
            dt = datetime.strptime(time_string, '%Y/%m/%d %H:%M')
        else:
            dt = datetime.strptime(time_string, '%Y/%m/%d')

        candlestick = Candlestick(bstrStockNo, dt, open_price, high_price, low_price, close_price, qty)
        self.eventmgr(Event(MARKET_QUOTE, candlestick))

    def OnNotifyStockList(self, sMarketNo, bstrStockData):
        stock_list = []
        for stock_category in bstrStockData.split('\n'):
            for stock_info in stock_category.split(';'):
                s = stock_info.split(',')
                stock_list.append(s[0])
        self.eventmgr(Event(market_orderbook_list, stock_list))
