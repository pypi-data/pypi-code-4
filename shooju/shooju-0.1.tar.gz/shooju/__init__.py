import itertools
import tempfile
from collections import defaultdict
from functools import partial
import json
from datetime import date
import datetime
import calendar
from operator import truth

import requests

try:
    import pandas
    PANDAS_SUPPORT = True
except ImportError:
    PANDAS_SUPPORT = False


def sid(*args):
    """
    Constructs a series id using the list of arguments

    :param args: parts of the series id
    :return: formatted series id
    :rtype: str
    """
    return "\\".join(args)


class Point(object):
    """
    Point represents a value in the remote API
    """

    def __init__(self, dt, value):
        """
        Representation of a point for a time series

        :param int datetime.datetime datetime.date dt: date for the point
        :param float value: value of the point
        """
        self.date = dt
        self.value = value

    @property
    def value(self):
        """
        Value of the point

        :return: value of the point
        :rtype: float
        """
        return self._val

    @value.setter
    def value(self, value):
        """
        Sets the value of the point, only accepts float

        :param float value: value of the point
        """
        value = float(value) # testing if it's a float
        self._val = value


    @property
    def date(self):
        """
        Date of the point

        :return: date
        :rtype: datetime.date
        """
        return datetime.date(self._dt.year, self._dt.month, self._dt.day)

    @date.setter
    def date(self, value):
        """
        Sets the date of the point

        :param int float datetime.datetime datetime.date value:
        :raise ValueError:
        """
        if isinstance(value, int):
            self._dt = datetime.datetime.utcfromtimestamp(value)
        elif isinstance(value, datetime.datetime):
            self._dt = value
        elif isinstance(value, date):
            self._dt = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0)
        elif isinstance(value, float):
            self._dt = datetime.datetime.utcfromtimestamp(int(value))
        else:
            raise ValueError("You can pass unixtime(int) or datetime.date objects only")


    @property
    def datetime(self):
        """
        Date of the point as datetime.datetime

        :return: date of the point
        :rtype: datetime.datetime
        """
        return self._dt

    def to_dict(self):
        """
        Returns back a dictionary of the point
        which will be ready to be serialized in the
        next steps ...
        """
        return {
            datetime_to_unixtime(self._dt): self._val
        }

    def __repr__(self):
        return "Point(%s, %s)" % (self._dt, self.value)


def unixtime_to_datetime(unixtime):
    """
    Converts unix time to utc datetime

    :param int float unixtime: unix time
    :return:
    """
    return datetime.datetime.utcfromtimestamp(unixtime)


def date_to_unixtime(dt):
    """
    Date to utc unix time

    :param datetime.date dt: date
    :return: the date as a unix time string
    :rtype: str
    """
    dd = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0)
    return datetime_to_unixtime(dd)


def datetime_to_unixtime(dt):
    """
    Datetime to utc unixtime

    :param datetime.datetime dt: date
    :return : date as a unix time string
    :rtype : str
    """
    return str(int(calendar.timegm(dt.utctimetuple())))


def to_unixtime(dt):
    """
    Date to utc unix time

    :param datetime.date datetime.datetime dt: date to be converted
    :return: date as a unix time string
    :rtype: str
    """
    if isinstance(dt, datetime.datetime):
        return datetime_to_unixtime(dt)
    elif isinstance(dt, date):
        return date_to_unixtime(dt)
    else:
        raise ValueError("You can pass unixtime(int) or datetime.date objects only")


