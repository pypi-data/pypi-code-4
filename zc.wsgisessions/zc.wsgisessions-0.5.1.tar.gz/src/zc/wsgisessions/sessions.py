"""WSGI Sessions support."""

__docformat__ = 'reStructuredText'

import binascii
import hashlib
import hmac
import os
import string
import time
import transaction
import webob
import zope.component
import zope.interface
import zope.session.interfaces
import zope.session.session

from zc.wsgisessions.utils import boolean


def store(request, pkg_id, key, value):
    session = zope.session.interfaces.ISession(request)[pkg_id]
    session[key] = value


def get(request, pkg_id, key=None):
    adapter = zope.session.interfaces.ISession(request)
    if key is None:
        return adapter[pkg_id]
    return adapter.get(pkg_id, {}).get(key)


def remove(request, pkg_id, key):
    adapter = zope.session.interfaces.ISession(request)
    return adapter.get(pkg_id, {}).pop(key, None)


def rand(n=20):
    return binascii.hexlify(os.urandom(n))


class Session(zope.session.session.Session):

    def __init__(self, client_id, sdc):
        self.client_id = client_id
        self._data_container = sdc

    def _sdc(self, pkg_id):
        return self._data_container

    def __iter__(self):
        raise NotImplementedError


class BrowserIdFilter(object):

    db_name = 'sessions'
    http_only = True
    secure = False

    def __new__(cls, global_conf, **kw):
        def create(app):
            self = object.__new__(cls)
            self.app = app
            # db-name is passed in kw from a setting in .ini file
            self.db_name = kw.get('db-name', self.db_name)
            for setting in ('http-only', 'secure'):
                attr = setting.replace('-', '_')
                if setting in kw:
                    setattr(self, attr, boolean(kw[setting]))
                # for selenium testing set http_only in global_conf
                if setting in global_conf:
                    setattr(self, attr, boolean(global_conf[setting]))
            return self
        return create

    def __call__(self, environ, start_response):
        start_response = self.prepare(environ, start_response)
        return self.app(environ, start_response)

    def prepare(self, environ, start_response):
        # Look in the db for the cookie name and the secret:
        conn = environ['zodb.connection'].get_connection(self.db_name)
        root = conn.root()
        namespace, secret = root['browserid_info']
        added_headers = []
        sid = webob.Request(environ).cookies.get(namespace)
        if sid is not None:
            sid = self.verify(secret, sid)
        if sid is None:
            sid = self.generate(secret)
            cookie = '%s=%s; path=/' % (namespace, sid)
            if self.http_only:
                cookie += '; HttpOnly'
            if self.secure or environ['wsgi.url_scheme'] == 'https':
                cookie += '; secure'
            # XXX need to set expiration
            added_headers = [('Set-Cookie', cookie)]
            original_start_response = start_response
            def my_start_response(status, headers, exc_info=None):
                return original_start_response(
                    status, list(headers) + added_headers, exc_info)
            start_response = my_start_response
        environ['zc.wsgisessions.browserid'] = sid
        environ['zc.wsgisessions.session'] = Session(sid, root['sessions'])
        return start_response

    def generate(self, secret):
        data = '%s%.20f%.20f' % (rand(), time.time(), time.clock())
        digest = hashlib.sha1(data).digest()
        s = digestEncode(digest)
        # we store an HMAC of the random value together with it, which makes
        # our session ids unforgeable.
        mac = hmac.new(secret, s, digestmod=hashlib.sha1).digest()
        return s + digestEncode(mac)

    def verify(self, secret, sid):
        if (not sid) or len(sid) != 54:
            return None
        s, mac = sid[:27], sid[27:]

        if (digestEncode(hmac.new(
                secret, s.encode(), digestmod=hashlib.sha1
            ).digest()) != mac):
            return None
        else:
            return sid


cookieSafeTrans = string.maketrans('+/', '-.')


def digestEncode(s):
    """Encode SHA digest for cookie."""
    return s.encode('base64')[:-2].translate(cookieSafeTrans)


def initialize_database(database, *args, **kw):
    conn = database.open()
    db_name = kw.get('db_name', BrowserIdFilter.db_name)
    root = conn.get_connection(db_name).root()
    if 'browserid_info' not in root:
        if 'namespace' in kw:
            namespace = kw['namespace']
        else:
            namespace = 'browserid_%x' % (int(time.time()) - 1000000000)
        if 'secret' in kw:
            secret = kw['secret']
        else:
            secret = rand()
        root['browserid_info'] = (namespace, secret)
    if 'sessions' not in root:
        sdc = zope.session.session.PersistentSessionDataContainer()
        if 'timeout' in kw:
            sdc.timeout = kw['timeout']
        else:
            sdc.timeout = 24 * 60 * 60 # 1 day
        if 'resolution' in kw:
            sdc.resolution = kw['resolution']
        else:
            sdc.resolution  = 1 * 60 * 60 # 1 hour
        root['sessions'] = sdc
    transaction.commit()
    conn.close()


@zope.interface.implementer(zope.session.interfaces.ISession)
@zope.component.adapter(webob.Request)
def get_session(request):
    return request.environ['zc.wsgisessions.session']
