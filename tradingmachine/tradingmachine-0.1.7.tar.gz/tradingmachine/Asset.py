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


from tradingmachine.sharedLogger import logger
import os
import pandas as pd
from tradingmachine import Utils
import re
from tradingmachine import DataFeed
import collections
import csv
from datetime import datetime


class Asset():

    AssetAttributes = ["_symbol", "_description", "_ticksize", "_unitprice"]

    def __init__(self, symbol, description):
        self._symbol = symbol
        self._description = description
        self._filesMap = {
            DataFeed.IntervalPeriod1Minute: {},
            DataFeed.IntervalPeriodTick: {}}

        self.updateAttributes()

    @property
    def symbol(self):
        return self._symbol

    @property
    def ticksize(self):
        return self._ticksize

    @property
    def unitprice(self):
        return self._unitprice

    @property
    def description(self):
        return self._description

    def updateFileMap(self, period, file, interval):
        """
        :param  period: Used to repsent the time span of the data base file. For Tick, it's quarter of a year and for minutes, it's a year.
        :type   period: str
        """
        self._filesMap[interval][period] = file

    def __str__(self):
        return "Symbol: {0} - {1}".format(self.symbol, self.description())

    def __eq__(self, other):
        if (hasattr(other, "symbol") and isinstance(getattr(other, "symbol"), collections.Callable)):
            return self._symbol == other.symbol
        else:
            return False

    def earliestAvailableDate(self, interval=DataFeed.IntervalPeriod1Minute):
        if (interval == DataFeed.IntervalPeriod1Minute):
            earliestYear = min(self._filesMap[interval].keys())
            earliestFile = "{}_{}_{}_{}.csv".format(self.symbol, interval.__str__(), self._description, earliestYear)
            with open(
                os.path.join(
                    Utils.HISTORICALDATABASEPATH,
                    Utils.FORMATTEDDATAFOLDER,
                    interval.__str__(),
                    earliestFile), "r") as file:
                timestamp = csv.reader(file).__next__()[0]
                return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        else:
            # TODO: implement the tick side as well.
            pass

    def latestAvailableDate(self, interval=DataFeed.IntervalPeriod1Minute):
        if (interval == DataFeed.IntervalPeriod1Minute):
            latestYear = max(self._filesMap[interval].keys())
            latestFile = "{}_{}_{}_{}.csv".format(self.symbol, interval.__str__(), self._description, latestYear)
            with open(
                os.path.join(
                    Utils.HISTORICALDATABASEPATH,
                    Utils.FORMATTEDDATAFOLDER,
                    interval.__str__(),
                    latestFile), "r") as file:
                timestamp = file.readlines()[-1].split(",")[0]
                return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        else:
            # TODO: implement the tick side as well.
            pass

    def _getFilePathForYear(self, year):
        filename = "{}_{}_{}_{}.csv".format(self.symbol, DataFeed.IntervalPeriod1Minute.__str__(), self._description, year)
        filepath = os.path.join(
            Utils.HISTORICALDATABASEPATH,
            Utils.FORMATTEDDATAFOLDER,
            DataFeed.IntervalPeriod1Minute.__str__(),
            filename)
        return filepath

    def load(self, startFrom, endsOn, interval=DataFeed.IntervalPeriod1Minute):
        """
        Return a DataFeed object with time span equal to [startFrom, endsOn]
        TODO: implement the tick version of APIs. Refer to https://gitlab.com/chinux23/tradingmachine/issues/3191
        """
        earliestTime = self.earliestAvailableDate()
        latestTime = self.latestAvailableDate()
        if earliestTime > startFrom:
            logger.warning("Revise startFrom time to earliest time of available data.")
            startFrom = earliestTime
        if latestTime < endsOn:
            logger.warning("Revise endsOn time to latest time of available data.")
            endsOn = latestTime

        years = range(startFrom.year, endsOn.year+1, 1)
        if years:
            datafeedOfYears = pd.DataFrame()
            for year in years:
                fileToLoad = self._getFilePathForYear(year)
                dataframe = DataFeed.DataFeedBase.Load1minuteCSVDataFileWithOneDateTimeColumns(fileToLoad)
                datafeedOfYears = pd.concat([datafeedOfYears, dataframe])
            datafeedOfYears.asfreq(pd.offsets.Minute())     # TODO: verify this - https://github.com/pydata/pandas/issues/3932
            # Filter on given time span.
            startFrom.replace(second=0)
            endsOn.replace(second=0)
            return datafeedOfYears.loc[startFrom:endsOn]
        else:
            logger.info("There aren't any {} data available from {} to {}.".format(self.symbol, startFrom, endsOn))

    def updateAttributes(self):
        import csv
        with open(os.path.join(Utils.HISTORICALDATABASEPATH, "symbols_description.csv"), 'r') as f:
            reader = csv.reader(f)
            linesToProcess = filter(lambda line: line[0] == self.symbol, reader)
            for line in linesToProcess:
                logger.info("Update {} with info: {}.".format(self.symbol, line))
                setattr(self, self.AssetAttributes[2], float(line[2].strip()))
                setattr(self, self.AssetAttributes[3], float(line[3].strip()))


