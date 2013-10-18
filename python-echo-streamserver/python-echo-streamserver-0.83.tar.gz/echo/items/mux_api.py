""" Items MUX API Utilities

The Items MUX API allows a single API call to "multiplex" several requests.
The multiplexed requests are executed concurrently and independently by the Echo server.

This module provides utilities to the Items API mux method, echo.items.mux().
"""
try:
    import json
except ImportError:
    import simplejson as json

import logging

MUX_METHODS = [ 'search', 'count' ]
MUX_MAX_REQUESTS = 100

class MuxRequestError(Exception):
    pass

class MuxRequest(object):
    def __init__(self, query, id=None, api_method='search'):
        if api_method not in MUX_METHODS:
            raise MuxRequestError("Invalid API method %r" % api_method)
        # API method is parameter "method", as required by API.
        self.method = api_method
        # Construct id code, when None is given.
        if id:
            self.id = id
        else:
            self.id = "%s%d" % (api_method, 0) # TODO: time or sequence number?
        # EQL query string is parameter "q", as required by API.
        self.q = unicode(query)

    def _json_d(self):
        # Create a JSON dict object for the mux request list.
        return self.__dict__ # watch the attributes!
    json = property(_json_d)

    def __str__(self):
        return json.dumps(self.json, indent=4)

    def __repr__(self):
        return "%s:\n%s" % (self.__class__.__name__, self.__str__())

def requests_json(mux_requests_list):
    """ Transform a MuxRequest objects list into a JSON document.
    """
    try:
        requests_list = [ m.json for m in mux_requests_list ]
        requests = json.dumps(requests_list, indent=4)
        return requests
    except Exception, e:
        logging.error("MuxRequest to JSON Error: %s" % str(e))
        raise TypeError("Invalid MuxRequest objects list: %s" % str(e))

if __name__ == "__main__":
    r = MuxRequest("scope:*")
    s = MuxRequest("scope:http://example.com/*", api_method='count')
    request_objs = [ r, s ]

    # Convert MuxRequest objects into JSON.
    requests = requests_json(request_objs)
    print "Requests JSON:\n%s" % requests
    print


