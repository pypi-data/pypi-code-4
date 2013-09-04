import requests
import json
import sys
import time

from .auth import BasicAuth, OAuth2Auth, NullAuth
from .response import *
from .errors import RESTAPIError


class RESTClient(object):
    def __init__(self, endpoint='https://rest.dotcloud.com/v1',
            debug=False, user_agent=None, version_checker=None):
        self.endpoint = endpoint
        self.debug = debug
        self.authenticator = NullAuth()
        self._make_session()
        self._user_agent = user_agent
        self._version_checker = version_checker
        if self.debug:
            requests.packages.urllib3.connectionpool.HTTPSConnection.debuglevel = 1
            requests.packages.urllib3.connectionpool.HTTPConnection.debuglevel = 1

    def make_prefix_client(self, prefix=''):
        subclient = RESTClient(
                endpoint='{endpoint}{prefix}'.format(
                    endpoint=self.endpoint, prefix=prefix),
                debug=self.debug, user_agent=self._user_agent,
                version_checker=self._version_checker)
        subclient.session = self.session
        subclient.authenticator = self.authenticator
        return subclient

    def _make_session(self):
        headers = {'Accept': 'application/json'}
        hooks = {
            'response': self._response_hook
        }
        self.session = requests.session()
        self.session.headers = headers
        self.session.hooks = hooks
        self.session.auth = self._request_hook

    def _request_hook(self, request):
        if self._user_agent:
            request.headers['User-Agent'] = self._user_agent

        self.authenticator.pre_request_hook(request)
        if self.debug:
            print >>sys.stderr, '### {method} {url} data={data}'.format(
                method  = request.method,
                url     = request.path_url,
                data    = request.body
            )
        return request

    def _response_hook(self, response, **kw):
        r = self.authenticator.response_hook(self.session, response)
        if self.debug:
            print >>sys.stderr, '### {code} TraceID:{trace_id}'.format(
                code=response.status_code,
                trace_id=response.headers['X-DotCloud-TraceID'])
        return r

    def build_url(self, path):
        if path == '' or path.startswith('/'):
            return self.endpoint + path
        else:
            return path

    def request(self, method, path, streaming=False, **kw):
        url = self.build_url(path)
        kw = self.authenticator.args_hook(kw) or kw

        def do_request():
            return self.make_response(
                    self.session.request(
                        method, url, stream=streaming, **kw),
                    streaming
                    )

        for i in range(4):
            try:
                return do_request()
            except requests.exceptions.RequestException:
                time.sleep(1)
        return do_request()

    def get(self, path='', streaming=False):
        return self.request('GET', path, streaming, timeout=180)

    def post(self, path='', payload={}):
        return self.request('POST', path,
                            data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    def put(self, path='', payload={}):
        return self.request('PUT', path,
                            data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    def delete(self, path=''):
        return self.request('DELETE', path, headers={'Content-Length': '0'})

    def patch(self, path='', payload={}):
        return self.request('PATCH', path,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps(payload),
                            )

    def make_response(self, res, streaming=False):
        trace_id = res.headers.get('X-DotCloud-TraceID')
        if res.headers['Content-Type'] == 'application/json':
            pass
        elif res.status_code == requests.codes.no_content:
            return BaseResponse.create(res=res, trace_id=trace_id)
        else:
            raise RESTAPIError(code=requests.codes.server_error,
                               desc='Server responded with unsupported ' \
                                'media type: {0} (status: {1})' \
                                .format(res.headers['Content-Type'],
                                    res.status_code),
                               trace_id=trace_id)

        if res.status_code == requests.codes.im_a_teapot:
            # Maintenance mode
            message = 'The API is currently in maintenance mode.\n'\
            'Please try again later and check http://status.dotcloud.com '\
            'for more information.'
            if res.json['error']['description'] is not None:
                message = res.json['error']['description']
            raise RESTAPIError(code=requests.codes.im_a_teapot, desc=message)

        if not res.ok:
            data = json.loads(res.text)
            raise RESTAPIError(code=res.status_code,
                desc=data['error']['description'], trace_id=trace_id)

        if self._version_checker:
            self._version_checker(res.headers.get('X-DOTCLOUD-CLI-VERSION-MIN'),
                    res.headers.get('X-DOTCLOUD-CLI-VERSION-CUR'))

        return BaseResponse.create(res=res, trace_id=trace_id,
                streaming=streaming)
