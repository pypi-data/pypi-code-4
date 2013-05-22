""" Accessors for REST endpoints """
from urllib2 import HTTPError

from slacken.xml_accessor import XMLAccessor

__author__ = 'Alistair Broomhead'


class RESTaccess(object):
    """
    An accessor for REST endpoints

    rest_hub should be something like 'http://www.integration.moshi/services/rest'
    """
    rest_hub = ''

    @staticmethod
    def _get_raw(url, params=None):
        from urllib2 import build_opener, Request
        if params is not None:
            from urllib import urlencode
            params = urlencode(params)

        opener = build_opener()
        try:
            return opener.open(Request(url), params)
        except HTTPError:
            return opener.open(Request(url + '/'), params)

    @staticmethod
    def _parse_json(raw):
        from json import load
        return load(raw)

    @staticmethod
    def _get_json(url, params=None):
        return RESTaccess._parse_json(
            RESTaccess._get_raw(url, params)
        )

    @staticmethod
    def _parse_xml(raw):
        from xml.dom.minidom import parse
        dom = parse(raw)
        return XMLAccessor(dom)

    @staticmethod
    def _get_xml(url, params=None):
        return RESTaccess._parse_xml(
            RESTaccess._get_raw(url, params)
        )

    def __init__(self, rest_hub):
        self.rest_hub = rest_hub

    def __repr__(self):
        return 'RESTaccess(%r)' % self.rest_hub

    def url(self, endpoint):
        """ Gives the full url of the given endpoint """
        return '/'.join(
            (self.rest_hub.rstrip('/'), endpoint.lstrip('/'))).rstrip('/')

    def __call__(self, endpoint, params=None):
        """
        GETs the enpoint unless params is passed, in which case it POSTs params
        """
        url_ = self.url(endpoint)
        content = self._get_raw(url_, params)
        subtype = content.headers.subtype.lower().strip()
        assert isinstance(subtype, str)

        if subtype == 'json':
            return self._parse_json(content)
        elif subtype == 'xml':
            return self._parse_xml(content)
        else:
            return content
