## Python Compete API - Python wrapper around the compete.com api.
## Copyright (C) 2013 Max Retter
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import urllib2 as urllib
from datetime import datetime

## request formats
REQUEST_FORMAT_JSON = 'json'
REQUEST_FORMAT_PNG = 'png'
REQUEST_FORMAT_JPG = 'jpg'
REQUEST_FORMAT_GIF = 'gif'

## response codes
RESPONSE_STATUS_OK = 'OK'
RESPONSE_STATUS_NO_DATA = 'NO_DATA'
RESPONSE_STATUS_INVALID = 'INVALID'
RESPONSE_STATUS_ACCESS_DENIED = 'ACCESS_DENIED'
RESPONSE_STATUS_UNKNOWN_ERROR = 'UNKNOWN_ERROR'
RESPONSE_STATUS_UNAVAILABLE = 'UNAVAILABLE'


class CompeteAPI(object):
    """Main API object."""

    def __init__(self, api_key):
        self.api_key = api_key

    def build_request(self, site, *metrics, **extra_args):
        request = CompeteRequest()
        request.api_key = self.api_key
        request.site = site
        request.metrics = metrics
        request.format = extra_args.get('format', REQUEST_FORMAT_JSON)

        request.start_date = extra_args.get('start_date')
        request.end_date = extra_args.get('end_date')
        request.latest = extra_args.get('latest')

        return request

    def execute_request(self, site, *metrics, **extra_args):
        request = self.build_request(site, *metrics, **extra_args)
        return request.execute()


class CompeteRequest(object):
    """A request to be sent off to the api."""

    API_STRING = 'http://apps.compete.com/sites/%(site)s/trended/search/?apikey=%(api_key)s&metrics=%(metric_list)s&format=%(format)s%(date)s'
    DATE_QUERY_START_END = '&start_date=%s&end_date=%s'
    DATE_QUERY_LATEST = '&latest=%s'

    def __init__(self):
        self.api_key = ''
        self.site = 'facebook.com'
        self.metrics = ('uv',)
        self.format = REQUEST_FORMAT_JSON

        self.start_date = None
        self.end_date = None
        self.latest = None

    def execute(self):
        query = self.build_query()

        try:
            data = urllib.urlopen(query).read()
        except urllib.URLError, e:
            data = e.read()

        return CompeteResponse.get_responder(
            self.format,
            data
        )

    def build_query(self):
        return self.API_STRING % dict(
            site=self.site,
            api_key=self.api_key,
            metric_list=','.join(self.metrics),
            format=self.format,
            date=self.build_date()
        )

    def build_date(self):
        if self.start_date and self.end_date:
            return self.DATE_QUERY_START_END % (self.start_date, self.end_date, )
        elif self.latest:
            return self.DATE_QUERY_LATEST % self.latest

        return ''


class CompeteGraphResponse(object):
    """A graph (image) response from the api."""

    def __init__(self, raw_data):
        self.data = raw_data

    def export_image(self, file_path):
        with file(file_path, 'wb') as image_file:
            image_file.write(self.data)


class CompeteJSONResponse(object):
    """A json response from the api."""

    def __init__(self, raw_json):
        self._json = None
        self._points = None

        self.load_data(raw_json)

    def __len__(self):
        return len(self._points)

    def __iter__(self):
        return iter(self._points)

    ## data

    def load_data(self, raw_json):
        self._json = json.loads(raw_json)

        self._points = CompeteDataSet()
        self._parse_data(self._json)

    def _parse_data(self, json_data):
        if self.check_status('OK'):

            if 'data' in json_data and 'trends' in json_data['data']:
                for metric, data in json_data['data']['trends'].iteritems():
                    for data_point in data:
                        self._points.add_point(metric, data_point)

        self._points.finalize()

    ## status
    def status(self):
        return self._json.get('status', '')

    def check_status(self, status):
        return self.status() == status

    def status_message(self):
        return self._json.get('status_message', '')

    def low_sample(self):
        return self._json['data'].get('trends_low_sample', False)

    def cost(self):
        return self._json['data'].get('query_cost', 0)

    def frequency(self):
        return self._json['data'].get('trends_frequency', '')


class CompeteResponse(object):
    """A helper class for choosing the correct response type."""

    RESPONDERS = {
        REQUEST_FORMAT_JSON: CompeteJSONResponse,
        REQUEST_FORMAT_PNG: CompeteGraphResponse,
        REQUEST_FORMAT_JPG: CompeteGraphResponse,
        REQUEST_FORMAT_GIF: CompeteGraphResponse,
    }

    @staticmethod
    def get_responder(format, data):
        return CompeteResponse.RESPONDERS[format](data)


class CompeteDataPoint(object):
    """Single json data point."""

    DATE_FORMAT = '%Y%m'

    __slots__ = ['date', '_data', ]

    def __init__(self, date):
        self.date = datetime.strptime(date, self.DATE_FORMAT)
        self._data = {}

    def __contains__(self, key):
        return key in self._data

    def __unicode__(self):
        return unicode(self)

    def __str__(self):
        return 'date: %s\n%s' % (
            self.date,
            '\n'.join(['  %s: %s' % trend for trend in self._data.iteritems()])
        )

    def add_trend(self, metric, value):
        self._data[metric] = value

    def value(self, metric):
        return self._data[metric]


class CompeteDataSet(object):
    """A set of CompeteDataPoints."""

    def __init__(self):
        self._dates = {}
        self._points = []
        self._finalized = False

    def __len__(self):
        return len(self._dates)

    def __iter__(self):
        if not self._finalized:
            self.finalize()
        else:
            return iter(self._points)

    def finalize(self):
        self._points = sorted(self._dates.values(), key=lambda point: point.date)
        self._finalized = True

    def add_point(self, metric, raw_data_point):
        raw_date = raw_data_point['date']
        value = raw_data_point['value']

        point = self._dates.get(raw_date, CompeteDataPoint(raw_date))
        point.add_trend(metric, value)

        if raw_date not in self._dates:
            self._dates[raw_date] = point
