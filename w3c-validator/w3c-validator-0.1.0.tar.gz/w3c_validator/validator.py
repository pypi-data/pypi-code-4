import requests


class Validator(object):
    VALIDATOR_URL = 'http://validator.w3.org/check'
    DEFAULT_OUTPUT = 'json'

    def _validate_get(self, params, headers=None):
        uri = self.VALIDATOR_URL
        if 'output' not in params:
            params['output'] = self.DEFAULT_OUTPUT

        resp = requests.get(uri, params=params, headers=headers)
        self._process_response

    def _validate_post(self, params, headers=None, files=None):
        uri = self.VALIDATOR_URL
        if 'output' not in params:
            params['output'] = self.DEFAULT_OUTPUT

        resp = requests.post(uri, data=params, files=files, headers=headers)
        self._process_response(resp)

    def _process_response(self, resp):
        self.errors = []
        self.warnings = []
        if 'json' in resp.headers['content-type']:
            self.type = 'json'
            self.content = resp.json()
            #print self.content
            for message in self.content.get('messages', []):
                if 'lastLine' in message:
                    i = message['lastLine']
                    message['src'] = self.source[i-1]
                if message['type'] == u'error':
                    self.errors.append(message)
                else:
                    self.warnings.append(message)
        else:
            self.type = 'html'
            self.content = resp.content

        self.error_count = int(resp.headers.get('x-w3c-validator-errors', '0'))
        self.warning_count = int(resp.headers.get('x-w3c-validator-warnings', '0'))
        self.status = resp.headers.get('x-w3c-validator-status', 'Invalid')

    def validate(self, uri):
        params = dict(uri=uri)
        return self._validate(params)

    def validate_file(self, file):
        return self._validate_post(dict(), files=dict(uploaded_file=(file)))

    def validate_source(self, source):
        self.source = source.split("\n")
        self._validate_post(dict(), files=dict(uploaded_file=('source.html', source)))

