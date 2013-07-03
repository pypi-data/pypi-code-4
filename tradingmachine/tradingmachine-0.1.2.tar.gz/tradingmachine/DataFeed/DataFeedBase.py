'''
DataBaseFeedBase

Created on Apr 30, 2013

:author: Chen Huang
'''

from abc import ABCMeta, abstractmethod
from tradingmachine import Utils
from tradingmachine.Utils import accepts, returns
import builtins
from tradingmachine import Error
from tradingmachine.sharedLogger import logger
import pandas as pd
import os


EPSILON = 1e-10     # define the largest difference to consider two float different.


class IntervalPeriod(Utils.Enum):
    valueMap = {}

IntervalPeriodTick = IntervalPeriod(0, "Tick")
IntervalPeriod1Minute = IntervalPeriod(1, "1minute")
IntervalPeriod5Minutes = IntervalPeriod(5, "5minutes")
IntervalPeriod10Minutes = IntervalPeriod(10, "10minutes")
IntervalPeriod30Minutes = IntervalPeriod(30, "30minutes")
IntervalPeriod60Minutes = IntervalPeriod(60, "1hour")


class TradingPeriod(Utils.Enum):
    valueMap = {}

TradingPeriodDay = TradingPeriod(0, "Day Trading")
TradingPeriodDayAndNight = TradingPeriod(1, "Day and Night Trading")

"""
Database file name convention:
Symbol_Interval_ShortDescription.csv
ShortDescription is TypeName
Type: EminiFuture, Future, Stock, Index
Name: Copper(Future), Apple(Stock), Microsoft(Stock), SP500(Index or Future)
For example:
+HG#_1minute_EminiFutureCopper.csv means Emini Copper future 1 minute database.
"""


