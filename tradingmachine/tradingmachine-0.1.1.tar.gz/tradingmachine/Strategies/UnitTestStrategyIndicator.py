from tradingmachine.Strategies.Strategy import *
from tradingmachine.Asset import *
from tradingmachine.sharedLogger import logger
import pandas as pd
import numpy as np
from tradingmachine.Indicators.Indicator import TAIndicator

from talib.abstract import SMA


class UnitTestStrategyIndicator(Strategy):

    def __init__(self):
        super().__init__()

    def setup(self):
        self.symbol = "@ES#"

        # Register S&P 500 Emini as one of our monitoring ticker symbol.
        self.registerSymbol(self.symbol)

        # Logging a message.
        logger.info("Registering Transforms.")

        # Register a 10 data points Simple Moving average on the close price of S&P 500 Emini.
        # Use "SMA10" as the name of the new calculated column.
        self.registerTransform(func=TAIndicator("SMA"), symbol=self.symbol, desiredname="SMA10", tag="close", timeperiod=10)

        # Register a 30 data points Simple Moving average on the close price of S&P 500 Emini.
        # Use "SMA30" as the name of the new calculated column.
        self.registerTransform(func=TAIndicator("SMA"), symbol=self.symbol, desiredname="SMA30", tag="close", timeperiod=30)

        # Register a 30 data points Simple Moving average on the SMA10 price of S&P 500 Emini.
        # Use "SMA30_SMA10" as the name of the new calculated column.
        self.registerTransform(func=TAIndicator("SMA"), symbol=self.symbol, desiredname="SMA30_SMA10", tag="SMA10", timeperiod=30)

        # The following are the testing code.
        SP500 = sharedAssets.retrieveAssetFromSymbol(self.symbol)
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 28, 10, 30, 0)
        self.verifyDF = SP500.load(startFrom, endsOn)
        input_arrays = {"close": np.asarray(self.verifyDF["close"]),
                        "open": np.asarray(self.verifyDF["open"]),
                        "high": np.asarray(self.verifyDF["high"]),
                        "low": np.asarray(self.verifyDF["low"]),
                        "volume": np.asarray(self.verifyDF["volume"])}
        self.SMA10 = SMA(input_arrays, timeperiod=10)
        self.SMA30 = SMA(input_arrays, timeperiod=30)
        # Due to https://github.com/mrjbq7/ta-lib/issues/40
        # I need to recreate the input_arrays.
        input_arrays["SMA10"] = self.SMA10
        input_arrays["SMA30"] = self.SMA30
        self.SMA30_of_SMA10 = SMA(input_arrays, timeperiod=30, price="SMA10")

        self.verifyDF["SMA10"] = pd.Series(self.SMA10, index=self.verifyDF.index)
        self.verifyDF["SMA30"] = pd.Series(self.SMA30, index=self.verifyDF.index)
        self.verifyDF["SMA30_SMA10"] = pd.Series(self.SMA30_of_SMA10, index=self.verifyDF.index)

    def handleData(self, symbol, newData, time):
        assert("SMA10" in newData)
        assert("SMA30" in newData)
        assert("SMA30_SMA10" in newData)

        logger.debug("newData is {}.".format(newData))
        logger.debug("verifyData is {}.".format(self.verifyDF.loc[time]))
        assert((self.verifyDF.loc[time].dropna() == newData.dropna()).all())

    def handleOrder(self, order):
        pass

    def teardown(self):
        pass

if __name__ == "__main__":
    pass
