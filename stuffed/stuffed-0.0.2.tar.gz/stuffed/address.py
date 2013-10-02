import math
import requests
import json
try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3

TornadoAsyncHTTPClient = None
TornadoHTTPResponse = None
try:
    from tornado.httpclient import AsyncHTTPClient as TornadoAsyncHTTPClient
    from tornado.httpclient import HTTPResponse as TornadoHTTPResponse
except ImportError:
    TornadoAsyncHTTPClient = None
    TornadoHTTPResponse = None

class Address(object):
    """Google Geocoding
    https://developers.google.com/maps/documentation/geocoding
    https://developers.google.com/maps/documentation/geocoding/#Types
    """
    _STATES = (('AK', 'Alaska'), ('AL', 'Alabama'), ('AR', 'Arkansas'), ('AZ', 'Arizona'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DC', 'District of Columbia'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('GU', 'Guam'), ('HI', 'Hawaii'), ('IA', 'Iowa'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('MA', 'Massachusetts'), ('MD', 'Maryland'), ('ME', 'Maine'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MO', 'Missouri'), ('MS', 'Mississippi'), ('MT', 'Montana'), ('NA', 'National'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('NE', 'Nebraska'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NV', 'Nevada'), ('NY', 'New York'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VA', 'Virginia'), ('VI', 'Virgin Islands'), ('VT', 'Vermont'), ('WA', 'Washington'), ('WI', 'Wisconsin'), ('WV', 'West Virginia'), ('WY', 'Wyoming'))
    MILES, KILOMETERS, METERS = 'Miles', 'Kilometers', 'Meters'

    def __init__(self, address=None, sensor=False, httpclient=None, callback=None):
        self._address = address
        self._sensor = sensor
        self._latlng = None
        self._components = {}
        self._callback = callback
        if address:
            self._geocode_request(address=address,
                                  httpclient=httpclient,
                                  callback=self._address_callback,
                                  sensor=sensor)

    @property
    def full(self):
        return self._address

    @property
    def id(self):
        return self._address.get('id')

    @property
    def name(self):
        return self._components.get('establishment')

    @property
    def type(self):
        return self._components.get('type')

    @property
    def street(self):
        if self._components.get('street_number') and self._components.get('route'):
            return self._components.get('street_number') + " " + self._components.get('route')
        else:
            None

    @property
    def city(self):
        return self._components.get('locality')

    @property
    def state(self):
        return self._components.get('administrative_area_level_1')

    @property
    def zip(self):
        return self._components.get('postal_code')

    @property
    def county(self):
        return self._components.get('administrative_area_level_2')

    @property
    def country(self):
        return self._components.get('country')

    @property
    def latlng(self):
        return self._latlng

    @property
    def lat(self):
        return self._latlng[0] if self._latlng else None

    @property
    def lng(self):
        return self._latlng[1] if self._latlng else None

    def distance_to(self, address, measure="Miles", httpclient=None):
        """Distance to another address
        """
        if isinstance(address, Address) and self.latlng and address.latlng:
            lat1, lon1 = map(float, self.latlng)
            lat2, lon2 = map(float, address.latlng)
        elif self.latlng and type(address) is tuple:
            lat1, lon1 = map(float, self.latlng)
            lat2, lon2 = address
        else:
            raise ValueError(":address must be type tuple or Address")
            
        radius = 6371 # km          
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
          * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c
        # d is in kilometers
        if measure == self.KILOMETERS:
            return d
        elif measure == self.METERS:
            return d / 1000
        elif measure == self.MILES:
            return d * .621371
        else:
            return d

    def staticmap(self, z=16, w=256, h=256):
        return "http://maps.googleapis.com/maps/api/staticmap?" + \
               urlencode(dict(center=str(','.join(map(str, self.latlng)) if self.latlng else str(self)),
                              zoom=z,
                              size="%dx%d" % (w, h),
                              maptype='roadmap',
                              markers='color:blue|label:abc|%s' % str(','.join(map(str,self.latlng) if self.latlng else str(self))),
                              sensor='false'))

    @classmethod
    def get_directions(self, fromaddr, toaddr, sensor=False):
        a = fromaddr.get_address() if isinstance(fromaddr, Address) else fromaddr
        b = fromaddr.get_address() if isinstance(toaddr, Address) else toaddr
        data = requests.get("http://maps.googleapis.com/maps/api/directions/json",
                            params=dict(origin=a,
                                        destination=b,
                                        sensor=str(sensor).lower()))
        json = data.json()
        if json.get('status',False) == 'OK':
            if not isinstance(fromaddr, Address):
                fromaddr = Address(json['routes'][0]['legs'][0]['start_address'], load=False, latlng=(json['routes'][0]['legs'][0]['start_location']['lat'], json['routes'][0]['legs'][0]['start_location']['lng']))
            if not isinstance(toaddr, Address):
                toaddr = Address(json['routes'][0]['legs'][0]['end_address'], load=False, latlng=(json['routes'][0]['legs'][0]['end_location']['lat'], json['routes'][0]['legs'][0]['end_location']['lng']))
            return fromaddr, toaddr, json
        return None,None,None

    @classmethod
    def search(self, address=None, sensor=False, httpclient=None, callback=None):
        """Returns a list of Addresses
        """
        pass

    def _geocode_request(self, address, httpclient, callback, sensor=False):
        if not httpclient:
            geocode = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
                                   params=dict(address=address,
                                               sensor=str(sensor).lower()))
            callback(geocode.json())

        elif isinstance(httpclient, TornadoAsyncHTTPClient):
            httpclient.fetch("https://maps.googleapis.com/maps/api/geocode/json?" + \
                             urlencode(dict(address=address,
                                            sensor=str(sensor).lower())),
                             callback=callback)

    def _address_callback(self, data):
        if isinstance(data, TornadoHTTPResponse):
            data = json.loads(data.body)
        if data.get('status') == 'OK':
            for result in data['results']:
                self._address = result['formatted_address']
                self._latlng = result['geometry']['location']['lat'], result['geometry']['location']['lng']
                self._components['type'] = result['types'][0]
                for component in result['address_components']:
                    self._components[component['types'][0]] = component['short_name']
        elif data.get('status',False) == 'ZERO_RESULTS':
            pass
        elif data.get('status',False) == 'OVER_QUERY_LIMIT':
            pass
        elif data.get('status',False) == 'REQUEST_DENIED':
            pass
        elif data.get('status',False) == 'INVALID_REQUEST':
            pass
        else:
            raise ValueError('Unknown error retrieving address.')

        if self._callback:
            self._callback(self)