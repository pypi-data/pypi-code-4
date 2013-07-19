#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

backends = ['redis', 'memcached', 'json', 'pickle']  # Supported backends.
import hashlib
import os

try:
    import memcache
except ImportError:
    memcache = False
try:
    import redis
except ImportError:
    redis = False

from . import jsonr
from . import pickler


class Cache:
    def __init__(self, **kw):
        print kw['backend']
        if 'backend' in kw:
            self.type = kw['backend'].lower()
        else:
            self.type = guess_backend()
        host = kw.get('host', '127.0.0.1')
        filename = kw.get('filename', 'cache')
        self.prefix = hashlib.md5(os.environ['USER']).hexdigest() + kw.get('prefix', '')
        if self.type in ['memcache', 'memcached']:
            if not memcache:
                raise ImportError
            self.backend = memcache.Client([host])
        elif self.type == 'redis':
            if not redis:
                raise ImportError
            port = kw.get('port', 6379)  # Default redis port
            self.backend = redis.StrictRedis(host=host, port=port)
        elif self.type == 'pickle':
            self.backend = pickler.Pickler(filename)
        elif self.type == 'json':
            self.backend = jsonr.JSON(filename)
        if not hasattr(self, 'backend'):
            raise ValueError("You must provide a supported backend.")

    def __repr__(self):
        return "Cache(backend={0})".format(self.type)

    def normalize_key(self, key):
        return self.prefix + key

    def set(self, key, value, *args):
        key = self.normalize_key(key)
        self.backend.set(key, value, *args)

    def get(self, key):
        key = self.normalize_key(key)
        return self.backend.get(key)

    def delete(self, key):
        key = self.normalize_key(key)
        self.backend.delete(key)

    def __contains__(self, key):
        """
        Not all backends will have a __contains__
        method, so we might need to improvise.
        """
        key = self.normalize_key(key)
        if hasattr(self.backend, '__contains__'):
            return key in self.backend

        try:
            value = self.get(key)
            if value is None:
                #Some backends like memcached do this.
                return False
        except KeyError:
            return False

        return True


def test_backend(c):
    """
    Simple function to test if a backend is operational.
    This is not intended to replace unit tests, but can be run
    quickly when needing to pick a backend.
    """
    c.set('test', '123')
    working = c.get('test') == '123'
    if working:
        c.delete('test')  # Cleanup
    return working


def guess_backend(order=None):
    """
    Function to guess which backend to use.

    Does basic verification that we can use that specific
    backend and that it actually works.
    """
    if not order:
        order = ['redis', 'memcache', 'pickle', 'json']

    for backend in order:
        try:
            c = Cache(backend=backend)
        except ImportError:
            continue
        if test_backend(c):
            return backend


