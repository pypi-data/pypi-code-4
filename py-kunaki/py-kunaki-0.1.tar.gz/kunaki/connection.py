import urllib
import urlparse
import httplib


class Connection(object):
    """ Basic class to send requests to Kunaki XML Web service.
    """
    def __init__(self, url):
        url_scheme = urlparse.urlparse(url)
        self.scheme = url_scheme.scheme
        self.host = url_scheme.netloc
        self.port = url_scheme.port or (443 if self.scheme == 'https' else 80)
        self.path = url_scheme.path
        self.is_secure = self.scheme == 'https'

    def send_request(self, body, status=200, ctype='text/xml'):
        """ Sends a POST request to the connection host.
        Returns success status and response as a tuple.
        """
        headers = {
            'Host': '%s' % self.host,
            'Content-Type': ctype,
        }
        if isinstance(body, dict):
            body = urllib.urlencode(body)

        if self.is_secure:
            conn = httplib.HTTPSConnection(self.host, int(self.port))
        else:
            conn = httplib.HTTPConnection(self.host, int(self.port))

        conn.request('POST', self.path, body, headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        if res.status != status:
            msg = '%s - %s' % (res.status, res.reason)
            return False, msg

        return True, data
