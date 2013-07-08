'''
Copyright 2013-2013 Chen Huang.
All rights reserved. FreeBSD License.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the
     distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from tradingmachine.Strategy.Strategy import *
from tradingmachine.Asset import *
from tradingmachine.sharedLogger import logger
import pandas as pd
import numpy as np
from tradingmachine.Indicators.Indicator import TAIndicator

from talib.abstract import BBANDS
import talib


class BollingerBands(Strategy):

    def __init__(self):
        super().__init__()

    def setup(self):
        self.symbol = "@ES#"

        # Register S&P 500 Emini as one of our monitoring ticker symbol.
        self.registerSymbol(self.symbol)

        # Logging a message.
        logger.info("Registering Transforms.")

        # Register a 5 data points Exponential Moving average on the close price of S&P 500 Emini.
        # The newly calculated Bollinger Bands are assigned with names of "UpBand", "MidBand", "LowBand".
        self.registerTransform(
            func=TAIndicator("BBANDS"),
            symbol=self.symbol,
            desiredname=["UpBand", "MidBand", "LowBand"],
            tag="close",
            timeperiod=5,
            nbdevup=2,
            nbdevdn=2,
            matype=talib.MA_Type.EMA)

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
        self.bands = BBANDS(input_arrays, timeperiod=5, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.EMA, price="close")
        self.verifyDF["UpBand"] = pd.Series(self.bands[0], index=self.verifyDF.index)
        self.verifyDF["MidBand"] = pd.Series(self.bands[1], index=self.verifyDF.index)
        self.verifyDF["LowBand"] = pd.Series(self.bands[2], index=self.verifyDF.index)

        self.verifyDF = self.verifyDF.sort(axis=1, ascending=True)  # Needed for comparision

    def handleData(self, symbol, newData, time):
        assert("UpBand" in newData)
        assert("MidBand" in newData)
        assert("LowBand" in newData)

        update = newData.copy()
        update = update.sort_index(True)    # needed for comparison.
        logger.debug("newData is {}.".format(update))
        logger.debug("verifyData is {}.".format(self.verifyDF.loc[time]))
        assert((self.verifyDF.loc[time].dropna() == update.dropna()).all())

    def handleOrder(self, order):
        pass

    def teardown(self):
        pass

if __name__ == "__main__":
    logger.info("{:=^60}".format("Starting Test"))
    strategy = BollingerBands()
    logger.info("{:-^60}".format("Starting Setup"))
    strategy.setup()
    startFrom = datetime(2012, 12, 28, 9, 16, 0)
    endsOn = datetime(2012, 12, 28, 10, 30, 0)
    logger.info("{:-^60}".format("Starting Run"))
    strategy.backTest(startFrom, endsOn)
    logger.info("{:-^60}".format("Starting TearDown"))
    strategy.teardown()
    logger.info("{:=^60}".format("End of Test"))
