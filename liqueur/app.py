from typing import Callable
from liqueur.database.database import SchemaBase
import pythoncom

from datetime import datetime

from .center import Center
from .quote import Quote
from .reply import Reply
from .codes import err_codes
from .util import Attributes
from .marketboard import MarketBoard, MARKET_QUOTE
from .applog import AppLog
from .extention import ExtentionManager
from .database import Database
from .event import EventManager, SYS_EVENT_TIMER

Today = datetime.today()
log = AppLog.get('liqueur')


class LoginError(BaseException):
    pass


class Liqueur:
    # Private variable
    __center = None
    __quote = None
    __reply = None

    __corelog = AppLog.get('liqueur.core')

    _alive = True
    _is_service = False
    _market_board = None
    _trade_board = None
    _extention_mgr = ExtentionManager()

    # Public variable
    db: Database = None

    # Private function
    def _corelog(self, err, message=''):
        if err != err_codes.success:
            self.__corelog.error(self.__center.get_return_code_msg(err))
            return True

        if message != '':
            log.info(message)

        return False

    def _login(self):
        if self._corelog(self.__center.login(), 'Login...ok'):
            raise LoginError

    def __init__(self, conf):
        AppLog(conf.applog)
        self.__center = Center(conf)
        self.__quote = Quote()
        self.__reply = Reply()
        self.conf = conf

        eventmgr: EventManager = EventManager(10)
        self._extention_mgr.add(eventmgr)

        on_quote: Callable = None
        if conf.database.host != "":
            db: Database = Database(conf.database.host, SchemaBase)
            self._extention_mgr.add(db)
            on_quote = db.async_create
        else:
            on_quote = AppLog.get('dev').debug
        eventmgr.register_callback(MARKET_QUOTE, on_quote)

        def send_heartbeat():
            if self._corelog(self.__quote.request_server_time()):
                self.stop()

        self._market_board = MarketBoard(eventmgr, Attributes({
            'stop': self.stop,
            'corelog': self._corelog,
            'send_heartbeat': send_heartbeat,
            'get_profile': self.__quote.get_stock_by_index,
            'fetch_orderbook': self.__quote.request_stock_list,
            'subscribe_tick': self.__quote.request_ticks,
            'subscribe_candlestick': self.__quote.request_k_line_am,
            'on_quote': on_quote,
        }), conf.marketboard)

    def __del__(self):
        if self.__center is not None:
            del self.__center
        if self.__quote is not None:
            del self.__quote
        if self.__reply is not None:
            del self.__reply

    # Event callback
    def OnReplyMessage(self, bstrUserID, bstrMessage, sConfirmCode=0xFFFF):
        return sConfirmCode

    # Public function
    def start(self):
        (qhandler, rhandler) = (self.__quote.hook_event(self._market_board), self.__reply.hook_event(self))
        self._extention_mgr.start()

        try:
            self._login()
        except:
            log.error('login fail!')
            return

        evtmgr: EventManager = self._extention_mgr.get('EventManager')
        open: datetime = datetime.strptime(self.conf.market_open, "%H:%M")
        close: datetime = datetime.strptime(self.conf.market_close, "%H:%M")

        def market_open(dt: datetime):
            if dt >= datetime.combine(
                    datetime.now(),
                    open.time()) and dt < datetime.combine(
                    datetime.now(),
                    close.time()) and self._is_service is False:
                self._is_service = True
                log.info('market open')
                if self._corelog(self.__quote.enter_monitor(), 'Connect quote server...ok'):
                    raise LoginError
        evtmgr.register_callback(SYS_EVENT_TIMER, market_open)

        def market_close(dt: datetime):
            if dt >= datetime.combine(datetime.now(), close.time()) and self._is_service:
                self._is_service = False
                log.info('market close')
                self.__quote.leave_monitor()
        evtmgr.register_callback(SYS_EVENT_TIMER, market_close)

        while self._alive:
            pythoncom.PumpWaitingMessages()

        self._extention_mgr.wait()

    def stop(self):
        if self._alive:
            self._alive = False
            self.__quote.leave_monitor()
            self._extention_mgr.stop()
