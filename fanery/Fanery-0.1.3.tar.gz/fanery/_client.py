from time import time as timestamp
from os.path import splitext
from webob import Request
import requests

from _term import parse_term, parse_json, to_simple, to_json
from _crypto import AES, hmac, gen_token
from _auth import State
from _service import consume
from _wsgi import handler as wsgi_app

class PyClient(object):

    def __init__(self):
        self.__state = State()

    def _consume(self, urlpath, **argd):
        _, ext, ret = consume(self.__state, urlpath, **argd)
        return ext, ret

    def call(self, urlpath, **argd):
        ext, ret = self._consume(urlpath, **argd)
        return parse_json(ret) if ext == '.json' else ret

    def safe_call(self, urlpath, **argd):
        state = self.__state
        sid, token = str(state.sid), state.token
        params = to_json(to_simple(argd))
        sign = hmac(token, params)
        aes = AES(token)
        enc = aes.encrypt('|'.join((sign, params)))
        enc_ret = self.call(urlpath, enc = '|'.join((sid, enc)))
        ret = aes.decrypt(enc_ret)
        sign, new_token, json = ret.split('|', 2)
        assert sign == hmac(token, '|'.join((new_token, sid, json))), \
                ('bad-signature', sid)
        state.update(token = new_token)
        return parse_term(parse_json(json))

    def login(self, login, password, force = False, **extra):
        nonce = gen_token()[:8]
        token = gen_token()
        data = '%s|%s|%s' % (int(timestamp()), nonce, token)
        enc = AES(nonce + password).encrypt(data)
        enc_ret = self.call('login.json',
                uid = login, nonce = nonce, enc = enc,
                force = force, **extra)
        ret = AES(token).decrypt(enc_ret)
        self.__state.update(parse_term(parse_json(ret)))
        return True

    def logout(self):
        return self.safe_call('logout.json')

class WsgiClient(PyClient):

    def _consume(self, urlpath, **argd):
        _, ext = splitext(urlpath)
        if argd:
            params = dict((k, (v.name, v) if isinstance(v, file) else v)
                          for k, v in argd.iteritems())
            req = Request.blank(urlpath, POST = params)
        else:
            req = Request.blank(urlpath)
        #req.charset = 'utf8'
        res = req.get_response(wsgi_app)
        return ext, res.body

class HttpClient(PyClient):

    def __init__(self, baseurl = 'http://127.0.0.1:9000'):
        super(HttpClient, self).__init__()
        self.__baseurl = baseurl

    def _consume(self, urlpath, **argd):
        url = '/'.join((self.__baseurl, urlpath))
        _, ext = splitext(url)
        if argd:
            data, files = dict(), dict()
            for k, v in argd.iteritems():
                if isinstance(v, file):
                    files[k] = v
                else:
                    data[k] = v
            res = requests.post(url, files=files, data=data)
        else:
            res = requests.get(url)
        return ext, res.text

if __name__ == '__main__':
    client = PyClient()
    client.login('admin', 'admin')
