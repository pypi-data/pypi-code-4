'''
MarketSimualtor.py
Created on Apr 28, 2013

:author: Chen Huang
'''
from tradingmachine.Utils import *
from tradingmachine.DataFeed import *
from tradingmachine.sharedLogger import logger
from tradingmachine.Asset import *
import weakref


class OrderType(Utils.Enum):
    valueMap = {}

OrderTypeMarketLong = OrderType(0, "Market Long")
OrderTypeMarketShort = OrderType(1, "Market Short")
OrderTypeLimitShort = OrderType(3, "Limit Short")
OrderTypeLimitLong = OrderType(4, "Limit Long")


class Order():

    def __init__(self, symbol, orderType, orderQuantity, askingPrice):
        """
        Costbase is used to represent the cost for buy/sell of underlying asset.
        For example, in market orders, costbase will be the price of buy/sell underlying asset.
        In limit orders, costbase will be the asking price of buy/sell underlying asset.
        """
        self.orderID = None
        self.symbol = symbol
        self.orderType = orderType
        self.orderQuantity = orderQuantity
        self.time = None
        self.costbase = None
        self.fulfilled = False
        self.limitedOrderAskingPrice = askingPrice

    def __str__(self):
        return "[OrderID[{}]: {} {} {} @ ${}]".format(self.orderID, self.orderType, self.orderQuantity, self.symbol, self.costbase)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.orderID == other.orderID


class Policy():

    """
    A Policy defines what strategies can do and can not do.
    """
    pass


