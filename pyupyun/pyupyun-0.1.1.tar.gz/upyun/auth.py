import datetime
import hashlib

from requests.auth import AuthBase


class UpYunDigestAuthentication(AuthBase):
    """UpYun signature digest authentication implemented for `requests`

    :param str user: Username
    :param str passwd: Password
    """
    AUTH_STR = 'UpYun'

    def __init__(self, user, passwd):
        self.user = user
        self.passwd_digest = hashlib.md5(passwd).hexdigest()

    def _get_content_length(self, r):
        cont_len = r.headers.get('content-length', None)
        if cont_len is not None:
            return int(cont_len)
        try:
            return len(r.body)
        except (AttributeError, TypeError):
            pass
        try:
            return len(r.data)
        except (AttributeError, TypeError):
            pass
        return 0

    def __call__(self, r):
        datetime_str = datetime.datetime.utcnow().strftime(
                '%a, %d %b %Y %H:%M:%S GMT')
        sign_base = '&'.join((r.method, r.path_url, datetime_str,
            str(self._get_content_length(r)), self.passwd_digest))
        sign = hashlib.md5(sign_base).hexdigest()
        r.headers['Date'] = datetime_str
        r.headers['Authorization'] = \
                self.AUTH_STR + ' ' + self.user + ':' + sign
        return r
