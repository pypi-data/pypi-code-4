'''
Created on Apr 30, 2013

:author: Chen Huang <chinux@gmail.com>
'''

import datetime
from tradingmachine.DataFeed.DataFeedBase import IntervalPeriod


class PriceRecord(object):
    '''
    Price Record hold the high, low, end, open price for a given interval. It can be considered as a bar in the bar chart.
    '''

    def __init__(self, *args, **kw):
        '''
        :param args: containing open, high, low, end price
        :type args: list
        :param kw: containing datetime of this price record and its interval type
        '''
        self._open = args[0]
        self._high = args[1]
        self._low = args[2]
        self._end = args[3]
        self._vol = args[4]
        assert type(kw["datetime"]) == datetime.datetime
        self._datetime = kw["datetime"]
        assert type(kw["interval"]) == IntervalPeriod
        self._interval = kw["interval"]

    @property
    def open(self):
        return self._open

    @property
    def low(self):
        return self._low

    @property
    def high(self):
        return self._high

    @property
    def end(self):
        return self._end

    @property
    def volume(self):
        return self._vol

    @property
    def time(self):
        return self._datetime
