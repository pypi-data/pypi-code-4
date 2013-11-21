"""MPower Payments

MPower Payments Python clinet library.
Modules implemented: DirectPay, DirectCard, Invoice, and OPR
"""

__version__ = '0.1.0'
__author__ = "Mawuli Adzaku <mawuli@mawuli.me>"

import os
import sys
import requests
try:
    import simplejson as json
except ImportError:
    import json

# runs in LIVE mode by defaults
debug = False
api_keys = {}
store = None

# MPower HTTP API version
API_VERSION = 'v1'

SERVER = "app.mpowerpayments.com"

#Sandbox Endpoint
SANDBOX_ENDPOINT = "https://%s/sandbox-api/%s/" % (SERVER, API_VERSION)

# Live Endpoint
LIVE_ENDPOINT = "https://%s/api/%s/" % (SERVER, API_VERSION)

# user-agent
MP_USER_AGENT = "mpower-python/v%s" % __version__

# simple hack to reference current module
__MODULE__ = sys.modules[__name__]


class MPowerError(Exception):
    """Base Exception class"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Store(object):
    """MPower Store

    Creates a storw object for MPower Payments transactions
    """
    def __init__(self, info={}):
        self.info = {"name": info.get("name"),
                     "tagline": info.get("tagline"),
                     "postal_address": info.get("postal_address"),
                     "phone": info.get("phone"),
                     "logo_url": info.get("logo_url"),
                     "website_url": info.get("website_url")
        }


class Payment(object):
    """Base class for other MPower payments classes"""
    def __init__(self):
        """Base class for all the other payment libraries"""
       # request headers
        self._headers = {'User-Agent': MP_USER_AGENT,
                         "Content-Type": "application/json"}
        # response object
        self._response = None
        # data to send to server
        self._data = None
        self.store = __MODULE__.store or Store()

    def _process(self, resource=None, data={}):
        """Processes the current transaction

        Sends an HTTP request to the currently active endpoint of the MPower API
        """
        # use object's data if no data is passed
        _data = data or self._data
        rsc_url = self.get_rsc_endpoint(resource)
        if _data:
            req = requests.post(rsc_url, data=json.dumps(data),
                               headers=self.headers)
        else:
            req = requests.get(rsc_url, params=data,
                               headers=self.headers)
        if req.status_code == 200:
            self._response = json.loads(req.text)
            if int(self._response['response_code']) == 00:
                return (True, self._response)
            else:
                return (False, self._response['response_text'])
        return (response.code, "Request Failed")

    @property
    def headers(self):
        """Returns the client's Request headers"""
        return dict(self._config, **self._headers)

    def add_header(self, header):
        """Add a custom HTTP header to the client's request headers"""
        if type(header) is dict:
            self._headers.update(header)
        else:
            raise ValueError("Dictionary expected, got '%s' instead" % type(header))

    def get_rsc_endpoint(self, rsc):
        """Returns the HTTP API URL for current payment transaction"""
        if self.debug:
            return SANDBOX_ENDPOINT + rsc
        return LIVE_ENDPOINT + rsc

    @property
    def debug(self):
        """Returns the current transaction mode"""
        return __MODULE__.debug

    @property
    def _config(self):
        _m = __MODULE__
        return {'MP-Master-Key': _m.api_keys.get('MP-Master-Key'),
                'MP-Private-Key': _m.api_keys.get('MP-Private-Key'),
                'MP-Token': _m.api_keys.get('MP-Token')
        }


# moved here so the modules that depend on the 'Payment' class will work
from .invoice import Invoice
from .direct_payments import DirectPay, DirectCard
from .opr import OPR

__all__ = [Store.__name__,
           Payment.__name__,
           Invoice.__name__,
           DirectCard.__name__,
           DirectPay.__name__,
           OPR.__name__
]
