import base64
import re
import requests
import urllib


RESPONSE_SUCCESS_EXPRESSION = re.compile(r'<response\s+status="OK"\s*/>')


class CacheFlyError(Exception):
    """CacheFly communications error.
    """

    pass


class Client(object):
    """CacheFly CDN client.
    """

    def __init__(self, api_key):
        """Initialize a CacheFly CDN purging client.

        :param api_key: API key.
        """

        self.api_key = api_key

        self._session = requests.Session()

    def _request(self, endpoint_method, method, data=None):
        """Perform a request.

        :param endpoint_method: Endpoint method such as ``purge.purge.file``.
        :param method: Request method.
        :param data: Optional form data as a :class:`dict`.
        """

        # Perform the request.
        response = self._session.request(
            method,
            'http://api.cachefly.com/1.0/%s' % (endpoint_method),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            } if data else {},
            auth=(self.api_key, ''),
            data=urllib.urlencode(data)
        )

        # Check the status code.
        try:
            response.raise_for_status()
        except:
            raise CacheFlyError('unexpected response code %d: %s' %
                                (response.status_code, response.text))

        # Check the response.
        if not RESPONSE_SUCCESS_EXPRESSION.search(response.text):
            raise CacheFlyError('unexpected response from CacheFly: %s' %
                                (response.text))

    def purge(self, *files):
        """Purge one or more resources from the CDN.

        :param \*files: File paths.
        """

        if not files:
            return

        self._request('purge.purge.file', 'POST', {
            'files': ','.join([base64.b64encode(f.encode('utf-8'))
                               for f in files]),
        })

    def purge_all(self, *files):
        """Purge all resources from the CDN.
        """

        self._request('purge.purge.all', 'GET')


__all__ = (
    'Client',
    'CacheFlyError',
)