class Assets(object):

    def __init__(self):
        logger.info("Initializing Global Assets.")
        # Initialize over available data feed files
        self._databaseLocation = os.path.join(
            Utils.HISTORICALDATABASEPATH,
            Utils.FORMATTEDDATAFOLDER,
            str(DataFeed.IntervalPeriod1Minute))
        logger.debug("GlobalAssets database location is {0}.".format(self._databaseLocation))

        self._assets = {}

        if os.path.isdir(self._databaseLocation):
            for fileName in os.listdir(self._databaseLocation):
                logger.debug("Evaluating file: {}.".format(fileName))
                if (Assets.validateFileName(fileName)):
                    symbol, interval, description, year = os.path.splitext(fileName)[0].split("_")
                    if ("minute" in interval):
                        interval = DataFeed.IntervalPeriod.valueMap[int(interval.replace("minute", ""))]
                    else:
                        interval = DataFeed.IntervalPeriodTick

                    asset = self.retrieveAssetFromSymbol(symbol)
                    if not asset:
                        logger.info("Creating [{}] in global assets.".format(symbol))
                        asset = Asset(symbol, description)
                        self._assets.update({symbol: asset})
                    else:
                        logger.debug("Updating [{}] in global assets with file {}.".format(symbol, fileName))
                    asset.updateFileMap(year, fileName, interval)
        else:
            logger.error("GlobalAssets database location is expected to be a folder.")

    def databaseLocation(self):
        self._databaseLocation = os.path.join(Utils.HISTORICALDATABASEPATH, Utils.FORMATTEDDATAFOLDER)

    def retrieveAssetFromSymbol(self, symbol):
        if symbol in self._assets:
            asset = self._assets[symbol]
            return asset
        else:
            logger.debug("[{}] is not in Global assets.".format(symbol))

    @staticmethod
    def ConvertAllRawFileIntoFormattedDataFile():
        for fileName in os.listdir(os.path.join(Utils.HISTORICALDATABASEPATH, Utils.RAWDATAFOLDER, str(DataFeed.IntervalPeriod1Minute))):
            if Assets.validateFileName(fileName):
                fileReadPath = os.path.join(Utils.HISTORICALDATABASEPATH, Utils.RAWDATAFOLDER, str(DataFeed.IntervalPeriod1Minute), fileName)
                fileWriteFolder = os.path.join(Utils.HISTORICALDATABASEPATH, Utils.FORMATTEDDATAFOLDER, str(DataFeed.IntervalPeriod1Minute))
                if not os.path.exists(fileWriteFolder):
                    try:
                        os.makedirs(fileWriteFolder)
                    except:
                        logger.warn("Failed to create path = %s.", fileWriteFolder)
                        return  # Bail.
                symbol = fileName.split("_")[0]
                rawDataFrame = pd.read_csv(fileReadPath, header=None, parse_dates=[[0, 1]], names=["date", "time", "open", "high", "low", "close", "volume"])
                rawDataFrame.index = rawDataFrame.pop("date_time")
                DataFeed.UpdateDTNDataWithCurrentDatabase(rawDataFrame, symbol, DataFeed.IntervalPeriod1Minute)
            else:
                logger.info("Skipping file %s.", fileName)

    @staticmethod
    def validateFileName(fileName):
        csvFileRule = re.compile(".+\.(txt|csv)")   # Match any character before dot, and after dot, match either to txt or csv
        if (csvFileRule.match(fileName)):
            return True
        else:
            logger.debug("{0} is not a valid csv data feed.".format(fileName))
            return False

    def __getitem__(self, symbol):
        return self.retrieveAssetFromSymbol(symbol)

# This ensures that we have only one globalAssets
sharedAssets = Assets()
