""" Accessors for REST endpoints """

from slacken.xml_accessor import XMLAccessor

__author__ = 'Alistair Broomhead'


class RESTaccess(object):
    """
    An accessor for REST endpoints

    rest_hub should be something like 'http://www.integration.moshi/services/rest'
    """
    rest_hub = ''

    @staticmethod
    def _get_raw(url, data=None, auth=None):
        kwargs = {}
        import requests
        get_rest_response = requests.get
        if auth is not None:
            kwargs['auth'] = auth
        if data is not None:
            kwargs['data'] = data
            get_rest_response = requests.post
        return get_rest_response(url, **kwargs)

    @staticmethod
    def _parse_json(raw):
        return raw.json()

    @staticmethod
    def _get_json(url, params=None, credentials=None):
        return RESTaccess._get_raw(url, params, credentials).json()

    @staticmethod
    def _parse_xml(response):
        from xml.dom.minidom import parseString
        dom = parseString(response.content)
        return XMLAccessor(dom)

    @staticmethod
    def _get_xml(url, params=None, credentials=None):
        return RESTaccess._parse_xml(
            RESTaccess._get_raw(url, params, credentials)
        )

    def __init__(self, rest_hub, username=None, password=None):
        self.rest_hub = rest_hub
        self._credentials = {}
        if username is not None:
            self._credentials["username"] = username
            if password is not None:
                self._credentials["password"] = password

    def __repr__(self):
        return 'RESTaccess(%r)' % self.rest_hub

    def url(self, endpoint):
        """ Gives the full url of the given endpoint """
        return '/'.join(
            (self.rest_hub.rstrip('/'), endpoint.lstrip('/'))).rstrip('/')

    def auth(self, username=None, password=None):
        if username is None:
            if "username" in self._credentials:
                username = self._credentials["username"]
            else:
                return None
        if password is None and "password" in self._credentials:
            password = self._credentials["password"]
        return username, password

    def __call__(self, endpoint, params=None, username=None, password=None):
        """
        GETs the enpoint unless params is passed, in which case it POSTs params
        """
        url_ = self.url(endpoint)
        credentials = self.auth(username=username, password=password)
        response = self._get_raw(url_, params, credentials)
        content_type = response.headers['content-type'].lower().strip()
        assert isinstance(content_type, str)

        if 'json' in content_type:
            return response.json()
        elif 'xml' in content_type:
            return self._parse_xml(response)
        else:
            return response.content
