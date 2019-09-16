from .dll import Component


class Quote(Component):
    def __init__(self):
        super(Quote, self).__init__()
        self._component = self._Component__component_generator('quote')

    def enter_monitor(self):
        return self._component.SKQuoteLib_EnterMonitor()

    def leave_monitor(self):
        return self._component.SKQuoteLib_LeaveMonitor()

    def request_stocks(self, psPageNo, bstrStockNos):
        return self._component.SKQuoteLib_RequestStocks(psPageNo, bstrStockNos)

    def get_stock_by_index(self, sMarketNo, sIndex):
        return self._component.SKQuoteLib_GetStockByIndex(sMarketNo, sIndex)

    def get_stock_by_no(self, bstrStockNo):
        return self._component.SKQuoteLib_GetStockByNo(bstrStockNo)

    def request_ticks(self, psPageNo, bstrStockNo):
        return self._component.SKQuoteLib_RequestTicks(psPageNo, bstrStockNo)

    def get_tick(self, sMarketNo, sIndex, nPtr, pSKTick):
        return self._component.SKQuoteLib_GetTick(sMarketNo, sIndex, nPtr, pSKTick)

    def get_best_5(self, sMarketNo, sIndex, pSKBest5):
        return self._component.SKQuoteLib_GetBest5(sMarketNo, sIndex, pSKBest5)

    def request_k_line(self, bstrStockNo, sKLineType, sOutType):
        return self._component.SKQuoteLib_RequestKLine(bstrStockNo, sKLineType, sOutType)

    def request_server_time(self):
        return self._component.SKQuoteLib_RequestServerTime()

    def get_market_buy_sell_up_down(self):
        return self._component.SKQuoteLib_GetMarketBuySellUpDown()

    # def RequestMACD(self, psPageNo, bstrStockNo):
    #     return self._component.SKQuoteLib_RequestMACD(psPageNo, bstrStockNo)

    # def GetMACD(self, sMarketNo, sIndex, pSKMACD):
    #     return self._component.SKQuoteLib_GetMACD(sMarketNo, sIndex, pSKMACD)

    # def RequestBoolTunel(self, psPageNo, bstrStockNo):
    #     return self._component.SKQuoteLib_RequestBoolTunel(psPageNo, bstrStockNo)

    # def GetBoolTunel(self, sMarketNo, sIndex, pSKStock):
    #     return self._component.SKQuoteLib_GetBoolTunel(sMarketNo, sIndex, pSKStock)

    # def RequestFutureTradeInfo(self, psPageNo, bstrStockNo):
    #     return self._component.SKQuoteLib_RequestFutureTradeInfo(psPageNo, bstrStockNo)

    # def Delta(self, nCallPut, S, K, R, T, sigma, dDelta):
    #     return self._component.SKQuoteLib_Delta(nCallPut, S, K, R, T, sigma, dDelta)

    # def Gamma(self, S, K, R, T, sigma, dGamma):
    #     return self._component.SKQuoteLib_Gamma(S, K, R, T, sigma, dGamma)

    # def Theta(self, nCallPut, S, K, R, T, v, dTheta):
    #     return self._component.SKQuoteLib_Theta(nCallPut, S, K, R, T, v, dTheta)

    # def Vega(self, S, K, R, T, sigma, dVega):
    #     return self._component.SKQuoteLib_Vega(S, K, R, T, sigma, dVega)

    # def Rho(self, nCallPut, S, K, R, T, v, dRho):
    #     return self._component.SKQuoteLib_Rho(nCallPut, S, K, R, T, v, dRho)

    def get_strike_prices(self):
        return self._component.SKQuoteLib_GetStrikePrices()

    def request_k_line_am(self, bstrStockNo, sKLineType, sOutType, sTradeSession):
        return self._component.SKQuoteLib_RequestKLineAM(bstrStockNo, sKLineType, sOutType, sTradeSession)

    def request_stock_list(self, sMarketNo):
        return self._component.SKQuoteLib_RequestStockList(sMarketNo)

    def request_live_tick(self, psPageNo, bstrStockNo):
        return self._component.SKQuoteLib_RequestLiveTick(psPageNo, bstrStockNo)

    def is_connected(self):
        return self._component.SKQuoteLib_IsConnected()
