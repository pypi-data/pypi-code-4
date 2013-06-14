from fanery import service, authorize, store
from fanery.terms import (
    hict, get_timestamp, is_string, is_string,
    parse_term, parse_json, to_json,
)
from fanery.crypto import gen_token, digest, encrypt, decrypt

class PyClient(object):

    def __init__(self):
        self.session = hict(token = None, sid = None)

    def call(self, urlpath, *args, **argd):
        return service.consume(urlpath, *args, **argd)

    def safe_call(self, urlpath, *args, **argd):
        session = self.session
        sid = session.sid
        key = session.token
        params = argd.pop('params', dict())
        enc_call = encrypt(key, [urlpath, args, argd])
        params.update(sid = sid, enc_call = enc_call)
        enc_ret = self.call('safe_call', **params)
        ret = decrypt(key, enc_ret)
        session.token = ret.token
        return parse_term(ret.data)

    def login(self, username, password, **argd):
        password = digest(password)
        tstamp = get_timestamp()
        nonce = gen_token()
        key = digest('%s%s%f' % (nonce, password, tstamp))
        msg = digest('%s%s%s' % (username, nonce, password))
        ret = self.call('login', username = username,
                                 nonce = nonce,
                                 tstamp = tstamp,
                                 enc_token = encrypt(key, msg),
                                 **argd)
        self.session.update(decrypt(key, ret))
        return True

    def logout(self):
        try:
            return self.safe_call('logout')
        finally:
            self.session.update(token = None, sid = None)

from fanery.wsgi import JSON_KEY, handler
from webob import Request

class WSGIClient(PyClient):

    def send(self, urlpath, **argd):
        req = Request.blank(urlpath, POST = {JSON_KEY: to_json(argd)})
        return req.get_response(handler)

    def call(self, urlpath, *args, **argd):
        path = '/'.join(['', urlpath, '/'.join(str(i) for i in args)])
        res = self.send(path, **argd)
        if res.status_code == 200:
            try:
                return parse_json(res.body)
            except:
                return res.body
        elif res.status_code == 400:
            try:
                error = parse_json(res.body)
                etype = getattr(store, error.type, None) or \
                        getattr(service, error.type, None) or \
                        getattr(authorize, error.type, None) or \
                        getattr(__builtins__, error.type, Exception)
                reason = error.reason
            except:
                raise Exception(res.body)
            if issubclass(etype, Exception):
                raise etype(*reason)
            else:
                raise Exception(*reason)
        else:
            raise Exception(res.body)

class HTTPClient(WSGIClient):

    def send(self, urlpath, **argd):
        raise NotImplementedError
