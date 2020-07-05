import pythoncom
import math
from datetime import datetime
from threading import Thread
import logging

from .center import Center
from .quote import Quote
from .reply import Reply
from .codes import err_codes, kbar_type, kbar_out_type, kbar_trade_session
from .structure import Tick, QuoteData, KBar, PriceQty, BestFivePrice
from .sqlalchemy import LiqueurSqlAlchemy


Today = datetime.today()


class SubscriptionMgr:
    __quote = []
    __detail = []
    __tick = []
    __kbar = []
    __stocks_of_market = []

    @property
    def quote(self):
        page_list = []

        while len(self.__quote) > 0:
            pos = min(len(self.__quote), 99)
            page_list.append(','.join('%s' % id for id in self.__quote[:pos]))
            self.__quote = self.__quote[pos + 1:]

        return page_list

    @property
    def detail(self):
        return self.__detail

    @property
    def tick(self):
        return self.__tick

    @property
    def kbar(self):
        return self.__kbar

    @property
    def stocks_of_market(self):
        return self.__stocks_of_market

    def __load_quote(self, quote_conf):
        if len(quote_conf) > 0:
            for q in quote_conf:
                self.__quote.append(str(q))

    def __load_detail(self, detail_conf):
        if len(detail_conf) > 0:
            for d in detail_conf:
                self.__detail.append(str(d))

    def __load_tick(self, tick_conf):
        if len(tick_conf) > 0:
            for t in tick_conf:
                self.__tick.append(str(t))

    def __load_kbar(self, kbar_conf):
        if len(kbar_conf) > 0:
            for (orderbook_id, k_type) in kbar_conf:
                self.__kbar.append((str(orderbook_id), k_type))

    def __load_stocks_of_market(self, stocks_of_market_conf):
        if len(stocks_of_market_conf) > 0:
            for market in stocks_of_market_conf:
                self.__stocks_of_market.append(int(market))

    def __init__(self, subscription_conf=None):
        if subscription_conf is not None:
            self.load(subscription_conf)

    def load(self, subscription_conf):
        if 'quote' in subscription_conf:
            self.__load_quote(subscription_conf['quote'])

        if 'detail' in subscription_conf:
            self.__load_detail(subscription_conf['detail'])

        if 'tick' in subscription_conf:
            self.__load_tick(subscription_conf['tick'])

        if 'kbar' in subscription_conf:
            self.__load_kbar(subscription_conf['kbar'])

        if 'stocks_of_market' in subscription_conf:
            self.__load_stocks_of_market(subscription_conf['stocks_of_market'])

    def clear(self, item=None):
        if item is None:
            self.__quote = []
            self.__detail = []
            self.__tick = []
            self.__kbar = []
            self.__stocks_of_market = []
        elif item == 'quote':
            self.__quote = []
        elif item == 'detail':
            self.__detail = []
        elif item == 'kbar':
            self.__kbar = []
        elif item == 'stock_of_market':
            self.__stock_of_market = []

    def append_stock_quote(self, orderbook_id):
        self.__quote.append(str(orderbook_id))

    def append_detail(self, orderbook_id):
        if len(self.__detail) > 49:
            raise ValueError('The max stock detail subscription number is 49.')

        if len(self.__tick) > 0:
            self.__tick.clear()

        self.__detail.append(str(orderbook_id))

    def append_tick_only(self, orderbook_id):
        if len(self.__tick) > 49:
            raise ValueError('The max stock tick subscription number is 49.')

        if len(self.__detail) > 0:
            self.__detail.clear()

        self.__tick.append(str(orderbook_id))

    def append_kbar(self, orderbook_id, kbar_type):
        self.__kbar.append((str(orderbook_id), kbar_type))

    def append_stocks_of_market(self, market):
        self.__stocks_of_market.append(int(market))


