'''
Strategy.py
Created on Apr 28, 2013

:author: Chen Huang
'''
from abc import ABCMeta, abstractmethod
from tradingmachine.MarketSimulator.MarketSimulator import *


class Strategy(metaclass=ABCMeta):

    def __init__(self):
        """
        :param  symbols:    symbols to intialize.
        :type   symbols:    list of str
        :description:   initialize a strategy.
        """
        # Strategy initialize a historical data (pandas dataframe) from symbols.
        # for symbol in symbols:
        #     setattr(self, symbol, None)
        # self.marketSimulator = None
        self.symbols = []
        self.marketSimulator = MarketSimulator(strategy=self)

    @abstractmethod
    def setup(self):
        # initialize function is called before strategy is ran.
        pass

    def registerTransform(self, func, symbol, desiredname, tag, *args, **kwargs):
        """
        Register transform.
        :param  func: The function that will be applied to the data frame.
        :param  desiredname: The name to be given to the new generated column.
        :param  tag: The name of the column of dataframe to apply func on. Such as "close", "open", "high", "low".
                            It can also be any transformation registered before.
                            For example, if an SMA has been registered before as the name of "sma".
                            The pricename can be "sma". It will be the sma of the sma of pricename. (double SMA)
        :param  args: The positional args to be passed into func.
        :param  kwargs: The keyword arguments to be passed into func.
        """
        self.marketSimulator.registerTransform(func, symbol, desiredname, tag, args, kwargs)

    @abstractmethod
    def handleData(self, symbol, newData, time):
        # handleData will be called once there is a new data ready.
        # subclass must overload this function.
        pass

    def sendOrder(self, order):
        if self.marketSimulator:
            self.marketSimulator.addOrderRequest(order)

    @abstractmethod
    def handleOrder(self, order):
        pass

    def registerSymbol(self, symbol):
        self.symbols.append(symbol)

    @abstractmethod
    def teardown(self):
        pass

    def getFulfilledOrders(self):
        if self.marketSimulator:
            return self.marketSimulator.getFulfilledOrders

    def getPnL(self):
        if self.marketSimulator:
            return self.marketSimulator.getPnL()

    def backTest(self, startFrom, endsOn):
        """
        BackTest through timeframe.
        """
        self.marketSimulator.setCurrentTime(startFrom)
        for symbol in self.symbols:
            self.marketSimulator.addObserver(symbol)
        self.marketSimulator.run(until=endsOn)
