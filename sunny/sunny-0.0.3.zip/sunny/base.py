from .compat import urljoin
from urllib3.connectionpool import connection_from_url
import json
import urllib


try:
    from orderedmultidict import omdict
    _omdict_support = True
except ImportError:
    _omdict_support = False


def normalize_params(params):
    """
    Normalize ``params`` to a list of key-value tuples.
    """
    if _omdict_support and isinstance(params, omdict):
        return params.allitems()
    elif isinstance(params, dict):
        res = []
        for k, v in params.iteritems():
            if isinstance(v, list):
                for x in v:
                    res.append((k, x))
            else:
                res.append((k, v))
        return res


class Solr(object):

    def __init__(self, url):
        self._http = connection_from_url(url)
        self.url = url
        if not self.url.endswith('/'):
            self.url += '/'

    def query(self, params, resource = 'select'):
        params['wt'] = 'json'
        params = normalize_params(params)
        query_string = urllib.urlencode(params, doseq=True)
        url = urljoin(self.url, resource)
        response = self._http.request('GET', url + '?' + query_string)
        return json.loads(response.data, 'utf-8')