class MarketSimulator():

    def __init__(self, currentSimulatorTime=None, strategy=None):
        """
        MarketSimulator take a datetime object representing "now".
        All subsequent data is coming after now.

        :param  currentSimulatorTime:   Specify the time now. Simulator will use this time going forward.
        :type   currentSimulatorTime:   datetime.datetime
        """
        self.nextAvailableOrderID = 0
        self.now = currentSimulatorTime
        self._slippage = 0
        self.registeredSymbols = []
        self._orderRequests = []
        self._fulfilledOrders = []
        self._orderHistory = pd.DataFrame()     # TODO: A time series stores all the orders.
        self.PnL = 0
        self._pricesCache = {}
        self.registeredTransforms = []

        self.running = False    # This is used to indicate whether the simulator is running or not.
        if strategy:
            self._strategyWeakRef = weakref.ref(strategy)

    def setCurrentTime(self, currentSimulatorTime):
        self.now = currentSimulatorTime

    def currentTime(self):
        return self.now

    @property
    def getFulfilledOrders(self):
        return list(self._fulfilledOrders)

    def getHistoricalPrice(self, symbol, start, end=None, interval=IntervalPeriod1Minute):
        if not end or end > self.now:
            end = self.now
        asset = Assets.retrieveAssetFromSymbol(symbol)
        if (asset):
            historicalDataFrame = asset.load(start, end)
        return historicalDataFrame

    def addOrderRequest(self, order):
        # TODO: Add policy to examine orders.
        # To see if it's a valid order as well as if policy allows this order under current condition.
        order.orderID = self.nextAvailableOrderID
        self.nextAvailableOrderID += 1
        self._orderRequests.append(order)

    def addObserver(self, symbol):
        if not symbol in self.registeredSymbols:
            self.registeredSymbols.append(symbol)

    def removeObserver(self, symbol):
        if symbol in self.registeredSymbols:
            self.registeredSymbols.remove(symbol)

    def feedStrategyWith(self, symbol, data, time):
        strategy = self._strategyWeakRef()
        if (strategy):
            strategy.handleData(symbol, data, time)

    # @accepts(object, datetime, IntervalPeriod) This is not working yet. Should get this work.
    def run(self, until=None, interval=IntervalPeriod1Minute):
        """
        Start market simulator until specified date or until the last date/time of the database.
        :param  until:  The end time of the simulator.
                        If until is None, simulator will run until the end of the data feed.
        :type   until:  datetime.datetime
        """
        assert(self.now)

        logger.info("Market Simulator loading all data feed.")
        datafeed = None
        for symbol in self.registeredSymbols:
            datafeed = self.prepareSimulatorDataFeed(self.now, until)

        logger.info("Apply transforms to data feed.")
        datafeed = self.applyTransforms(datafeed)

        if datafeed is not None:
            self.running = True
            """
            The following code is a bit tricky and finished by trial and error. Needs futhur clarification from pandas.
            I found if datafeed.major_xs or transpose is called, the datafeed will erase the indicator columns
            created from applyTransforms.
            I guess it's because this data panel is not a valid data panel after introduce indicators to a symbol.
            For example:
            If we are loading @ES# and @test#, and only apply technical indicators to @ES#, although @ES# dataframe has the
            indicators, @test# doesn't have those. Therefore it does't form a valid 3D panel.

            So the following is kinda of avoid invoking major_xs or transpose function.
            """
            for timestamp in datafeed.major_axis:
                if (self.running):
                    self.now = timestamp.to_datetime()
                    for symbol in datafeed.items:
                        self.process(symbol, datafeed[symbol].loc[timestamp], timestamp)

        else:
            logger.info("Market simulator failed to load datafeed. Abort")

    def process(self, symbol, data, time):
        # Update price cache.
        self._pricesCache[symbol] = data
        self.orderProcessing(symbol, data, time)
        self.policyProcessing(symbol, data, time)
        self.feedStrategyWith(symbol, data, time)

    def orderProcessing(self, symbol, data, time):
        """
        This function processes current order requests.
        """
        if len(self._orderRequests) > 0:
            for order in self._orderRequests:
                fulfilled = False
                if symbol == order.symbol:
                    if order.orderType == OrderTypeMarketLong:
                        order.costbase = data["open"] + self._slippage
                        fulfilled = True
                    elif order.orderType == OrderTypeMarketShort:
                        order.costbase = data["open"] - self._slippage
                        fulfilled = True
                    elif order.orderType == OrderTypeLimitShort:
                        """
                        # TODO: limit orders need some careful design.
                        # In a simulated environment, try to simulate the best limit order possible.
                        There are a couple situations here in the limited order.
                        1. Asking price is bigger than data["high"].
                        2. Asking price is between High and Low.
                        3. Asking price is smaller than data["low"].

                        # Also current implementation doesn't take account of the order the bar is formed.
                        Is it form low first? or high first?
                        """
                        if self.limitedOrderAskingPrice <= (data["high"] + self._slippage):
                            fulfilled = True
                            # Determine the costbase.
                            if (data["low"] >= self.limitedOrderAskingPrice):
                                order.costbase = data["low"]
                            else:
                                order.costbase = self.limitedOrderAskingPrice
                    elif order.orderType == OrderTypeLimitLong:
                        if self.limitedOrderAskingPrice > (data["low"] - self._slippage):
                            fulfilled = True
                            # Determine the cost base.
                            if (data["high"] <= self.limitedOrderAskingPrice):
                                order.costbase = data["high"]
                            else:
                                order.costbase = self.limitedOrderAskingPrice
                    order.fulfilled = fulfilled
                    if (fulfilled):
                        self._fulfilledOrders.append(order)
                        strategy = self._strategyWeakRef()
                        if (strategy):
                            strategy.handleOrder(order)
            # Remove fulfilled order.
            self._orderRequests = [order for order in self._orderRequests if not order.fulfilled]

    def policyProcessing(self, symbol, data, time):
        """
        This function evaluates current policy when a new market data arrives.
        """
        pass

    def stop(self):
        self.running = False

    def pause(self):
        pass

    def resume(self):
        pass

    def getPnL(self):
        '''
        # TODO: improve this function. Is caching going to help here?

        # TODO: There is a quicker way to calculating pnl.
        negate all long cost plus all short costs.

        We might also need to get the orders into a pandas dataframe too to speed things up in multi symbol environment.
        Python native list is not suitable for multi symbol environment.
        Also sorting might be easier.
        '''
        pnl = 0
        for order in self._fulfilledOrders:
            if order.orderType == OrderTypeMarketLong or order.orderType == OrderTypeLimitLong:
                pnl -= (self._pricesCache[order.symbol]["close"] - order.costbase) * order.orderQuantity
            else:
                pnl += (order.costbase - self._pricesCache[order.symbol]["close"]) * order.orderQuantity
        return pnl

    def prepareSimulatorDataFeed(
            self, startFrom, endsOn,
            symbols=None,
            interval=DataFeed.IntervalPeriod1Minute,
            tradingPeriod=DataFeed.TradingPeriodDay):
        """
        This function prepare a hierarchical dataframe.
        First index is datetime, second index is symbol.
        This dataframe is useful for simulator.
        """
        if not symbols:
            symbols = self.registeredSymbols
        logger.info("Prepare simulator data feed for {} from {} to {}.".format(", ".join(symbols), startFrom, endsOn))
        # loadedSymbols = []
        # dataframes = []

        dataframes = {}

        loadedSimulatorDataFrame = None
        for symbol in symbols:
            asset = sharedAssets.retrieveAssetFromSymbol(symbol)
            if (asset):
                dataframes[asset.symbol] = asset.load(startFrom, endsOn)
                # dataframes.append(asset.load(startFrom, endsOn))
                # loadedSymbols.append(asset.symbol)
            else:
                logger.debug("Failed to retrieve asset {}.".format(symbol))

        if (dataframes):
            # loadedSimulatorDataFrame = pd.concat(dataframes, axis=1, keys=loadedSymbols)
            loadedSimulatorDataFrame = pd.Panel(dataframes)
        else:
            logger.warning("There aren't any assets loaded.")

        return loadedSimulatorDataFrame

    def setSlippage(self, value):
        """
        Slippage is the cost used for an order to be executed in a simulated environment.
        Slippage is different than the service fee that each order is charged at a fixed rate by the broker.
        Slippage is to ensure that the order will be executed for sure in the real-time environment.real-time

        If an order is a limit long order, the price is set to X.
        The order will be executed if and only if the actual price went below X - Slippage.
        If an order is a limit short ordre, the price is set to X,
        The order will be executed if and oly if the actual price went above X + Slippage.
        """
        self._slippage = value

    def getSlippage(self):
        return self._slippage

    def registerTransform(self, func, symbol, desiredname, tag, args, kwargs):
        self.registeredTransforms.append({
            "func": func,
            "symbol": symbol,
            "desiredname": desiredname,
            "tag": tag,
            "args": args,
            "kwargs": kwargs})

    def applyTransforms(self, datafeed):
        # TODO: check dependency and assumption and error out if such dependency or assumption doens't meet.

        for transform in self.registeredTransforms:
            inputs = datafeed[transform["symbol"]]
            transformedData = transform["func"](inputs, *(transform["args"]), price=transform["tag"], **(transform["kwargs"]))
            datafeed[transform["symbol"]][transform["desiredname"]] = pd.Series(
                transformedData,
                index=datafeed[transform["symbol"]].index
            )

        return datafeed
