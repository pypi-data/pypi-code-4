'''
CSVDataFeed

Created on Apr 30, 2013

:author: Chen Huang <chinux@gmail.com>
'''

from tradingmachine.DataFeed.DataFeedBase import *     # @UnusedWildImport
from tradingmachine.sharedLogger import logger
import pandas as pd
import datetime
import os
from tradingmachine import Error
from tradingmachine.Utils import *


class CSVDataFeed(DataFeedBase):

    '''
    CSVDataFeed provide price data from a local csv file.
    '''

    def __init__(self, symbol, start, end=None, interval=IntervalPeriod1Minute):
        '''
        CSV Data Feed must init with at least one argument of "file" = Path of the CSV file.
        :param filePath: filePath
        :type filePath: str
        '''
        super().__init__()
        self._symbol = symbol
        self._datafeedStart = start
        self._datafeedEnd = end
        self._interval = interval
        self._data = None

    def __eq__(self, other):
        pass

    def __str__(self):
        pass

    @staticmethod
    def convert(rawDataFile, formattedDataFile):
        """
        Convert a CSV file into properly formatted CSV file. Mainly to convert the time into ISO standard time to increase loading speed.
        :param rawDataFile: The csv file containing raw data
        :type rawDataFile: string represent the full path of the file containing raw CSV file
        :param formattedDataFile: The csv file containing the formatted data
        :type formattedDataFile: string represent the full path of the formattedDataFile, must have write permission.
        :rtype: bool
        """
        if not os.path.exists(rawDataFile):
            raise Error.FileNotExistsError("File {} does not exist.".format(rawDataFile))

        if not os.path.exists(os.path.split(formattedDataFile)[0]):
            try:
                logger.info("Creating path to %s.", formattedDataFile)
                os.makedirs(os.path.split(formattedDataFile)[0])
            except:
                logger.error("Failed to create path %s.", os.path.split(formattedDataFile)[0])
                return False

        logger.info("Loading raw data from %s.", rawDataFile)
        dataframe = pd.read_csv(rawDataFile, header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
        logger.info("Loaded: \n%s.", dataframe)
        dataframe.index = dataframe.pop('date_time')    # Use DateTime object as index.
        logger.info("Saving into file %s.", formattedDataFile)
        dataframe.to_csv(formattedDataFile, header=None)
        return True

    @staticmethod
    def merge(anotherFeed):
        """
        Merge two data feed using their date time index. After merge, create a new DataFeed that has both data but using same date time index.
        """
        pass

    def validate(self):
        """
        Validate data file on daily base.
        """
        pass

    def removeBrokenDataRecords(self):
        """
        Remove broken data records that are not complete.
        """
        pass

    def save(self):
        """
        Save the modified database to the local file representing this feed.
        """
        self._data = self._data.to_csv(self._file, header=None)

    def load(self):
        """
        Load the database from the local csv file.
        """
        self._data = pd.read_csv(self._file, header=None, parse_dates=[0], names=["datetime", "open", "high", "low", "close", "volume"])

    def copyDataframeDuringTradingHour(self):
        """
        Return a data frame for the normal trading hour. 9 AM to 5 PM. Futures and Stocks has different trading hour. This should include the longest time span. If NaN is used if no data available after hours.
        """
        dataframeDuringTradingHour = self._data.ix(self._data.index.indexer_between_time(datetime.time(9), datetime.time(5)))
        return dataframeDuringTradingHour.copy(True)

    def copydataframe(self):
        """
        Deep copy the data frame for manupliation.
        """
        another_copy = self._data.copy(True)
        return another_copy

    def countDays(self):
        """
        Returns the number of trading days. Excluding holidays or non-trading days.
        """
        dayframe = self._data.asfreq(pd.offsets.BDay())
        return dayframe["close"].count()

    def countRecords(self):
        """
        Returns the number of records in memory.
        """
        return self._data["close"].count()

    def PriceDataFromRange(self, asset, start, end, interval=IntervalPeriod1Minute, tradingPeriod=TradingPeriodDay):
        pass
