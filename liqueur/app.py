import pythoncom

from datetime import datetime

from .center import Center
from .quote import Quote
from .reply import Reply
from .codes import err_codes
from .util import Attributes
from .marketboard import MarketBoard
from .sqlalchemy import LiqueurSqlAlchemy
from .applog import AppLog
from .extention import ExtentionManager


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
    _ctx = None
    _market_board = None
    _trade_board = None
    _extention_mgr = ExtentionManager()

    # Public variable

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

        if self._corelog(self.__quote.enter_monitor(), 'Connect quote server...ok'):
            raise LoginError

    def _send_heartbeat(self, dt=datetime.now()):
        if not self._alive or Today.replace(hour=14, minute=0) < dt:
            return

        if dt is not None and dt.second % 10 != 0:
            return

        if self._corelog(self.__quote.request_server_time()):
            self.stop()

    def __init__(self, conf):
        self.__center = Center(conf)
        self.__quote = Quote()
        self.__reply = Reply()

        AppLog(conf.applog)

        self._market_board = MarketBoard(Attributes({
            'stop': self.stop,
            'connect': self.__quote.enter_monitor,
            'disconnect': self.__quote.leave_monitor,
            'corelog': self._corelog,
            'send_heartbeat': self._send_heartbeat,
            'get_profile': self.__quote.get_stock_by_index,
            'fetch_orderbook': self.__quote.request_stock_list,
            'subscribe_tick': self.__quote.request_ticks,
            'subscribe_candlestick': self.__quote.request_k_line_am,
            'on_quote': self._extention_mgr.on_quote,
        }), conf.marketboard)

        self._extention_mgr.add('db', LiqueurSqlAlchemy(Attributes({
            'stop': self.stop,
        }), conf.sqlalchemy))

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

        while self._alive:
            pythoncom.PumpWaitingMessages()

        self._extention_mgr.wait()

    def stop(self):
        if self._alive:
            self._alive = False
            self.__quote.leave_monitor()
            self._extention_mgr.stop()
