import hashlib
import time

from requests.auth import AuthBase


class MasheryAuth(AuthBase):
    """
    Adds ``apikey`` and ``sig`` query parameters to the request
    """

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def __call__(self, r):
        params = {
            'apikey': self.key,
            'sig': self._sig(),
        }
        r.prepare_url(r.url, params)

        return r

    def _sig(self):
        timestamp = int(time.time())

        m = hashlib.md5()
        m.update(self.key)
        m.update(self.secret)
        m.update(str(timestamp))

        return m.hexdigest()
