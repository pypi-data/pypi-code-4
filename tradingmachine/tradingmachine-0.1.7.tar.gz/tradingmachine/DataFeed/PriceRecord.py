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