class DataFeedBase(object, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *args, **kw):
        pass

    @abstractmethod
    def PriceDataFromRange(self, asset, start, end, interval=IntervalPeriod1Minute, tradingPeriod=TradingPeriodDay):
        '''
        :param  asset: Symbol of the trading asset. i.e. "@ES#":E-mini S&P 500 continuous contract, "AAPL":Apple Computer, Inc.
                start: Python date time object indicating star time of the price data.
                end: Python date time object indicating end time of the price data
                interval: Bar chart interval. Type of (Interval Period)
                tradingPeriod: Day-Trading or GlobalExchange: Day & Night
        :return: Return an array of asset price record of defined interval from "start" to "end".
        '''
        pass

    @staticmethod
    @accepts(builtins.str)
    @returns(pd.DataFrame)
    def Load1minuteCSVDataFileWithTwoDateTimeColumns(filePath):
        """
        Using this function to load a csv file in which the first two colums are used to specify the date time. And covert this csv data to pandas dataframe with datetime index.
        :discussion: This function is manily used as a wrapper to clean up DTN csv data.
        """
        assert(os.path.exists(filePath))
        csvdata = pd.read_csv(filePath, header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        csvdata.index = csvdata.pop("date_time")
        return csvdata

    @staticmethod
    @accepts(builtins.str)
    @returns(pd.DataFrame)
    def Load1minuteCSVDataFileWithOneDateTimeColumns(filePath):
        """
        Using this function to load a csv file in which the first two colums are used to specify the date time. And covert this csv data to pandas dataframe with datetime index.
        :discussion: This function is manily used as a wrapper to clean up DTN csv data.
        """
        assert(os.path.exists(filePath))
        csvdata = pd.read_csv(filePath, header=None, parse_dates=[0], names=["date_time", "open", "high", "low", "close", "volume"], index_col="date_time")
        return csvdata

    @staticmethod
    @accepts(pd.DataFrame)
    @returns(builtins.set)
    def GetYearsInvolved(dataframe):
        """
        Take a pandas dataframe and figure out how many years involved. Return a unique set of years in which there are data in this dataframe.
        """
        return set(dataframe.index[:].year)

    @staticmethod
    @accepts(pd.DataFrame, builtins.str, IntervalPeriod)
    def UpdateDTNDataWithCurrentDatabase(dataframe, symbol, period):
        """
        This function will update current data base in HistoricalData/FormattedData/1minute/ with dataframe object.
        """
        import decimal
        years = DataFeedBase.GetYearsInvolved(dataframe)
        if (period == IntervalPeriod1Minute):
            dataframe.asfreq(pd.tseries.offsets.Minute())

            for year in years:
                # load 1 minute symbol file
                fileName = "_".join((symbol, period.__str__(), DataFeedBase.DescriptionLookupWithSymbol(symbol), str(year))) + ".csv"
                filePath = os.path.join(Utils.HISTORICALDATABASEPATH, Utils.FORMATTEDDATAFOLDER, period.__str__(), fileName)
                dataframeThisYear = dataframe["-".join((str(year), "1", "1")):"-".join((str(year), "12", "31"))]
                try:
                    originalDataframe = DataFeedBase.Load1minuteCSVDataFileWithOneDateTimeColumns(filePath)
                    dataframeThisYear = DataFeedBase.combine(originalDataframe, dataframeThisYear)
                except:
                    logger.info("Could not find 1 minute dataframe of {} for {}.".format(symbol, year))
                ticksize = DataFeedBase.TickSizeForSymbol(symbol)
                decimalPoints = decimal.Decimal(ticksize).as_tuple().exponent
                if decimalPoints < 0:
                    decimalPoints = 0 - decimalPoints
                else:
                    decimalPoints = 0
                dataframeThisYear.to_csv(filePath, header=False, float_format='%.{}f'.format(decimalPoints))

        elif (period == IntervalPeriodTick):
            pass
        else:
            raise Error.UnknownIntervalPeriod("Dataframe frequency is unknown.")

    @staticmethod
    @accepts(builtins.str)
    def DescriptionLookupWithSymbol(symbol):
        """
        Look up the current Symbol and description mapping and return the proper description for the dataframe.
        """
        import csv
        with open(os.path.join(Utils.HISTORICALDATABASEPATH, "symbols_description.csv"), 'r') as f:
            reader = csv.reader(f)
            lookupTable = dict(x[0:2] for x in reader)  # read first two and put them into a dictionary.
            desc = lookupTable[symbol]
            logger.info("Description for symbol {} is {}.".format(symbol, desc))
        return desc

    @staticmethod
    @accepts(builtins.str)
    def TickSizeForSymbol(symbol):
        import csv
        with open(os.path.join(Utils.HISTORICALDATABASEPATH, "symbols_description.csv"), 'r') as f:
            reader = csv.reader(f)
            lookupTable = dict((x[0], x[2]) for x in reader)     # read first two and put them into a dictionary.
            ticksize = lookupTable[symbol]
            logger.info("ticksize for symbol {} is {}.".format(symbol, ticksize))
        return ticksize

    @staticmethod
    @accepts(pd.DataFrame, pd.DataFrame)
    @returns(pd.DataFrame)
    def combine(source, target):
        """
        Combine source dataframe with target data frame. It will use source dataframe as base while update NAN with target values.
        :rtype: pandas.DataFrame
        """
        concatenated = pd.concat([source, target])
        concatenated['index'] = concatenated.index
        concatenated.drop_duplicates(cols='index', take_last=False, inplace=True)
        del concatenated['index']
        concatenated = concatenated.sort_index()
        return concatenated

    @staticmethod
    @accepts(pd.DataFrame, pd.DataFrame)
    @returns(builtins.bool)
    def isDataFrameSame(first, second):
        """
        Compare two data frame and test to see if they are the same.
        """
        try:
            equalFrame = first - second
        except:
            return False
        # iterate through the columes and make sure std = 0 and mean = 1
        for i in equalFrame.__iter__():
            tempTimeSeries = getattr(equalFrame, i)
            if (tempTimeSeries.std() <= EPSILON and tempTimeSeries.mean() <= EPSILON):
                continue
            else:
                return False
        return True
