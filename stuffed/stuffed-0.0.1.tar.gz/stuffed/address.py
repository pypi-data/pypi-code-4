import math
import requests
try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3

# https://developers.google.com/maps/documentation/geocoding/#Types
ADDRESS_TYPES = ['street_address','route','intersection','political','country','administrative_area_level_1',
                    'administrative_area_level_2','administrative_area_level_3','colloquial_area','locality',
                    'sublocality','neighborhood','premise','subpremise','postal_code','natural_feature','airport',
                    'park','point_of_interest']

STATES = (('AK', 'Alaska'),('AL', 'Alabama'),('AR', 'Arkansas'),('AZ', 'Arizona'),('CA', 'California'),('CO', 'Colorado'),('CT', 'Connecticut'),('DC', 'District of Columbia'),('DE', 'Delaware'),('FL', 'Florida'),('GA', 'Georgia'),('GU', 'Guam'),('HI', 'Hawaii'),('IA', 'Iowa'),('ID', 'Idaho'),('IL', 'Illinois'),('IN', 'Indiana'),('KS', 'Kansas'),('KY', 'Kentucky'),('LA', 'Louisiana'),('MA', 'Massachusetts'),('MD', 'Maryland'),('ME', 'Maine'),('MI', 'Michigan'),('MN', 'Minnesota'),('MO', 'Missouri'),('MS', 'Mississippi'),('MT', 'Montana'),('NA', 'National'),('NC', 'North Carolina'),('ND', 'North Dakota'),('NE', 'Nebraska'),('NH', 'New Hampshire'),('NJ', 'New Jersey'),('NM', 'New Mexico'),('NV', 'Nevada'),('NY', 'New York'),('OH', 'Ohio'),('OK', 'Oklahoma'),('OR', 'Oregon'),('PA', 'Pennsylvania'),('RI', 'Rhode Island'),('SC', 'South Carolina'),('SD', 'South Dakota'),('TN', 'Tennessee'),('TX', 'Texas'),('UT', 'Utah'),('VA', 'Virginia'),('VI', 'Virgin Islands'),('VT', 'Vermont'),('WA', 'Washington'),('WI', 'Wisconsin'),('WV', 'West Virginia'),('WY', 'Wyoming') )
MILES = 'Miles'
KILOMETERS = 'Kilometers'
METERS = 'Meters'


class Address(object):
    """Geocoding: <a href="https://developers.google.com/maps/documentation/geocoding/">Google Geocoding</a>
    """
    def __init__(self, component_group=None, **address):
        """Address must be supplied
        """
        self._address = component_group or address
        
#       if not self.__address or not self.__latlng:
#           uri = "https://maps.googleapis.com/maps/api/geocode/json?%s" % urllib.urlencode(dict(
#               address = (str(address) if address else ','.join(map(str,self.latlng()))),
#               sensor = str(self.get_sensor()).lower()))
#               
#           try:
#               url = urllib2.urlopen(uri)
#               data = tornado.escape.json_decode(url.read())
#               url.close()
#           except urllib2.URLError as a:
#               print a
#           except urllib2.HTTPError as httperror:
#               #self.data['error'] =   (url, httperror)
#               print httperror
#           else:
#               if data.get('status',False) == 'OK':
#                   for result in data['results']:
#                       if 'street_address' in result['types']:
#                           self.__address = dict(zip(('street', 'city', 'state', 'zip', 'country'), 
#                               filter(lambda a: a not in (None,', ',' '),re.split('(,\s)|(\s(?=\d{5}))',result.get('formatted_address')))))
#                           break
#               else:
#                   self.data['error'] = (url, data)
#               elif data.get('status',False) == 'ZERO_RESULTS':
#                   pass
#               elif data.get('status',False) == 'OVER_QUERY_LIMIT':
#                   pass
#               elif data.get('status',False) == 'REQUEST_DENIED':
#                   pass
#               elif data.get('status',False) == 'INVALID_REQUEST':
#                   pass
#               else:
#                   raise Error('Unknown error retrieving address.')
    @property
    def address(self):
        return self._address

    @property
    def id(self):
        return self._address.get('id')

    @property
    def street(self):
        return self._address.get('street')

    @property
    def city(self):
        return self._address.get('city')

    @property
    def state(self):
        return self._address.get('state')

    @property
    def zip(self):
        return self._address.get('zip')

    @property
    def latlng(self):
        return self._address.get('latlng')

    @property
    def x(self):
        return self._address.get('latlng')[0]

    @property
    def y(self):
        return self._address.get('latlng')[1]

    def distance_to(self, address, measure='Miles'):
        """Distance to another address
        """
        if isinstance(address, Address) and self.latlng and address.latlng:
            lat1, lon1 = map(float,self.latlng())
            lat2, lon2 = map(float,address.latlng())
        elif self.latlng and type(address) is tuple:
            lat1, lon1 = map(float,self.latlng())
            lat2, lon2 = address
        else:
            raise ValueError(":address must be type tuple or Address")
            
        radius = 6371 # km          
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
          * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c
        # d is in kilometers
        if measure == KILOMETERS:
            return d
        elif measure == METERS:
            return d / 1000
        elif measure == MILES:
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
    def get_directions(self, _from, _to, sensor=False):
        a = _from.get_address() if isinstance(_from, Address) else _from
        b = _from.get_address() if isinstance(_to, Address) else _to
        data = requests.get("http://maps.googleapis.com/maps/api/directions/json",
                            params=dict(origin=a,
                                        destination=b,
                                        sensor=str(sensor).lower()))
        json = data.json()
        if json.get('status',False) == 'OK':
            if not isinstance(_from, Address):
                _from = Address(json['routes'][0]['legs'][0]['start_address'], load=False, latlng=(json['routes'][0]['legs'][0]['start_location']['lat'], json['routes'][0]['legs'][0]['start_location']['lng']))
            if not isinstance(_to, Address):
                _to = Address(json['routes'][0]['legs'][0]['end_address'], load=False, latlng=(json['routes'][0]['legs'][0]['end_location']['lat'], json['routes'][0]['legs'][0]['end_location']['lng']))
            return _from, _to, json
        return None,None,None

    @classmethod
    def findall(self, text, **kwargs):
        """Finds all the address objects in a blog text
        """
        return []