class Liqueur:
    # Private variable
    __center = None
    __quote = None
    __reply = None

    __config = {}
    __alive = True
    __applog = None
    __corelog = None
    __shutdown = 0

    __extension = []

    __quote_delegation = {}
    __tick_delegation = {}
    __kbar_delegation = {}
    __best_five_delegation = {}
    __stocks_of_market_delegation = {}

    # Public variable
    subscription_mgr = None

    # Property
    @property
    def config(self):
        return self.__config

    # Private function
    def _corelog(self, err, level=logging.NOTSET, message=''):
        ''' A logging instance to log Capital internal message.

            More detail: https://docs.python.org/3/library/logging.html

            This function will log the error message when error code not success.
            Otherwise, will log the message with level if provide
        Args:
            [err_codes]err: The API return code, if this value isn't 0(success),
                the error message(via center module) will be logging with error level.
            [logging.level]level: Logging level which decide the message level.
            [string]message: Log this message if err is success.

        Returns:
            True: Means err isn't success.
            False: Means return is success.
        '''
        if err != err_codes.success:
            self.__corelog.error(self.__center.get_return_code_msg(err))
            return True

        log_fn = {
            logging.INFO: self.__applog.info,
            logging.WARN: self.__applog.warning,
            logging.ERROR: self.__applog.error,
            logging.CRITICAL: self.__applog.critical,
        }.get(level, self.__applog.debug)

        if message != '':
            log_fn(message)

        return False

    def _add_extension(self, t):
        if not isinstance(t, Thread):
            self.__applog.error('the class is not inheritance from Thread')
            return

        self.__extension.append(t)

    def _login(self):
        ''' Sign in the Capital server and enter the quote receiving mode.

        The attribute "account" has to exist in configuration object and
        the attributes "username" and "password" have to exist in account object.

        For example:
            {
                "account": {
                    "username": "A123456789",
                    "password": "xxxxxxxx"
                }
            }

        Args:
            None

        Returns:
            None

        Raises:
            AttributeError: The configuration lacks necessary attributes.
        '''
        if 'account' not in self.__config:
            raise AttributeError(
                'Invalid config format!'
                'The \"account\" attribute doesn\'t exist!'
            )

        account_conf = self.__config['account']

        if 'username' not in account_conf or 'password' not in account_conf:
            raise AttributeError(
                'Invalid config format! '
                'The \"username\" or \"password\" attribute doesn\'t exist!'
            )

        err = self.__center.login(account_conf['username'], account_conf['password'])
        if self._corelog(err, logging.INFO, 'Login...ok'):
            return

        err = self.__quote.enter_monitor()
        if self._corelog(err, logging.INFO, 'Connect quote server...ok'):
            return

    def _send_heartbeat(self, dt=None):
        ''' Send heartbeat to Capital server.

        It's a suggested by Capital to send a server time request as heartbeat every 15 secs.

        Args:
            (datetime)dt: The datetime object.

        Returns:
            None

        Raises:
            None
        '''
        if not self.__alive:
            return

        if dt is not None and dt.second % 15 != 0:
            return

        err = self.__quote.request_server_time()
        if self._corelog(err):
            self.stop()

    def _subscription(self):
        ''' Internal market data subscription.

        Considering the orignal subscription is diffcult for maintenance,
        liqueur offers an easy way to market data subscription.

        This function depends on the SubscriptionMgr class implementation.

        For some reason, either the detail(history tick, live tick and best five price) or
        tick(live tick only) can be chosen.

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        for page_string in self.subscription_mgr.quote:
            (page, err) = self.__quote.request_stocks(-1, page_string)
            if self._corelog(err):
                return

        if len(self.subscription_mgr.detail) > 0:
            for orderbook_id in self.subscription_mgr.detail:
                (page, err) = self.__quote.request_ticks(-1, orderbook_id)
                if self._corelog(err):
                    return
        else:
            for orderbook_id in self.subscription_mgr.tick:
                (page, err) = self.__quote.request_live_tick(-1, orderbook_id)
                if self._corelog(err):
                    return

        for (orderbook_id, kbar_type) in self.subscription_mgr.kbar:
            err = self.__quote.request_k_line_am(orderbook_id,
                                                 kbar_type, kbar_out_type.new, kbar_trade_session.daylight)
            if self._corelog(err):
                return

        for market in self.subscription_mgr.stocks_of_market:
            err = self.__quote.request_stock_list(market)
            if self._corelog(err):
                return

    def __add_hook_callback(self, delegation_map, func, rule):
        ''' Uniform callback delegation interface.

        Args:
            (dictionary)delegation_map: The delegation map object.
            (function point)func: Function pointer
            (int)rule: Task rules of sequence.

        Returns:
            None

        Raises:
            Warning: A mapping overwriting when rule exists.
        '''
        if rule == 0:
            rule = len(delegation_map)
            while rule in delegation_map:
                rule += 1
        else:
            rule = abs(rule)
        old_func = delegation_map.get(rule)

        if old_func is not None and old_func != func:
            raise Warning(
                "Function mapping is overwriting an "
                "existing task function rule: %d" % rule
            )

        delegation_map[rule] = func

    def __excute_delegation(self, delegation, *argv):
        ''' Excutes the delegation group functions.

        Args:
            (dictionary)delegation: The delegation group object.

        Returns:
            None

        Raises:
            TypeError: The delegation in invalid type.
        '''
        if not isinstance(delegation, dict):
            raise TypeError('The delegation group must be dictionary object.')

        if len(delegation) == 0:
            return

        for rule, func in sorted(delegation.items(), key=lambda d: d[0]):
            if func is not None:
                func(*argv)

    def _on_time(self, dt):
        if True:
            self.__applog.info(dt)

        if Today.replace(hour=14, minute=45) < dt:
            self.__shutdown += 1
            if self.__shutdown >= 60:
                self.__applog.info('cheers!')
                self.stop()

    def __init__(self, conf):
        ''' Liqueur application constructor

        Args:
            (Config)conf: The configuration object.

        Returns:
            None

        Raises:
            None
        '''
        self.__center = Center()
        self.__quote = Quote()
        self.__reply = Reply()

        self.__config = conf
        if 'subscription' in self.__config:
            self.subscription_mgr = SubscriptionMgr(
                self.__config['subscription'])
        else:
            self.subscription_mgr = SubscriptionMgr()

        logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")
        self.__applog = logging.getLogger('liqueur')
        self.__corelog = logging.getLogger('liqueur.core')

        if 'sqlalchemy' in conf:
            db = LiqueurSqlAlchemy(self, conf['sqlalchemy'])
            self._add_extension(db)
            self.append_tick_delegate(db.on_tick)
            self.append_kbar_delegate(db.on_candlestick)
            self.append_quote_delegate(db.on_quote)

    def __del__(self):
        ''' Liqueur application destructor

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__center is not None:
            del self.__center
        if self.__quote is not None:
            del self.__quote
        if self.__reply is not None:
            del self.__reply

    # Event callback
    def OnReplyMessage(self, bstrUserID, bstrMessage, sConfirmCode=0xFFFF):
        ''' Detail in offical document 4-3-e'''
        return sConfirmCode

    def OnNotifyServerTime(self, sHour, sMinute, sSecond, nTotal):
        ''' Detail in offical document 4-4-g'''
        dt = datetime.combine(datetime.now(), datetime.strptime(
            (('%d:%d:%d') % (sHour, sMinute, sSecond)), '%H:%M:%S').time())
        self._on_time(dt)

    def OnConnection(self, nKind, nCode):
        ''' Detail in offical document 4-4-a'''
        if self._corelog(nCode):
            self.stop()
            return

        if nKind == err_codes.subject_connection_connected:
            self.__applog.info('Session...established')
        elif nKind == err_codes.subject_connection_disconnect:
            self.__applog.warning('Session...disconnect')
            self.__alive = False
        elif nKind == err_codes.subject_connection_stocks_ready:
            self.__applog.info('Session...ready')
            self._send_heartbeat()
            self._subscription()
        elif nKind == err_codes.subject_connection_fail:
            self.__applog.error('Connection failure')
            self.__alive = False
        else:
            self._corelog(nKind)

    def OnNotifyQuote(self, sMarketNo, sIndex):
        ''' Detail in offical document 4-4-b'''
        (p_stock, err) = self.__quote.get_stock_by_index(sMarketNo, sIndex)
        if self._corelog(err):
            return

        orderbook_id = p_stock.bstrStockNo
        name = p_stock.bstrStockName
        cardinal_num = math.pow(10, p_stock.sDecimal)
        high_price = float(p_stock.nHigh / cardinal_num)
        open_price = float(p_stock.nOpen / cardinal_num)
        low_price = float(p_stock.nLow / cardinal_num)
        close_price = float(p_stock.nClose / cardinal_num)
        bid_price = float(p_stock.nBid / cardinal_num)
        bid_qty = p_stock.nBc
        ask_price = float(p_stock.nAsk / cardinal_num)
        ask_qty = p_stock.nAc
        buy_qty = p_stock.nTBc
        sell_qty = p_stock.nTAc
        tick_qty = p_stock.nTickQty
        total_qty = p_stock.nTQty
        ref_qty = p_stock.nYQty
        ref_price = float(p_stock.nRef / cardinal_num)
        up_price = float(p_stock.nUp / cardinal_num)
        down_price = float(p_stock.nDown / cardinal_num)
        simulate = p_stock.nSimulate

        stock_quote = QuoteData.from_quote(orderbook_id, name, high_price, open_price, low_price, close_price,
                                           bid_price, bid_qty, ask_price, ask_qty, buy_qty, sell_qty, tick_qty,
                                           total_qty, ref_qty, ref_price, up_price, down_price, simulate)

        self.__excute_delegation(self.__quote_delegation, stock_quote)

    def OnNotifyTicks(self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty,
                      nSimulate):
        ''' Detail in offical document 4-4-d'''
        (p_stock, err) = self.__quote.get_stock_by_index(sMarketNo, sIndex)
        if self._corelog(err):
            return

        orderbook_id = p_stock.bstrStockNo
        name = p_stock.bstrStockName
        cardinal_num = math.pow(10, p_stock.sDecimal)
        bid = float(nBid / cardinal_num)
        ask = float(nAsk / cardinal_num)
        close = float(nClose / cardinal_num)

        tick = Tick.from_tick(nDate, nTimehms, nTimemillismicros,
                              orderbook_id, name, bid, ask, close, nQty, nSimulate)
        self.__excute_delegation(self.__tick_delegation, tick)

    def OnNotifyHistoryTicks(self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose,
                             nQty, nSimulate):
        ''' Detail in offical document 4-4-c'''
        (p_stock, err) = self.__quote.get_stock_by_index(sMarketNo, sIndex)
        if self._corelog(err):
            return

        orderbook_id = p_stock.bstrStockNo
        name = p_stock.bstrStockName
        cardinal_num = math.pow(10, p_stock.sDecimal)
        bid = float(nBid / cardinal_num)
        ask = float(nAsk / cardinal_num)
        close = float(nClose / cardinal_num)

        tick = Tick.from_tick(nDate, nTimehms, nTimemillismicros,
                              orderbook_id, name, bid, ask, close, nQty, nSimulate)
        self.__excute_delegation(self.__tick_delegation, tick)

    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        ''' Detail in offical document 4-4-f'''
        if bstrData[:len('1989/00/14')] == '1989/00/14':
            return

        kbar = KBar.from_kbar_string(bstrStockNo, bstrData)
        self.__excute_delegation(self.__kbar_delegation, kbar)

    def OnNotifyBest5(self, sMarketNo, sStockidx, nBestBid1, nBestBidQty1, nBestBid2, nBestBidQty2, nBestBid3,
                      nBestBidQty3, nBestBid4, nBestBidQty4, nBestBid5, nBestBidQty5, nExtendBid, nExtendBidQty,
                      nBestAsk1, nBestAskQty1, nBestAsk2, nBestAskQty2, nBestAsk3, nBestAskQty3, nBestAsk4,
                      nBestAskQty4, nBestAsk5, nBestAskQty5, nExtendAsk, nExtendAskQty, nSimulate):
        ''' Detail in offical document 4-4-e'''
        (p_stock, err) = self.__quote.get_stock_by_index(sMarketNo, sStockidx)
        if self._corelog(err):
            return

        orderbook_id = p_stock.bstrStockNo
        cardinal_num = math.pow(10, p_stock.sDecimal)

        bid_py = [PriceQty(nBestBid1, nBestBidQty1), PriceQty(nBestBid2, nBestBidQty2),
                  PriceQty(nBestBid3, nBestBidQty3), PriceQty(nBestBid4, nBestBidQty4),
                  PriceQty(nBestBid5, nBestBidQty5)]
        ask_py = [PriceQty(nBestAsk1, nBestAskQty1), PriceQty(nBestAsk2, nBestAskQty2),
                  PriceQty(nBestAsk3, nBestAskQty3), PriceQty(nBestAsk4, nBestAskQty4),
                  PriceQty(nBestAsk5, nBestAskQty5)]

        best_five = BestFivePrice.from_best_five(orderbook_id, bid_py, ask_py)
        self.__excute_delegation(self.__best_five_delegation, best_five)

    def OnNotifyStockList(self, sMarketNo, bstrStockData):
        stock_list = []
        for stock_category in bstrStockData.split('\n'):
            for stock_info in stock_category.split(';'):
                s = stock_info.split(',')
                stock_list.append(s[0])

        self.__excute_delegation(self.__stocks_of_market_delegation, sMarketNo, stock_list)

    # Public function
    def run(self):
        ''' Runs the application.

        The function follows the steps as below:
            1. Hook the application signal event.
            2. Hook the API event to API module.
            3. Sign in to Capital server.
            4. Waitting the application until terminating.
            5. Exit the quote receiving mode when application terminates.

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        for t in self.__extension:
            t.start()

        (qhandler, rhandler) = (self.__quote.hook_event(self), self.__reply.hook_event(self))

        self._login()

        while self.__alive:
            pythoncom.PumpWaitingMessages()

        for t in self.__extension:
            t.join()

    def stop(self):
        ''' Terminate the application.

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__alive:
            self.__quote.leave_monitor()
            for t in self.__extension:
                t.stop()

    def hook_quote(self, rule=0):
        ''' Decorator which hooks the quote callback function.

        Returns:
            None

        Raises:
            None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__quote_delegation, f, rule)
            return f
        return decorator

    def append_quote_delegate(self, f):
        ''' Function way to hook the quote callback function.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__quote_delegation, f, 0)

    def hook_tick(self, rule=0):
        ''' Decorator which hooks the tick callback function.

        Returns:
            None

        Roseesg   None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__tick_delegation, f, rule)
            return f
        return decorator

    def append_tick_delegate(self, f):
        ''' Function way to hook the tick callback function.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__tick_delegation, f, 0)

    def hook_kbar(self, rule=0):
        ''' Decorator which hooks the K bar callback function.

        Returns:
            None

        Roseesg   None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__kbar_delegation, f, rule)
            return f
        return decorator

    def append_kbar_delegate(self, f):
        ''' Function way to hook the K bar callback function.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__kbar_delegation, f, 0)

    def hook_best_five(self, rule=0):
        ''' Decorator which hooks the best five prices callback function.

        Returns:
            None

        Raises:
            None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__best_five_delegation, f, rule)
            return f
        return decorator

    def append_best_five_delegate(self, f):
        ''' Function way to hook the best five prices callback function.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__best_five_delegation, f, 0)

    def hook_stocks_of_market(self, rule=0):
        ''' Decorator which hooks the stock of market callback function.

        Returns:
            None

        Raises:
            None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__stocks_of_market_delegation, f, rule)
            return f
        return decorator

    def append_stocks_of_market_delegate(self, f):
        ''' Function way to hook the stock of market callback function.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__stocks_of_market_delegation, f, 0)

    def subscription(self, subscription_conf=None):
        ''' Subscribe the stock information from market.

        Args:
            [dictionary]subscription_conf: The stock orderbood id dictionary.

        Returns:
            None

        Raises:
            None
        '''
        if subscription_conf is not None:
            self.subscription_mgr.clear()
            self.subscription_mgr.load(subscription_conf)

        self._subscription()
