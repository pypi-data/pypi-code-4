import datetime

from bs4 import BeautifulSoup
import requests
from requests import ConnectionError


class ApiUnavailableException(Exception):
    """Exception thrown when the Phish.net API returns non-200 response code"""
    pass


class ApiException(Exception):
    """Exception thrown when the Phish.net API returns an error JSON"""
    pass


class API(object):
    """Wrapper for making web requests to the Phish.net API"""
    API_BASE_URL = "https://api.phish.net/api.js?api=2.0&format=json"

    def __init__(self, apikey=None):
        self.apikey = apikey

    def request(self, method, **params):
        """Make any request to the API"""
        params['method'] = method

        # Add the API Key if it exists
        if self.apikey:
            params['apikey'] = self.apikey

        # Hit the server for the data
        try:
            apidata = requests.get(self.API_BASE_URL, params=params).json()
        except ConnectionError:
            raise ApiUnavailableException("Error connecting to Phish.net API")

        # Check edge cases
        if type(apidata) == dict:
            if apidata.get('reason') == "General API Error":
                # Usually an API key issue
                raise ApiException(
                    "API returned an error. Does this require an API key?")
            elif apidata.get('reason') == "No Shows Found":
                # Just didn't find any results. Shows up as error.
                return []
            else:
                raise ApiException(
                    "Unknown API Error: {}".format(apidata.get('reason')))

        # Normal cases
        if len(apidata) == 1:
            return Show(self, apidata[0])
        else:
            return [Show(self, s) for s in apidata]

        return apidata

    def _check_error(self, apidata):
        """Check whether the request failed (usually due to API key issues)"""
        if hasattr(apidata, 'get') and apidata.get('success', 1) == 0:
            raise ApiException(
                "API returned an error. Does this method require an API key?")


class Show(object):
    """Object encompassing Phish.net Show data"""
    def __init__(self, api, data):
        self._api = api  # for later lookups

        self.nicedate = data['nicedate']
        self.relativetime = data['relativetime']
        self.showdate = data['showdate']
        self.showid = data['showid']
        self.showyear = data['showyear']

        self.venue = Venue(api, data['venue'], data['venueid'],
                           data['city'], data['state'], data['country'])

        # These fields not returned on every call
        self._url = data.get('url')
        self._raw_setlist = data.get('setlist')

        if self._raw_setlist:
            self.parse_setlist()

        # Create a real date object
        self.date = create_date(self.showdate)

    def __repr__(self):
        return "{} - {}".format(self.nicedate, self.venue)

    def update_url_setlist(self):
        """Get the URL and setlist data if it wasn't already present"""
        apidata = self._api.request("pnet.shows.setlists.get",
                                    showid=self.showid)
        self._url = apidata.url
        self._raw_setlist = apidata._raw_setlist
        self._setlist = apidata._setlist

    def parse_setlist(self):
        """Parse the raw setlist HTML into Python lists"""
        soup = BeautifulSoup(self._raw_setlist)
        sets = [[a.get_text() for a in p.find_all("a")]
                for p in soup.find_all("p")]
        sets = [s for s in sets if s]  # Remove empty sets
        self._setlist = sets

    @property
    def url(self):
        """URL is not set if we got this object from pnet.shows.query"""
        if not self._url:
            self.update_url_setlist()
        return self._url

    @property
    def setlist(self):
        """Setlist is not set if we got this object from pnet.shows.query"""
        if not self._raw_setlist:
            self.update_url_setlist()
        return self._setlist


class Venue(object):
    """Object encompassing Phish.net Venue data"""
    def __init__(self, api, name, venueid, city, state, country):
        self._api = api  # for later lookups

        self.name = name
        self.venueid = venueid
        self.city = city
        self.state = state
        self.country = country

        self._shows = None

    def __repr__(self):
        return "{name} - {city}, {state}, {country}".format(**self.__dict__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.venueid == other.venueid)

    @property
    def shows(self):
        if not self._shows:
            self._shows = self._api.request("pnet.shows.query",
                                            venueid=self.venueid)
        return self._shows


def create_date(showdate):
    "Convert a YYYY-mm-dd string into a datetime.date object"""
    year, month, day = map(int, showdate.split("-"))
    return datetime.date(year, month, day)
