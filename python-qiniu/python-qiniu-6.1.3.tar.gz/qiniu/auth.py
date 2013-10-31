#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2013-10-12
@author: shell.xu
'''
import time, hmac, json
from base64 import urlsafe_b64encode
from hashlib import sha1
from urlparse import urlparse
from cStringIO import StringIO
from http import file_source

def gensha1(s):
    h = sha1()
    h.update(s)
    return h.digest()

def qetag(s):
    l = [gensha1(block) for block in file_source(s, 4 * 1024 * 1024)]
    if len(l) == 1: return urlsafe_b64encode('\x16' + l[0])
    return urlsafe_b64encode('\x96' + gensha1(''.join(l)))

def qetags(s):
    return qetag(StringIO(s))

class Mac(object):

    def __init__(self, access, secret):
        self.access, self.secret = access, secret

    def _sign(self, data):
        hashed = hmac.new(self.secret, data, sha1)
        return urlsafe_b64encode(hashed.digest())

    def sign(self, data):
        return '%s:%s' % (self.access, self._sign(data))

    def sign_data(self, b):
        data = urlsafe_b64encode(b)
        return '%s:%s:%s' % (self.access, self._sign(data), data)

    def sign_req(self, req):
        u = urlparse(req.uri)
        data = u.path
        if u.query:
            data += '?' + u.query
        data += '\n'
        if req.body and \
                req.get_header('Content-Type') == "application/x-www-form-urlencoded":
            data += req.body
        req.set_header('Authorization', 'QBox %s:%s' % (self.access, self._sign(data)))

    def put_token(self, scope=None, expires=3600, token=None):
        if token is None: token = {}
        token.update({'scope': scope, 'deadline': int(time.time()) + expires})
        b = json.dumps(token, separators=(',',':'))
        return self.sign_data(b)

    def get_url(self, url, expires=3600):
        if '?' in url: url += '&'
        else: url += '?'
        url += 'e=%s' % str(int(time.time()) + expires)
        return url + '&token=%s' % self.sign(url)

import conf
if conf.getcfg('keys', 'access_key') and conf.getcfg('keys', 'secret_key'):
    MAC = Mac(conf.getcfg('keys', 'access_key'), conf.getcfg('keys', 'secret_key'))
