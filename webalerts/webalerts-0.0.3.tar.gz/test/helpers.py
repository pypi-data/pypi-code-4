import os

from mock import Mock
import yaml

from webalerts import Response, SiteException


def mock_function(d):
    def side_effect(*args):
        return d[args]
    return Mock(side_effect=side_effect)


class MockRequest(object):

    def __init__(self):
        self._base = None
        self._pages = {}
        self._flags = {}

    def from_yaml(self, name):
        self._base = os.path.abspath(os.path.dirname(name))
        with open(name) as f:
            config = yaml.load(f)
            for item in config:
                methods = item.get('method', 'get')
                if isinstance(methods, basestring):
                    methods = [methods]
                for method in methods:
                    key = method + ':' + item['url']
                    self._pages[key] = item

    def __call__(self, url, method='get', data=None):
        key = method + ':' + url
        if key not in self._pages:
            raise SiteException('unknown method and url: {0} {1}'.format(method, url))
        item = self._pages[key]
        if method == 'post' and 'set_flag' in item and includes(data, item.get('data')):
            self._flags[item['set_flag']] = True
        content = ''
        if 'response' in item:
            response = None
            if isinstance(item['response'], basestring):
                response = item['response']
            elif isinstance(item['response'], dict):
                responses = item['response']
                for flag in responses:
                    if self._flags.get(flag):
                        response = responses[flag]
                        break
                if not response:
                    response = responses['__default__']
            else:
                responses = item['response']
                i = item.get('_last_index', -1) + 1
                if i == len(responses):
                    raise SiteException('no more pages for: {0} {1}'.format(method, url))
                response = responses[i]
                item['_last_index'] = i
            if isinstance(response, basestring):
                with open(os.path.join(self._base, response)) as f:
                    content = f.read()
            elif isinstance(response, dict):
                if 'redirect' in response:
                    return self.__call__(response['redirect'])
                raise RuntimeError('response dict should have redirect')
            else:
                raise RuntimeError('response should be either string or dict')
        return Response(url, content, 200)


def includes(d1, d2):
    if d1 is None:
        return d2 is None
    return d2 is None or all(d1.get(k) == d2.get(k) for k in d2)