class Field(object):
    """
    Field represents the remote field of the API
    """

    def __init__(self, field_dict=None):
        """
        Accepts a dictionary of key values
        :param dict field_dict: dict with fields
        """
        if field_dict:
            self._fdict = field_dict
        else:
            self._fdict = {}

        self.__initialised = True

    def __setattr__(self, name, value):
        if not self.__dict__.has_key(
                '_Field__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, name, value)
        else:
            self._fdict[name] = value

    def __getattr__(self, name):
        if not self._fdict.has_key(name):
            raise AttributeError, "Doesnt have field with name : %s" % name
        return self._fdict[name]

    def __setitem__(self, name, value):
        self._fdict[name] = value

    def __getitem__(self, name):
        return self._fdict[name]

    def __repr__(self):
        return 'Field(%s)' % str(self._fdict)


class Connection(object):
    """
    Represents a Connection to the Shooju api
    """

    def __init__(self, username, api_key, server):
        """
        Initializes connection with Shooju API
        :param str username: Shooju username
        :param api_key: Shooju API key
        :param server: Shooju server with protocol (https://alpha2.shooju.com)
        """
        self._shooju_api = ShoojuApi(server, username, api_key)
        self.job_source = "python"

        # testing connection with server to make sure credentials are valid and server is up
        self._shooju_api.ping()

    @property
    def raw(self):
        """
        Retrieves a REST client to perform arbitrary requests to shooju api

        Usage:
            conn.raw.get('/teams/', params={'q': 'test'})
            conn.raw.post('/teams/myteam/', data_json={'description': 'description'})
            conn.raw.delete('/series/single/', params={'series_id': series_id}

        :return: shooju.Client instance
        """
        return self._shooju_api.client

    @property
    def pd(self):
        """
        If pandas is installed, pd can be used to format data as pandas data structures

        Usage:
            conn.pd.search_series('', size=0, query_size=3, fields=['code_country'])
                returns a pandas.DataFrame
            conn.pd.get_fields('series_id')
                returns a pandas.Series
            conn.get_points('series_id', size=30)
                returns a pandas.Series

        :return: shooju.PandasFormatter instance
        """
        if PANDAS_SUPPORT:
            if not hasattr(self, '_pandas_formatter'):
                self._pandas_formatter = PandasFormatter(self._shooju_api)
            return self._pandas_formatter
        else:
            return None

    def change_job_source(self, name):
        """
        Changes the name of the source

        :param str name: name of the new job source
        """
        self.job_source = name

    def search(self, query='', date_start=None, date_finish=None, fields=None, size=10, query_size=10):
        """
        Performs a block search

        :param query: query to perform
        :param query_size: number of series to return
        :param date_start: start date for points
        :param date_finish: end date for points
        :param fields: list of fields to retrieve
        :param size: number of points to retrieve per series
        :return: a dict hashed by series id with a list of Points per series id
        :rtype: dict
        """
        data = self._shooju_api.search_series(query, date_start, date_finish, size, query_size, fields)
        return self._process_search_response(data)

    def scroll_series(self, query='', date_start=None, date_finish=None, fields=None, size=10):
        """
        Performs a scroll search. Function is a generator, it returns dicts of series.

        Usage:

            for series in conn.scroll_series():
                # do something with the dict

        :param query: query to perform
        :param date_start: start date for points
        :param date_finish: end date for points
        :param fields: list of fields to retrieve
        :param size: number of points to retrieve per series
        """

        data = self._shooju_api.search_series(query, date_start, date_finish, size, fields=fields, scroll=True)
        scroll_id = data['scroll_id']
        yield self._process_search_response(data)

        while True:
            data = self._shooju_api.scroll_series(scroll_id)
            if not data['series_ids']:
                break
            else:
                yield self._process_search_response(data)

    def get_points(self, series_id, date_start=None, date_finish=None, size=10):
        """
        Retrieves points for a series id. Can select time range

        :param str series_id: series id
        :param datetime.datetime date_start: get points < date
        :param datetime.datetime date_finish: get points > date
        :param int size: number of points to get
        :return: a list of Points
        :rtype: list
        """
        data = self._shooju_api.get_series(series_id, date_start, date_finish, size)
        return map(lambda p: Point(p[0], p[1]), data['points'])

    def get_point(self, series_id, dt):
        """
        Retrieves a point from the series

        :param str series_id: series id
        :param datetime.datetime dt: date of the point
        :return: a Point instance
        :rtype: shooju.Point
        """
        points = self.get_points(series_id, dt, dt)
        return points[0] if len(points) == 1 else None

    def get_field(self, series_id, field):
        """
        Retrieves a field value from the series

        :param str series_id: series id
        :param str field: name of the field
        :return: value of the field
        :rtype: str
        """
        return self.get_fields(series_id, [field])[field]

    def get_fields(self, series_id, fields=None):
        """
        Retrieves fields from series. Parameter `fields` is a list of field names. If `fields` is not
        present, all of the fields are returned

        :param str series_id: series id
        :param list fields: list of fields to retrieve
        :return: fields of the series
        """
        data = self._shooju_api.get_series(series_id, size=0, fields=fields)
        field = Field()
        for k, v in data['fields'].iteritems():
            field[k] = v

        return field

    def register_job(self, name, description="", notes="", batch_size=1):
        """
        Registers a job in Shooju. A job is used to write series.

        :param str name: name of the job
        :param str description: brief description
        :param str notes: notes about the job
        :param int batch_size: indicates the size of the buffer before creating new series in the server
        :return: a RemoteJob instance
        :rtype: shooju.RemoteJob
        """
        data = self._shooju_api.register_job(name, description, notes, self.job_source)

        return RemoteJob(self, data['job_id'], batch_size=batch_size)

    def multi_get(self):
        """
        Creates a multiget object to perform requests in batch
        """
        return GetBulk(self)

    def delete(self, series_id):
        """
        Deletes the series

        :param series_id: series id
        :return: True if the deletion was successful
        """
        return self._shooju_api.delete_series(series_id)

    def download_file(self, file_id, filename=None):
        """
        Downloads a file. If no `filename` is provided, a temporary file is created

        :param file_id: file id
        :param filename: file name for downloaded file
        :return: File instance
        """
        return self._shooju_api.download_file(file_id, filename)

    def _post_bulk(self, bulk_data, job_id=None):
        """
        Helper method to perform a series POST bulk request. Do not used directly

        :param list bulk_data: list of requests
        :param str int job_id: job id
        :return: dict with the response
        """
        return self._shooju_api.bulk_series(bulk_data, job_id)

    def _get_bulk(self, bulk_data):
        """
        Internal method use get_bulk method to create
        GetBulk object and to to do getting bulk operations
        through it. @bulk_data is the dict to be sent to server
        """
        return self._shooju_api.bulk_series(bulk_data)

    def _process_search_response(self, data):
        """
        Helper method to convert a block search response to the module data structures
        :param data: api block response
        :return: a dict hashed by series ids with a list of Points and Field
        """
        result = defaultdict(dict)
        for i, series_id in enumerate(data['series_ids']):
            if data['points']:
                for j, date in enumerate(data['points']['dates']):
                    value = data['points']['values'][j][i]
                    if value is not None:
                        result[series_id].setdefault('points', []).append(Point(date, value))
            else:
                result[series_id]['points'] = []

            fields = Field()
            for k, field in enumerate(data['fields']['fields']):
                value = data['fields']['values'][k][i]
                if value is not None:
                    fields[field] = value
            result[series_id]['fields'] = fields
        return dict(result)


class PandasFormatter(object):

    def __init__(self, api_client):
        """

        :param shooju.ShoojuApi api_client: ShoojuApi instance
        """
        self.api_client = api_client

    def search_series(self, query='', date_start=None, date_finish=None, size=10, fields=None, query_size=10):
        """
        Performs a block search and returns the results in pandas.DataFrame.

        :param query: query to perform
        :param query_size: number of series to return
        :param date_start: start date for points
        :param date_finish: end date for points
        :param size: number of points to retrieve per series
        :param fields: list of fields to retrieve
        :return: a pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        response = self.api_client.search_series(query, date_start, date_finish, size, query_size, fields)
        return self._process_search_request(response)

    def get_points(self, series_id, date_start=None, date_finish=None,size=10):
        """
        Gets the points of a series

        :param str series_id: series id
        :param datetime.datetime date_start: start date for points
        :param datetime.datetime date_finish: end date for points
        :param int size: number of points to retrieve
        :return: a pandas.Series with the points
        """
        response = self.api_client.get_series(series_id, date_start, date_finish, size, fields=[])
        index = [unixtime_to_datetime(p[0]) for p in response['points']]
        values = [p[1] for p in response['points']]
        return pandas.Series(values, index)

    def get_fields(self, series_id, fields=None):
        """
        Gets the fields for a series

        :param series_id: series id
        :param fields: list of fields
        :return: a pandas.Series with the fields
        """
        response = self.api_client.get_series(series_id, size=0, fields=fields)
        return pandas.Series(response['fields'])


    def _process_search_request(self, response):
        """
        Processes the search results and returns a pandas.DataFrame

        If there are only points it returns a DataFrame with columns for series_id and the dates of the points,
        if there are only fields it returns a DataFrame with colums for series_id and the name of the fields,
        if there are both it returns a DataFrame with columns for series_id, the name of the fields, date and points,
        the size of the DataFrame is number of series ids * number of dates in the result

        :param dict response: api response dict
        :return: a pandas.DataFrame with the search result data
        """
        series_ids = response['series_ids']
        if not series_ids:
            return pandas.DataFrame()

        has_fields = truth(response['fields'].get('fields'))
        has_points = truth(response['points'])

        if has_points and has_fields:
            series_dates = response['points']['dates']
            num_of_dates = len(series_dates)
            num_of_series = len(series_ids)

            # preparing dict to feed DataFrame
            data = {
                'series_id': list(flatten([series_id] * num_of_dates for series_id in series_ids)),
                'date':  map(unixtime_to_datetime, series_dates * num_of_series),
                'points': list(roundrobin(*response['points']['values']))
            }
            data.update(
                {field: list(flatten([value] * num_of_dates for value in response['fields']['values'][i])) for i, field in enumerate(response['fields']['fields'])}
            )
        elif has_points:
            data = {'series_id': series_ids}
            data.update({unixtime_to_datetime(date): response['points']['values'][i] for i, date in enumerate(response['points']['dates'])})

        elif has_fields:
            data = {'series_id': series_ids}
            data.update(
                {field: response['fields']['values'][i] for i, field in enumerate(response['fields']['fields'])}
            )
        else:
            data = {'series_id': series_ids}

        return pandas.DataFrame(data)


class ShoojuApi(object):
    """
    Class used to encapsulate Shooju API methods. Methods return the json decoded response from the server and raise
    an error if the response had errors.
    """

    API_URL = '/api/1'
    API_SERIES_SINGLE = '/series/single'
    API_SERIES_BULK = '/series/bulk/'
    API_SERIES_BLOCK_SEARCH = '/series/block/search'
    API_SERIES_SCROLL = '/series/block/scroll'
    API_JOBS = '/jobs/'
    API_FILES = '/files/{id}/download'
    API_STATUS = '/status/detailed/'
    API_PING = '/status/ping'

    def __init__(self, server, user, password):
        url = '{}{}'.format(server, self.API_URL)
        self.client = Client(url, user, password)

    def get_series(self, series_id, date_start=None, date_finish=None, size=10, fields=None):
        """
        Retrieves series

        :param str series_id: series id
        :param datetime.datetime date_start: start date for points
        :param datetime.datetime date_finish:  end date for points
        :param int size: number of points to retrieve
        :param list fields: list of fields to retrieve
        :return: api response
        :rtype: dict
        """
        params = {
            'date_format': 'unix',
            'df': to_unixtime(date_start) if date_start else 'MIN',
            'dt': to_unixtime(date_finish) if date_finish else 'MAX',
            'size': size,
            'series_id': series_id
        }

        if fields is not None:
            params['fields'] = ','.join(fields)

        response = self.client.get(self.API_SERIES_SINGLE, params=params)
        return response

    def bulk_series(self, requests, job_id=None):
        """
        Executes a bulk series request

        :param list requests: list of dict with the requests to be performed
        :param int str job_id: job id
        :return: api reponse
        :rtype: dict
        """
        params = {'job_id': job_id} if job_id else None
        payload = {'requests': requests}
        response = self.client.post(self.API_SERIES_BULK, data_json=payload, params=params)
        return response

    def delete_series(self, series_id):
        """
        Deletes the series

        :param series_id: series id
        :return: True if the deletion was successful
        """
        params = {'series_id': series_id}
        self.client.delete(self.API_SERIES_SINGLE, params=params)
        return True

    def register_job(self, name, description, notes='', source='shooju'):
        """
        Registers a job in Shooju.

        :param str name: name of the job
        :param str description: brief description
        :param str notes: notes about the job
        :param str source: source of the job
        :return: api response
        :rtype: dict
        """
        payload = {
            "name": name,
            "source": source,
            "description": description,
            "notes": notes
        }

        data = self.client.post(self.API_JOBS, data_json=payload)
        return data

    def download_file(self, file_id, filename=None):
        """
        Downloads a file. If no `filename` is provided, a temporary file is created

        :param file_id: file id
        :param filename: file name for downloaded file
        :return: File instance
        """
        path = self.API_FILES.format(id=file_id)
        if filename:
            f = open(filename, 'w+b')
        else:
            f = tempfile.NamedTemporaryFile(prefix='download')

        r = self.client.get(path, binary_response=True)

        for chunk in r.iter_content(chunk_size=16 * 1024):
            if chunk:
                f.write(chunk)
                f.flush()
        f.seek(0, 0)
        return f

    def search_series(self, query='', date_start=None, date_finish=None, size=10, query_size=None, fields=None, scroll=False):
        """
        Performs a search request to the shooju api

        :param query: query string
        :param date_start: points start date
        :param date_finish: points end date
        :param size: number of points
        :param query_size: number of series to retrieve
        :param fields: list of fields to retrieve
        :param scroll: flag indicating if it's a scroll search
        :return: dict with the api response
        """
        params = {
            'query': query,
            'df': to_unixtime(date_start) if date_start else 'MIN',
            'dt': to_unixtime(date_finish) if date_finish else 'MAX',
            'size': size,
        }

        if fields:
            params['fields'] = ','.join(fields)

        if query_size is not None:
            params['query_size'] = query_size

        if scroll:
            params['scroll'] = True

        return self.client.get(self.API_SERIES_BLOCK_SEARCH, params=params)

    def scroll_series(self, scroll_id):
        """
        Series scroll endpoint. Retrieves the next scroll data. Should be used in tandem with
        search_series with scroll flag set to True.

        Scroll has finished when no more series are returned

        :param scroll_id: scroll id
        :return: api response
        :rtype: dict
        """
        response = self.client.get(self.API_SERIES_SCROLL, params={'scroll_id': scroll_id})
        return response

    def api_status(self):
        """
        Checks Shooju API status

        :return: api response
        :rtype: dict
        """
        return self.client.get(self.API_STATUS)

    def ping(self):
        """
        Pings Shooju API

        :return: API response
        """
        return self.client.get(self.API_PING)


class Client(object):

    ALLOWED_METHODS = ('get', 'post', 'delete')  # list of allowed HTTP methods

    def __init__(self, url_base, user, password):
        """
        REST Client

        :param str url_base:  url of the server including protocol ('https://alpha2.shooju.com')
        :param str user: username
        :param password: api secret
        """
        self._url_base = url_base
        self._user = user
        self._password = password
        self._method = None

    def __getattr__(self, item):
        if item not in self.ALLOWED_METHODS:
            raise AttributeError('Method %s not supported' % item)
        self._method = item
        return self._call

    def _call(self, path=None, **kwargs):
        """
        Helper method that executes the HTTP request. By default, it json decodes the response and checks for API errors

        accepted keyword arguments:
            - binary_response (bool) flag indicating if the response is binary
            - data_json (dict) json payload
            - data_raw (str) raw payload
            - data (str) url encoded payload
            - params (dict) hash with the url parameters

        :param str path: resource path
        :param kwargs: keyword arguments
        :return: :raise ConnectionError: json response (or binary response if binary response selected)
        """
        headers = None
        payload = None
        json_reponse = kwargs.get('json_reponse', True)
        binary_reponse = kwargs.get('binary_response', False)
        if 'data_json' in kwargs:
            headers = {'content-type': 'application/json'}
            payload = json.dumps(kwargs.get('data_json'))
        elif 'data_raw' in kwargs:
            payload = kwargs.get('data_raw')
        elif 'data' in kwargs:
            payload = kwargs.get('data')

        method = getattr(requests, self._method)
        if binary_reponse:
            method = partial(method, stream=True)

        url = '{base}{path}'.format(base=self._url_base, path=path)
        r = method(url, params=kwargs.get('params'), data=payload, headers=headers, auth=(self._user, self._password))

        if r.status_code != requests.codes.ok:
            raise ConnectionError('Request failed. Error code %s' % r.status_code)

        if binary_reponse:
            return r
        elif json_reponse:
            return _check_errors(r.json())
        return r.text


def _check_errors(response):
    """
    Checks the API response for errors. Raises error if error is found in the response.

    :param dict response: api response
    :return: :raise ConnectionError: response
    """
    if not response['success']:
        raise ShoojuApiError(_format_error(response))
    if 'responses' in response:  # it's a bulk request
        _check_bulk_api_error(response)
    return response


def _check_bulk_api_error(response):
    """
    Checks bulk API response array
    :param dict response: api response
    :raise ConnectionError:
    """
    errors = []
    for response in response['responses']:
        if not response['success']:
            errors.append(_format_error(response))
    if errors:
        raise ShoojuApiError('\n'.join(errors))


def _format_error(response):
    """
    Formats the response error
    :param response: api response
    :return: formatted error string
    """
    return '%s (%s)' % (response.get('error'), response.get('description'))


class RemoteJob(object):
    """
    That object is used to submit data to API
    """

    def __init__(self, conn, job_id, batch_size):
        """
        Initialized with connection and job_id.

        :param shooju.Connection conn: API connection
        :param job_id: job id
        :param int batch_size: size of cache before uploading series to the API
        """
        self._conn = conn
        self._job_id = job_id
        self._batch_size = batch_size
        self._cur_batch_size = 0

        #those are values that will be sent to server
        #series_id will be the key and they will match to
        #{'fields':{},'points':{}} that !
        self._values = {}

    @property
    def job_id(self):
        return self._job_id

    def _init_get_series_dict(self, series, incr_bulk=False):
        if not self._values.has_key(series):
            self._values[series] = {'fields': {}, 'points': {}}
            if incr_bulk:
                self._cur_batch_size += 1
        else:
            if not self._values[series]['points'] and incr_bulk:
                self._cur_batch_size += 1

        return self._values[series]

    def _submit_if_bulk(self):
        """
        Submits data if we have enough  bulk
        """
        if self._cur_batch_size >= self._batch_size:
            self.submit()
            self._cur_batch_size = 0

    def put_points(self, series_id, points):
        """
        Accepts the series and points(Point objects)
        that will be submitted to server.

        :param series_id: series id
        :param list points: list of shooju.Point
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        for p in points:
            series_values['points'].update(p.to_dict())

        self._submit_if_bulk()

    def put_point(self, series_id, pt):
        """
        Submits a single point.

        :param shooju.Point pt: point
        :param str series_id: series id
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        series_values['points'].update(pt.to_dict())

        self._submit_if_bulk()

    def put_field(self, series_id, field_name, field_value):
        """
        Submits single field.

        :param str series_id: series id
        :param str field_name: name of the field
        :param str field_value: value of the field
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        series_values['fields'].update({field_name: field_value})

        self._submit_if_bulk()

    def put_fields(self, series_id, field_object):
        """
        Submits field objects.

        :param srt series_id:
        :param shooju.Field field_object: Field object with fields
        """
        series_values = self._init_get_series_dict(series_id, incr_bulk=True)
        series_values['fields'].update(field_object)

        self._submit_if_bulk()

    def submit(self):
        """
        Submits the current cached data to server
        """
        #the submit part should traverse all of the sids and submit them
        bulk_data = []
        for series, values in self._values.iteritems():
            #here we will construct a BULK API call
            tmp_dict = {"type": "POST", "id": series, "body": values}
            bulk_data.append(tmp_dict)

        #we send the bulk data at once
        if bulk_data:
            self._conn._post_bulk(bulk_data, self._job_id)

        #also empty the current cache
        self._values = {}
        return True


class GetBulk(object):
    """
    That class is responsible for constructing a get bulk
    request and send it to the remote API.
    """

    def __init__(self, conn):
        """
        Gets a connection object to send the data to server
        """
        self._conn = conn
        self._reqs = []


    def get_point(self, series_id, date):
        """
        Gets a point 
        """
        data = {
            '_get_type': 'get_point',
            'date_format': 'unix',
            'df': to_unixtime(date),
            'dt': to_unixtime(date),
            'id': series_id
        }

        self._reqs.append(data)

    def get_points(self, series_id, date_start=None, date_finish=None, size=10):
        """
        Get points method
        """
        data = {
            '_get_type': 'get_points',
            'date_format': 'unix',
            'df': 'MIN',
            'dt': 'MAX',
            'size': size,
            'id': series_id
        }

        if date_start:
            data['df'] = to_unixtime(date_start)

        if date_finish:
            data['dt'] = to_unixtime(date_finish)

        self._reqs.append(data)

    def get_fields(self, series_id, fields=None):
        """
        Gets fields for series_id
        if fields is None then all of the fields for series is fetched
        if fields is a list then only those in the list are fetched
        """
        data = {
            '_get_type': 'get_fields',
            'date_format': 'unix',
            'df': 'MIN',
            'dt': 'MAX',
            'id': series_id,
            'size': 0
        }

        if fields:
            data['fields'] = ",".join(fields)

        self._reqs.append(data)


    def get_field(self, series_id, field):
        """
        Gets field
        """
        data = {
            '_get_type': 'get_field',
            'date_format': 'unix',
            'df': 'MIN',
            'dt': 'MAX',
            'size': 0,
            'id': series_id,
            'size': 0
        }

        data['fields'] = field
        self._reqs.append(data)


    def fetch(self):
        """
        That is the place we construct the get bulk query
        """
        #for now just puts the series id, but will change in future
        bulk_get = []
        for r in self._reqs:
            tmp = {"type": "GET"}
            for k, v in r.iteritems():
                if not k.startswith("_"):
                    tmp[k] = v

            bulk_get.append(tmp)

        if not bulk_get:
            return []

        result = self._conn._get_bulk(bulk_get)
        #do some cleanup here !

        responses = []
        for i, resp in enumerate(result['responses']):
            responses.append(self._convert_web_data(self._reqs[i]['_get_type'], resp))

        self._reqs = []

        return responses

    def _convert_web_data(self, get_type, response):
        """
        Converts the data that comes from web to Point and Field objects
        """
        if get_type == "get_points":
            return map(lambda p: Point(p[0], p[1]), response['points'])
        elif get_type == "get_fields" or get_type == "get_field":
            field = Field()
            for k, v in response['fields'].iteritems():
                field[k] = v
            return field
        elif get_type == "get_point":
            pdata = response['points'][0]
            return Point(pdata[0], pdata[1])
        else:
            return []

def flatten(iterable):
    """
    Flattens a list

    :param iterable: list of lists
    """
    for x in iterable:
        if hasattr(x, '__iter__') and not isinstance(x, basestring):
            for y in flatten(x):
                yield y
        else:
            yield x

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))

class ConnectionError(Exception):
    """
    Connection Errors
    """
    pass

class ShoojuApiError(Exception):
    """
    Shooju API errors
    """
    pass


