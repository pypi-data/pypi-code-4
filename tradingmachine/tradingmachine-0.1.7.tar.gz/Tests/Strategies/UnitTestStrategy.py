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


class UnitTestStrategy(Strategy):

    def __init__(self):
        super().__init__()

    def setup(self):
        self.registerSymbol("@test#")
        self.collectedData = pd.DataFrame(columns=['open', 'low', 'high', 'close', 'volume'])

    def handleData(self, symbol, newData, time):
        df = pd.DataFrame(
            data={
                "open": newData["open"],
                "low": newData["low"],
                "high": newData["high"],
                "close": newData["close"],
                "volume": newData["volume"].astype(int)},
            index=[time])

        if not self.collectedData.empty:
            self.collectedData = self.collectedData.append(df)
        else:
            self.collectedData = df.asfreq(pd.offsets.Minute())

        if time.hour == 9 and time.minute == 30:
            self.sendOrder(Order(symbol, OrderTypeMarketLong, 1, 0))

    def handleOrder(self, order):
        logger.info("An order has been fulfilled by market simualtor {}.".format(order))
        if order.costbase != 3.609:
            raise("The order should be filled with $3.609.")

    def teardown(self):
        # Doing verification for this unit test strategy.
        testingAsset = sharedAssets.retrieveAssetFromSymbol("@test#")
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 28, 10, 30, 0)
        verifyDF = testingAsset.load(startFrom, endsOn)

        if not DataFeed.DataFeedBase.isDataFrameSame(verifyDF, self.collectedData):
            raise("These two data frame should be same.")
        else:
            logger.info("Two data frame is same.")

        # Verify fulfilled orders.
        if self.marketSimulator:
            listOfOrders = self.marketSimulator.getFulfilledOrders
            if len(listOfOrders) > 0:
                assert(listOfOrders[0].orderID == 0)
                assert(listOfOrders[0].costbase == 3.609)
                assert(listOfOrders[0].orderQuantity == 1)
                assert(listOfOrders[0].fulfilled)
                assert(listOfOrders[0].symbol == "@test#")

        # Verify PnL calculation.
        if self.marketSimulator:
            pnl = self.marketSimulator.getPnL()
            logger.info("At end of this test, buy & hold strategy's PnL is %s.", pnl)
            if (abs(pnl - 27.5) < DataFeed.EPSILON):
                logger.info("Verified PnL at the end.")
            else:
                logger.info("PnL should be 27.5.")
                raise Exception("PnL should be 27.5.")

if __name__ == "__main__":
    logger.info("{:=^60}".format("Starting Test"))
    strategy = UnitTestStrategy()
    logger.info("{:-^60}".format("Starting Setup"))
    strategy.setup()
    startFrom = datetime(2012, 12, 28, 9, 16, 0)
    endsOn = datetime(2012, 12, 28, 10, 30, 0)
    logger.info("{:-^60}".format("Starting Run"))
    strategy.backTest(startFrom, endsOn)
    logger.info("{:-^60}".format("Starting TearDown"))
    strategy.teardown()
    logger.info("{:=^60}".format("End of Test"))
