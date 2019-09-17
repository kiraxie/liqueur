import pythoncom
import signal
import math
from datetime import datetime

from .dll import new_stock_quote
from .center import Center
from .quote import Quote
from .reply import Reply
from .codes import return_codes, kbar_type, kbar_out_type, kbar_trade_session
from .structure import Tick, QuoteData, KBar, PriceQty, BestFivePrice


class SubscriptionMgr:
    __quote = []
    __detail = []
    __tick = []
    __kbar = []

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

    def __init__(self, subscription_conf=None):
        if subscription_conf is not None:
            if len(subscription_conf['quote']) > 0:
                for q in subscription_conf['quote']:
                    self.__quote.append(q)

            if len(subscription_conf['detail']) > 0:
                for d in subscription_conf['tick']:
                    self.__detail.append(d)

            if len(subscription_conf['tick']) > 0:
                for t in subscription_conf['tick']:
                    self.__tick.append(t)

            if len(subscription_conf['kbar']) > 0:
                for (orderbook_id, k_type) in subscription_conf['kbar']:
                    self.__kbar.append((str(orderbook_id), k_type))

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


class Liqueur:
    # Private variable
    __center = None
    __quote = None
    __reply = None

    subscription_mgr = None

    __config = {}
    __is_login = False
    __alive = True

    # Public variable
    __time_delegation = {}
    __message_delegation = {}
    __quote_delegation = {}
    __tick_delegation = {}
    __kbar_delegation = {}
    __best_five_delegation = {}

    # Private function
    def __message(self, message='', ret_code=-1, end='\n'):
        ''' Uniform message interface for class internal use.

        Args:
            [string]message: Message that you want to send.
            [return_codes]ret_code: The API return code, if this value isn't 0(success),
                the error message(via center module) will be appended to the message.
                Default: success(0)
            [string]end: Append this argument to the message tail.

        Returns:
            True: Means return code isn't success.
            False: Means return is success.
        '''
        err_ret = False

        if ret_code != return_codes.success and ret_code != -1:
            message += ('[%s]' % self.__center.get_return_code_msg(ret_code))
            err_ret = True

        if message != '' and ret_code == -1:
            Liqueur.excute_delegation(self.__message_delegation, message + end)

        return err_ret

    def __login(self):
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

        ret = self.__center.login(
            account_conf['username'], account_conf['password'])
        if self.__message('...fail!', ret_code=ret):
            return

        ret = self.__quote.enter_monitor()
        if self.__message('Quote server sign in fail! ', ret_code=ret):
            return

        self.__is_login = True
        self.__message(message='...ok')

    def __signal_handler(self, signum, frame):
        ''' The daemon signal handler.

        The main goal is to catch "ctrl + c" interrupt sig number to stop this application.

        More detail: https://docs.python.org/3/library/signal.html

        Args:
            (int)signum: The signal number.
            (frame)frame: The current stack frame (None or a frame object)

        Returns:
            None

        Raises:
            None
        '''
        self.__quote.leave_monitor()
        self.__alive = False

    def __send_heartbeat(self, dt=None):
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

        ret = self.__quote.request_server_time()
        if self.__message('Heartbeat miss! ', ret_code=ret):
            return

    def __subscription(self):
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
        for page_string in self.__subscription_mgr.quote:
            (page, ret) = self.__quote.request_stocks(-1, page_string)
            if self.__message('Quote subscription: ', ret_code=ret):
                return

        if len(self.__subscription_mgr.detail) > 0:
            for orderbook_id in self.__subscription_mgr.detail:
                (page, ret) = self.__quote.request_ticks(-1, orderbook_id)
                if self.__message('Quote detail subscription: ', ret_code=ret):
                    return
        else:
            for orderbook_id in self.__subscription_mgr.tick:
                (page, ret) = self.__quote.request_live_tick(-1, orderbook_id)
                if self.__message('Quote tick subscription: ', ret_code=ret):
                    return

        for (orderbook_id, kbar_type) in self.__subscription_mgr.kbar:
            ret = self.__quote.request_k_line_am(orderbook_id,
                                                 kbar_type, kbar_out_type.new, kbar_trade_session.daylight)
            if self.__message('Quote K bar subscription: ', ret_code=ret):
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
            self.__subscription_mgr = SubscriptionMgr(
                self.__config['subscription'])
        else:
            self.__subscription_mgr = SubscriptionMgr()
        self.__time_delegation[-1] = self.__send_heartbeat

    def __del__(self):
        ''' Liqueur application destructor

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        del self.__center
        del self.__quote
        del self.__reply

    # Event callback
    def OnReplyMessage(self, bstrUserID, bstrMessage, sConfirmCode=0xFFFF):
        ''' Detail in offical document 4-3-e'''
        return sConfirmCode

    def OnNotifyServerTime(self, sHour, sMinute, sSecond, nTotal):
        ''' Detail in offical document 4-4-g'''
        dt = datetime.combine(datetime.now(), datetime.strptime(
            (('%d:%d:%d') % (sHour, sMinute, sSecond)), '%H:%M:%S').time())
        Liqueur.excute_delegation(self.__time_delegation, dt)

    def OnConnection(self, nKind, nCode):
        ''' Detail in offical document 4-4-a'''
        if self.__message('', ret_code=nCode):
            return

        if nKind == return_codes.subject_connection_connected:
            self.__message(message='Connect...', end='')
        elif nKind == return_codes.subject_connection_disconnect:
            self.__message(message='Disconnect!')
            self.__alive = False
        elif nKind == return_codes.subject_connection_stocks_ready:
            self.__message(message='...success')
            self.__send_heartbeat()
            self.__subscription()
        elif nKind == return_codes.subject_connection_fail:
            self.__message(message='...failure')
            self.__alive = False
        else:
            self.__message(message='...', ret_code=nKind)

    def OnNotifyQuote(self, sMarketNo, sIndex):
        ''' Detail in offical document 4-4-b'''
        (p_stock, ret) = self.__quote.get_stock_by_index(sMarketNo, sIndex)
        if self.__message('', ret_code=ret):
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

        Liqueur.excute_delegation(self.__quote_delegation, stock_quote)

    def OnNotifyTicks(self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty,
                      nSimulate):
        ''' Detail in offical document 4-4-d'''
        (p_stock, ret) = self.__quote.get_stock_by_index(sMarketNo, sIndex)
        if self.__message('', ret_code=ret):
            return

        orderbook_id = p_stock.bstrStockNo
        name = p_stock.bstrStockName
        cardinal_num = math.pow(10, p_stock.sDecimal)
        bid = float(nBid / cardinal_num)
        ask = float(nAsk / cardinal_num)
        close = float(nClose / cardinal_num)

        tick = Tick.from_tick(nDate, nTimehms, nTimemillismicros,
                              orderbook_id, name, bid, ask, close, nQty, nSimulate)
        Liqueur.excute_delegation(self.__tick_delegation, tick)

    def OnNotifyHistoryTicks(self, sMarketNo, sIndex, nPtr, nDate, nTimehms, nTimemillismicros, nBid, nAsk, nClose,
                             nQty, nSimulate):
        ''' Detail in offical document 4-4-c'''
        (p_stock, ret) = self.__quote.get_stock_by_index(sMarketNo, sIndex)
        if self.__message('', ret_code=ret):
            return

        orderbook_id = p_stock.bstrStockNo
        name = p_stock.bstrStockName
        cardinal_num = math.pow(10, p_stock.sDecimal)
        bid = float(nBid / cardinal_num)
        ask = float(nAsk / cardinal_num)
        close = float(nClose / cardinal_num)

        tick = Tick.from_tick(nDate, nTimehms, nTimemillismicros,
                              orderbook_id, name, bid, ask, close, nQty, nSimulate)
        Liqueur.excute_delegation(self.__tick_delegation, tick)

    def OnNotifyKLineData(self, bstrStockNo, bstrData):
        ''' Detail in offical document 4-4-f'''
        kbar = KBar.from_kbar_string(bstrData)
        Liqueur.excute_delegation(self.__kbar_delegation, kbar)

    def OnNotifyBest5(self, sMarketNo, sStockidx, nBestBid1, nBestBidQty1, nBestBid2, nBestBidQty2, nBestBid3,
                      nBestBidQty3, nBestBid4, nBestBidQty4, nBestBid5, nBestBidQty5, nExtendBid, nExtendBidQty,
                      nBestAsk1, nBestAskQty1, nBestAsk2, nBestAskQty2, nBestAsk3, nBestAskQty3, nBestAsk4,
                      nBestAskQty4, nBestAsk5, nBestAskQty5, nExtendAsk, nExtendAskQty, nSimulate):
        ''' Detail in offical document 4-4-e'''
        bid_py = [PriceQty(nBestBid1, nBestBidQty1), PriceQty(nBestBid2, nBestBidQty2),
                  PriceQty(nBestBid3, nBestBidQty3), PriceQty(
                      nBestBid4, nBestBidQty4),
                  PriceQty(nBestBid5, nBestBidQty5)]
        ask_py = [PriceQty(nBestAsk1, nBestAskQty1), PriceQty(nBestAsk2, nBestAskQty2),
                  PriceQty(nBestAsk3, nBestAskQty3), PriceQty(
                      nBestAsk4, nBestAskQty4),
                  PriceQty(nBestAsk5, nBestAskQty5)]

        best_five = BestFivePrice.from_best_five(bid_py, ask_py)
        Liqueur.excute_delegation(self.__best_five_delegation, best_five)

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
        signal.signal(signal.SIGINT, self.__signal_handler)

        (qhandler, rhandler) = (self.__quote.hook_event(
            self), self.__reply.hook_event(self))

        self.__message(message='Login...', end='')
        self.__login()

        while self.__alive and self.__is_login:
            pythoncom.PumpWaitingMessages()

        if self.__is_login:
            self.__quote.leave_monitor()

    def hook_time(self, rule=0):
        ''' Decorator which hooks the time callback function.

        These functions will be excuted when time event was triggered.

        By default, the heartbeat was hooked on this delegation group in class initialization.

        Args:
            (int)rule: The excuted order.

        Returns:
            None

        Raises:
            None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__time_delegation, f, rule)
            return f
        return decorator

    def append_time_delegate(self, f):
        ''' function way to hook the time callback function.

        These functions will be excuted when time event was triggered.

        By default, the heartbeat was hooked on this delegation group in class initialization.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__time_delegation, f, 0)

    def hook_message(self, rule=0):
        ''' Decorator which hooks the message callback function.

        By default, the application DOES NOT print or log any message,
        so the developer can choose what it does when message pops out.

        Args:
            (int)rule: The excuted order.

        Returns:
            None

        Raises:
            None
        '''
        def decorator(f):
            self.__add_hook_callback(self.__message_delegation, f, rule)
            return f
        return decorator

    def append_message_delegate(self, f):
        ''' function way to hook the message callback function.

        By default, the application DOES NOT print or log any message,
        so the developer can choose what it does when message pops out.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__message_delegation, f, 0)

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
        ''' function way to hook the quote callback function.

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
        ''' function way to hook the tick callback function.

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
        ''' function way to hook the K bar callback function.

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
        ''' function way to hook the best five prices callback function.

        Args:
            (function point)func: Function pointer

        Returns:
            None

        Raises:
            None
        '''
        self.__add_hook_callback(self.__best_five_delegation, f, 0)

    @staticmethod
    def excute_delegation(delegation, *argv):
        ''' Excutes the delegation group functions.

        Args:
            (dictionary)delegation: The delegation group object.

        Returns:
            None

        Raises:
            TypeError: The delegation in invalid type.
        '''
        if not isinstance(delegation, dict):
            raise TypeError('The delegation group must be dictionary object')

        if len(delegation) == 0:
            return

        for rule, func in sorted(delegation.items(), key=lambda d: d[0]):
            if func is not None:
                func(*argv)