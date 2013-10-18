""" Feeds API

Echo Platform allows you to register Activity Stream feeds in the system. Registered URLs will be aggressively polled by the Platform looking for new data and the data will be submitted into the Echo database.
"""
from echo.core_api import EchoClient, StreamServerError
from parsers import OPMLFeedsContentHandler, ErrorFeedsContentHandler
from xml.sax import SAXParseException

import logging

# ======================================================================

class Client(EchoClient):
    def list(self, parsed=True):
        """ Fetch the list of registered feeds for a specified API key.
        When parsed=True, the default, it returns a nested dictionary of the 'feeds':
        { 'title': u'Feeds for example.com',
          'feeds': [ { u'refreshRate': u'300',
                   u'text': u'http://example.com/feed/1',
                   u'type': u'atom',
                   u'xmlUrl': u'http://example.com/feed/1'},
                 { u'refreshRate': u'50',
                   u'text': u'http://example.com/feed/2',
                   u'type': u'atom',
                   u'xmlUrl': u'http://example.com/feed/2'}]}
        When parsed=False, returns an OPML 2.0 (See http://www.opml.org/spec2) XML document.
        On error, it raises echo.StreamServerError.
        """
        try:
            xml_doc = self._send_request('feeds/list', http_post=False, is_json=False)
            if parsed:
                opml = OPMLFeedsContentHandler(xml_doc)
                return opml.feeds_dict
            else:
                return xml_doc
        except SAXParseException:
            # Error Document is invalid XML w/o root node; make it valid and parse it!
            xml_error_doc = '\n'.join([ '<stream>', xml_doc, '</stream>' ])
            err = ErrorFeedsContentHandler(xml_error_doc)
            raise StreamServerError(err.error_dict)

    def register(self, url, interval=300):
        """ Register a new Activity Stream feed URL to update every interval seconds. """
        param_d = {
            'url': url,
            'interval': interval, # seconds
        }
        r = self._send_request('feeds/register', param_d, http_post=False)
        # Return True on success.
        if 'result' in r and r['result'] == 'success':
            return True
        else:
            return False

    def unregister(self, url):
        """ Remove a certain URL form the list of Activity Stream feeds registered earlier. """
        param_d = {
            'url': url,
        }
        r = self._send_request('feeds/unregister', param_d, http_post=False)
        # Return True on success.
        if 'result' in r and r['result'] == 'success':
            return True
        else:
            return False

# Module-level client exposes API
# ======================================================================

def list(parsed=True):
    """ Fetch the list of registered feeds for a specified API key.
    When parsed=True, the default, it returns a nested dictionary of the 'feeds':
    { 'title': u'Feeds for example.com',
      'feeds': [ { u'refreshRate': u'300',
                   u'text': u'http://example.com/feed/1',
                   u'type': u'atom',
                   u'xmlUrl': u'http://example.com/feed/1'},
                 { u'refreshRate': u'50',
                   u'text': u'http://example.com/feed/2',
                   u'type': u'atom',
                   u'xmlUrl': u'http://example.com/feed/2'}]}
    When parsed=False, returns an OPML 2.0 (See http://www.opml.org/spec2) XML document.
    On error, it raises echo.StreamServerError.
    """
    return Client.get_client().list(parsed=parsed)

def register(url, interval=300):
    """ Register a new Activity Stream feed URL to update every interval seconds. """
    return Client.get_client().register(url, interval=interval)

def unregister(url):
    """ Remove a certain URL form the list of Activity Stream feeds registered earlier. """
    return Client.get_client().unregister(url)

