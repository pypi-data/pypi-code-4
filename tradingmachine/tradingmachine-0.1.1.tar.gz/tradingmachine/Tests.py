'''
Created on Apr 28, 2013

:author: chen
'''
import unittest
import sharedLogger
from tradingmachine.DataFeed import *  # @UnusedWildImport
from tradingmachine.MarketSimulator import *
from tradingmachine.Asset import *
import os
import inspect
from tradingmachine.Utils import *  # @UnusedWildImport


def logFunctionName(func):
    def newFunc(*args, **kwargs):
        sharedLogger.logger.info("\n")
        sharedLogger.logger.info("===={:=<56}".format(" [{funcName}]: enter ".format(funcName=func.__name__)))
        result = func(*args, **kwargs)
        sharedLogger.logger.info("===={:=<56}".format(" [{funcName}]: exit ".format(funcName=func.__name__)))
        sharedLogger.logger.info("\n")
        return result
    return newFunc


def logAllTests(cls, decorator=logFunctionName, prefix="test_"):
    for name, meth in inspect.getmembers(cls, inspect.isfunction):
        if (name.startswith(prefix)):
            setattr(cls, name, decorator(meth))
    return cls


@logAllTests
class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_logging(self):
        sharedLogger.logger.info("Test - this is an info message.")
        sharedLogger.logger.info("Second Message.")

    def test_csvDataFeed_convert(self):
        rawDataFilePath = os.path.join(HISTORICALDATABASEPATH, RAWDATAFOLDER, "samples", "sample.txt")
        formattedDataFilePath = os.path.join(HISTORICALDATABASEPATH, FORMATTEDDATAFOLDER, "samples", "sample.csv")
        result = CSVDataFeed.convert(
            rawDataFilePath,
            formattedDataFilePath)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(formattedDataFilePath))
        import hashlib
        with open(formattedDataFilePath, 'r') as f:
            m = hashlib.md5()
            for line in f:
                m.update(line.encode('utf-8'))
            self.assertEqual(m.hexdigest(), "7f5f2f76cf5a794b535b30a67fc9add6")

    def test_symbols_description(self):
        from DataFeed import DataFeedBase
        desc = DataFeedBase.DescriptionLookupWithSymbol("@ES#")
        self.assertEqual(desc, "EminiFutureSP500")
        self.assertRaises(KeyError, DataFeedBase.DescriptionLookupWithSymbol, "Somehting unreal")

    def test_csvDataFeed_combine(self):
        import pandas as pd
        from tradingmachine.DataFeed import DataFeedBase

        samplesFolder = os.path.join(HISTORICALDATABASEPATH, RAWDATAFOLDER, "samples")
        dataframe1 = pd.read_csv(os.path.join(samplesFolder, "combine1.txt"), header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        dataframe1.index = dataframe1.pop("date_time")
        dataframe2 = pd.read_csv(os.path.join(samplesFolder, "combine2.txt"), header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        dataframe2.index = dataframe2.pop("date_time")
        dataframeCombined = DataFeedBase.combine(dataframe1, dataframe2)
        dataframeToCheckWith = pd.read_csv(os.path.join(samplesFolder, "combineResult.txt"), header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        dataframeToCheckWith.index = dataframeToCheckWith.pop("date_time")
        self.assertTrue(DataFeedBase.isDataFrameSame(dataframeCombined, dataframeToCheckWith))

    def test_databaseUpdate(self):
        import pandas as pd
        from tradingmachine.DataFeed.DataFeedBase import IntervalPeriod1Minute
        copperFilePath = os.path.join(HISTORICALDATABASEPATH, RAWDATAFOLDER, SAMPLESFOLDER, "update.txt")
        copperPrices = pd.read_csv(copperFilePath, header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        copperPrices.index = copperPrices.pop("date_time")
        DataFeedBase.UpdateDTNDataWithCurrentDatabase(copperPrices, "@test#", IntervalPeriod1Minute)

        testFilePath1 = os.path.join(HISTORICALDATABASEPATH, FORMATTEDDATAFOLDER, IntervalPeriod1Minute.__str__(), "@test#_1minute_UnitTests_2012.csv")
        testDataFrame1 = pd.read_csv(testFilePath1, header=None, parse_dates=[0], names=["date_time", "open", "high", "low", "close", "volume"])
        testDataFrame1.index = testDataFrame1.pop("date_time")
        testFilePath2 = os.path.join(HISTORICALDATABASEPATH, FORMATTEDDATAFOLDER, IntervalPeriod1Minute.__str__(), "@test#_1minute_UnitTests_2013.csv")
        testDataFrame2 = pd.read_csv(testFilePath2, header=None, parse_dates=[0], names=["date_time", "open", "high", "low", "close", "volume"])
        testDataFrame2.index = testDataFrame2.pop("date_time")

        verifyFilePath1 = os.path.join(HISTORICALDATABASEPATH, FORMATTEDDATAFOLDER, SAMPLESFOLDER, "verify1.txt")
        verifyDataFrame1 = pd.read_csv(verifyFilePath1, header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        verifyDataFrame1.index = verifyDataFrame1.pop("date_time")
        verifyFilePath2 = os.path.join(HISTORICALDATABASEPATH, FORMATTEDDATAFOLDER, SAMPLESFOLDER, "verify2.txt")
        verifyDataFrame2 = pd.read_csv(verifyFilePath2, header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        verifyDataFrame2.index = verifyDataFrame2.pop("date_time")

        self.assertTrue(DataFeedBase.isDataFrameSame(testDataFrame1, verifyDataFrame1))
        self.assertTrue(DataFeedBase.isDataFrameSame(testDataFrame2, verifyDataFrame2))

    def test_Assets(self):
        from datetime import datetime
        symbol = "@test#"
        self.assertEqual(sharedAssets.retrieveAssetFromSymbol(symbol).symbol, symbol)
        AssetUnderTest = sharedAssets.retrieveAssetFromSymbol(symbol)
        assert isinstance(AssetUnderTest, Asset)
        self.assertTrue(AssetUnderTest.earliestAvailableDate() == datetime(2012, 12, 27, 2, 16, 00))
        self.assertTrue(AssetUnderTest.latestAvailableDate() == datetime(2013, 1, 7, 1, 8, 0))

    def test_Assets_load_earlierThanAvailableData(self):
        from datetime import datetime
        symbol = "@test#"
        AssetUnderTest = sharedAssets.retrieveAssetFromSymbol(symbol)
        assert isinstance(AssetUnderTest, Asset)
        startFrom = datetime(2012, 12, 27, 2, 15, 0)
        endsOn = datetime(2013, 1, 1, 18, 10, 0)
        DataFrameUnderTest = AssetUnderTest.load(startFrom, endsOn)
        sharedLogger.logger.info("The time stamp of the first element of DataFrameUnderTest is {}.".format(DataFrameUnderTest.index[0]))
        self.assertTrue(DataFrameUnderTest.index[0] == AssetUnderTest.earliestAvailableDate())
        sharedLogger.logger.info("The time stamp of the last element of DataFrameUnderTest is {}.".format(DataFrameUnderTest.index[-1]))
        self.assertTrue(DataFrameUnderTest.index[-1] == endsOn)

    def test_Assets_load_laterThanAvailableData(self):
        from datetime import datetime
        symbol = "@test#"
        AssetUnderTest = sharedAssets.retrieveAssetFromSymbol(symbol)
        assert isinstance(AssetUnderTest, Asset)
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2014, 1, 1, 18, 10, 0)
        DataFrameUnderTest = AssetUnderTest.load(startFrom, endsOn)
        sharedLogger.logger.info("The time stamp of the first element of DataFrameUnderTest is {}.".format(DataFrameUnderTest.index[0]))
        self.assertTrue(DataFrameUnderTest.index[0] == startFrom)
        sharedLogger.logger.info("The time stamp of the last element of DataFrameUnderTest is {}.".format(DataFrameUnderTest.index[-1]))
        self.assertTrue(DataFrameUnderTest.index[-1] == AssetUnderTest.latestAvailableDate())

    def test_Assets_load_fromAvailableData(self):
        from datetime import datetime
        symbol = "@test#"
        AssetUnderTest = sharedAssets.retrieveAssetFromSymbol(symbol)
        assert isinstance(AssetUnderTest, Asset)
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 31, 17, 10, 0)
        """
        #  There is no data at 2012-12-31 17:10:00. The data available is:
        2012-12-31 17:07:00,3.6500,3.6515,3.6500,3.6515,14
        2012-12-31 17:11:00,3.6505,3.6505,3.6505,3.6505,1
        So the endsOn should be at 2012-12-31 17:07:00
        """
        DataFrameUnderTest = AssetUnderTest.load(startFrom, endsOn)
        sharedLogger.logger.info("The time stamp of the first element of DataFrameUnderTest is {}.".format(DataFrameUnderTest.index[0]))
        self.assertTrue(DataFrameUnderTest.index[0] == startFrom)
        sharedLogger.logger.info("The time stamp of the last element of DataFrameUnderTest is {}.".format(DataFrameUnderTest.index[-1]))
        self.assertTrue(DataFrameUnderTest.index[-1] == datetime(2012, 12, 31, 17, 7, 0))

    def test_MarketSimulator_prepareSimulatorDataFeed_SingleSymbol(self):
        from datetime import datetime
        symbol = "@test#"
        market = MarketSimulator(datetime.now())
        market.addObserver(symbol)
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 31, 17, 10, 0)
        DataPanelUnderTest = market.prepareSimulatorDataFeed(startFrom, endsOn)
        self.assertTrue(DataPanelUnderTest.major_axis[0] == startFrom)
        self.assertTrue(DataPanelUnderTest.major_axis[-1] == datetime(2012, 12, 31, 17, 7, 0))

    def test_MarketSimulator_prepareSimulatorDataFeed_MultipleSymbols(self):
        from datetime import datetime
        import pandas as pd
        symbols = ["@test#", "@SanDiego#"]
        market = MarketSimulator(datetime.now())
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 31, 17, 10, 0)
        DataPanelUnderTest = market.prepareSimulatorDataFeed(startFrom, endsOn, symbols=symbols)
        self.assertTrue(DataPanelUnderTest.major_axis[0] == startFrom)
        self.assertTrue(DataPanelUnderTest.major_axis[-1] == datetime(2012, 12, 31, 17, 7, 0))
        multiindexRecord = DataPanelUnderTest.major_xs(startFrom)
        sharedLogger.logger.info("MultiIndex Record at 2012-12-28 9:16:00 is \n{}.".format(multiindexRecord))
        self.assertTrue(isinstance(multiindexRecord, pd.DataFrame))
        self.assertTrue((multiindexRecord["@test#"]["open"] == 3.596))
        self.assertTrue((multiindexRecord["@SanDiego#"]["close"] == 3.597))

    def test_Strategies_UnitTestStrategy(self):
        from tradingmachine.Strategies.UnitTestStrategy import UnitTestStrategy
        strategy = UnitTestStrategy()
        strategy.setup()
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 28, 10, 30, 0)
        strategy.backTest(startFrom, endsOn)
        strategy.teardown()

    def test_Strategies_UnitTestStrategyIndicator(self):
        from tradingmachine.Strategies.UnitTestStrategyIndicator import UnitTestStrategyIndicator
        strategy = UnitTestStrategyIndicator()
        strategy.setup()
        startFrom = datetime(2012, 12, 28, 9, 16, 0)
        endsOn = datetime(2012, 12, 28, 10, 30, 0)
        strategy.backTest(startFrom, endsOn)
        strategy.teardown()

#    def test_rawData_conversion(self):
#        Assets.ConvertAllRawFileIntoFormattedDataFile()

if __name__ == "__main__":
    unittest.main()
