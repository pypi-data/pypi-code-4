import requests
import os
import json
try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3

TornadoAsyncHTTPClient = None
TornadoHTTPResponse = None
try:
    from tornado.httpclient import AsyncHTTPClient as TornadoAsyncHTTPClient
    from tornado.httpclient import HTTPResponse as TornadoHTTPResponse
except ImportError:
    TornadoAsyncHTTPClient = None
    TornadoHTTPResponse = None


class Email(object):
    """Mailgun Email Validation
    https://api.mailgun.net/v2/address
    http://mailgun.github.io/validator-demo/
    """
    def __init__(self, email, validate=True, key=None, httpclient=None, callback=None):
        """
        :validate: boolean
            Validate the email
        :key: string
            Mailgun api key
        """
        self._key = key or os.environ.get("MAILGUN_API_KEY",
                                          "pubkey-5ogiflzbnjrljiky49qxsiozqef5jxp7")
        self._callback = callback
        self._valid = not validate
        self._suggestion = None
        self._domain = None
        self._email = email

        if validate:
            self._validate_request(email=email,
                                   httpclient=httpclient,
                                   callback=self._validation_callback)

    @property
    def valid(self):
        return self._valid

    @property
    def suggestion(self):
        return self._suggestion

    @property
    def email(self):
        return self._email

    @property
    def domain(self):
        return self._domain

    def __str__(self):
        return self._email

    def __nonzero__(self):
        return self._valid

    def _validate_request(self, email, httpclient, callback):
        if not httpclient:
            check = requests.get("https://api.mailgun.net/v2/address/validate",
                                 params={'address': email},
                                 auth=('api', self._key))
            callback(check.json())

        elif isinstance(httpclient, TornadoAsyncHTTPClient):
            httpclient.fetch("https://api.mailgun.net/v2/address/validate?" + urlencode({'address': email}),
                             method="GET",
                             callback=callback,
                             auth_username="api",
                             auth_password=self._key)
            
    def _validation_callback(self, data):
        if isinstance(data, TornadoHTTPResponse):
            data = json.loads(data.body)
        self._valid = data['is_valid']
        self._suggestion = data['did_you_mean']
        self._domain = data['parts']['domain']
        self._email = data['address']

        if self._callback:
            self._callback(self)
