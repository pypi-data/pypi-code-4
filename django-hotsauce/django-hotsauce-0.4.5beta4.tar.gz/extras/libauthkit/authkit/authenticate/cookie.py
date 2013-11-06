#!/usr/bin/env python
"""Heavily modified cookie-based authentication module.

For documentation about this module see 'docs/signed_cookies.rst'.
Current status:
- Works for simple login 
- Buggy for logout
- Contains a few Paste artefacts
- Might require a revised get_cookies function
"""

from hashlib import md5
import os
import inspect
import types
import time
import logging
from Cookie import SimpleCookie, CookieError

from base import strip_base, swap_underscore
from base import AuthKitConfigError
from base import get_template

# Paste artefacts.
# XXX hidden ``request`` object is imported from here
from paste.deploy.converters import asbool
from auth_tkt import *

# Setting up logging
log = logging.getLogger('authkit.authenticate.cookie')
log.setLevel('DEBUG')

class AuthKitTicket(AuthTicket):
    """
    This is a standard paste ``AuthTicket`` class except that it also supports a
    ``cookie_params`` dictionary which can have the following options: ``expires``,
    ``path``, ``comment``, ``domain``, ``max-age``, ``secure`` and ``version``.

    .. note ::
    
        Unlike the paste version the ``secure`` option is set as a cookie
        parameter, not on its own.

    The cookie parameters are described in the AuthKit manual under the 
    cookie section.
    """

    def __init__(
        self, 
        secret, 
        userid, 
        ip, 
        tokens=(), 
        user_data=None, 
        time=None, 
        cookie_name='authkit', 
        cookie_params=None,
        nouserincookie=False,
        ):
        #log.debug('yay in AuthKitTicket!')

        self.nouserincookie = nouserincookie
        secure = False
        if cookie_params is None:
            self.cookie_params = {}
        else:
            # This is a bit of a hack to keep the API consistent with the base
            # class
            if cookie_params.has_key('secure'):
                secure = asbool(cookie_params.get('secure',False))
                self.cookie_params = {}
                for k, v in cookie_params.items():
                    if k != 'secure':
                        self.cookie_params[k] = v
            else:
                self.cookie_params = cookie_params.copy()
        AuthTicket.__init__(self, secret, userid, ip, tokens=tokens, 
                            user_data=user_data, time=time, 
                            cookie_name=cookie_name, secure=secure)

    def digest(self):
        digest_ = calculate_digest(self.ip, self.time, self.secret, 
                                   self.userid, self.tokens, self.user_data)
        log.debug(
            "Calculating the digest ip %r, time %r, secret %r, userid %r, "
            "tokens %r, user_data %r, digest %r", self.ip, self.time, 
            self.secret, self.userid, self.tokens, self.user_data, digest_)
        return digest_

    def cookie_value(self):
        if not self.nouserincookie:
            v = '%s%08x%s!' % (self.digest(), int(self.time), self.userid)
        else:
            v = '%s%08x!' % (self.digest(), int(self.time))
            
        if self.tokens:
            v += self.tokens + '!'
        if not self.nouserincookie:
            v += self.user_data
        return v

    def cookie(self):
        #log.debug('in cookie method')

        c = Cookie.SimpleCookie()
        # XXX There is is a bug in the base class implementation fixed here
        c[self.cookie_name] = self.cookie_value().strip().replace('\n', '')
        for k, v in self.cookie_params.items():
            if k not in ['path', 'expires']:
                c[self.cookie_name][k] = v
        # path and secure are handled differently to keep it consistent with
        # the base class API
        if not self.cookie_params.has_key('path'):
            c[self.cookie_name]['path'] = '/'
        else:
            c[self.cookie_name]['path'] = self.cookie_params['path']
        if self.cookie_params.has_key('expires'):
            time = Cookie._getdate(float(self.cookie_params['expires']))
            log.info(time)
            c[self.cookie_name]['expires'] = time
        if self.secure:
            c[self.cookie_name]['secure'] = 'true'
        return c
        
# The other methods in the paste file, calculate_digest and encode_ip_timestamp
# are utility methods which you shouldn't need to use on their own.

def parse_ticket(secret, ticket, ip, session):
    """
    Parse the ticket, returning (timestamp, userid, tokens, user_data).

    If the ticket cannot be parsed, ``BadTicket`` will be raised with
    an explanation.
    """
    log.debug("parse_ticket(secret=%r, ticket=%r, ip=%r)", secret, ticket, ip)
    ticket = ticket.strip('"')
    digest = ticket[:32]
    try:
        timestamp = int(ticket[32:40], 16)
    except ValueError, e:
        raise BadTicket('Timestamp is not a hex integer: %s' % e)

    user_data = None
    if session is not None:
        if not session.has_key('authkit.cookie.user'):
            raise BadTicket('No authkit.cookie.user key exists in the session')
        if not session.has_key('authkit.cookie.user_data'):
            raise BadTicket('No authkit.cookie.user_data key exists in the session')
        userid = session['authkit.cookie.user']
        user_data = session['authkit.cookie.user_data']
        data = ticket[40:]
    else:
        try:
            userid, data = ticket[40:].split('!', 1)
        except ValueError:
            raise BadTicket('userid is not followed by !')
    if '!' in data:
        tokens, new_user_data = data.split('!', 1)
        if user_data is None:
            user_data = new_user_data
    else:
        # @@: Is this the right order?
        tokens = ''
        if user_data is None:
            user_data = data
    
    expected = calculate_digest(ip, timestamp, secret, userid, tokens, 
                                user_data)
    
    if expected != digest:
        raise BadTicket('Digest signature is not correct',
                        expected=(expected, digest))
    
    tokens = tokens.split(',')
    
    return (timestamp, userid, tokens, user_data)
    
def calculate_digest(ip, timestamp, secret, userid, tokens, user_data):
    log.debug(
        "calculate_digest(ip=%r, timestamp=%r, secret=%r, userid=%r, "
        "tokens=%r, user_data=%r)", ip, timestamp, secret, userid, tokens, 
        user_data)
    digest0 = md5(encode_ip_timestamp(ip, timestamp) + secret
                      + userid.encode("utf-8")
                      + '\0' + tokens + '\0' + user_data).hexdigest()
    digest = md5(digest0 + secret).hexdigest()
    return digest

def encode_ip_timestamp(ip, timestamp):
    log.debug("encode_ip_timestamp(ip=%r, timestamp=%r)", ip, timestamp)
    ip_chars = ''.join(map(chr, map(int, ip.split('.'))))
    t = int(timestamp)
    ts = ((t & 0xff000000) >> 24, (t & 0xff0000) >> 16, (t & 0xff00) >> 8,
          t & 0xff)
    ts_chars = ''.join(map(chr, ts))
    return ip_chars + ts_chars

#
# Custom AuthKitCookieMiddleware
#

class CookieUserSetter(AuthTKTMiddleware):
    
    """
    Same as paste's ``AuthTKTMiddleware`` except you can choose your own ticket
    class and your cookie is removed if there is a bad ticket. 
    
    Also features server-side cookie expiration and IP-based cookies which use the correct 
    IP address when a proxy server is used.

    The options are all described in detail in the cookie options part of the 
    main AuthKit manual.
    """

    def __init__(self, 
        app, 
        secret, 
        name='authkit', 
        params=None,   
        includeip=True,
        signoutpath=None, 
        enforce=False, 
        ticket_class=AuthKitTicket, 
        nouserincookie=False,
        session_middleware='beaker.session',
        badcookie=False,
        badcookie_template=None,
        secure=False
        ):
        #log.debug("Setting up the cookie middleware")
        #secure = False
        #if params.has_key('secure') and asbool(params['secure']) == True:
        #    secure = True
        # secure not needed!
        super(CookieUserSetter, self).__init__(app, secret, cookie_name=name, 
                                   secure=secure, include_ip=asbool(includeip),
                                   logout_path=signoutpath)
        print 'in CookieUserSetter!'
        self.ticket_class = ticket_class
        self.cookie_params = params and params.copy() or {}
        self.cookie_enforce = enforce
        if self.cookie_enforce and not self.cookie_params.has_key('expires'):
            raise AuthKitConfigError(
                "Cannot enforce cookie expiration since no "
                "cookie_params expires' has been set"
            )

        self.nouserincookie = nouserincookie
        self.session_middleware = session_middleware
        self.badcookie_page=badcookie
        if self.badcookie_page and not badcookie_template:
            raise AuthKitConfigError(
                "No badcookie.template option was specified for the cookie middleware"
            )
        self.badcookie_template = badcookie_template

    def __call__(self, environ, start_response):
        session = None
        if self.nouserincookie:
            session = environ[self.session_middleware]
            log.debug("Activating session object: %r" % session)
        import pdb; pdb.set_trace()
        cookies = self.get_cookies(environ)

        log.debug("These cookies were found: %s", cookies.keys())
        if self.cookie_name in cookies:
            cookie_value = cookies[self.cookie_name].value
        else:
            cookie_value = ''
        log.debug("Our cookie %r value is therefore %r", self.cookie_name, 
                  cookie_value)
        remote_addr = environ.get('HTTP_X_FORWARDED_FOR', 
                                  environ.get('REMOTE_ADDR','0.0.0.0'))
        remote_addr = remote_addr.split(',')[0]
        log.debug("Remote addr %r, value %r, include_ip %r", remote_addr, 
                  cookie_value, self.include_ip)
        if cookie_value:
            if self.include_ip:
                pass
            else:
                # mod_auth_tkt uses this dummy value when IP is not
                # checked:
                remote_addr = '0.0.0.0'
            try:
                log.debug("Parsing ticket secret %r, cookie value %r, "
                          "remote address %s", self.secret, cookie_value, 
                          remote_addr)
                timestamp, userid, tokens, user_data = \
                    parse_ticket(self.secret, cookie_value, remote_addr, session)
            except BadTicket, e:
                if e.expected:
                    log.warning("BadTicket: %s Expected: %s", e, e.expected)
                else:
                    log.warning("BadTicket: %s", e)
                environ['authkit.cookie.error'] = True
            else:
                now = time.time()
                log.debug("Cookie enforce: %s", self.cookie_enforce)
                log.debug("Time difference: %s", str(now-timestamp))
                log.debug("Cookie params expire: %s", 
                          self.cookie_params.get('expires'))
                if self.cookie_enforce and now - timestamp > \
                   float(self.cookie_params['expires']) + 1:
                   environ['authkit.cookie.error'] = True
                   environ['authkit.cookie.timeout'] = True
                else:
                    environ['paste.auth_tkt.timestamp'] = timestamp
            # End changes from the default
            if environ.get('authkit.cookie.badcookie', False) and self.badcookiepage:
                def bad_cookie_app(environ, start_response):
                    # If we are using optional session support remove the user from the session:
                    if self.nouserincookie:
                        environ[self.session_middleware]['authkit.cookie.user'] = None
                        del environ[self.session_middleware]['authkit.cookie.user']
                        environ[self.session_middleware]['authkit.cookie.user_data'] = None
                        del environ[self.session_middleware]['authkit.cookie.user_data']
                        environ[self.session_middleware].save()
                    # Now show the bad cookie screen:
                    headers = self.logout_user_cookie(environ) 
                    headers.append(('Content-type','text/html')) 
                    start_response('200 OK', headers) 
                    # Inspect the function to see if we can pass it anything useful:
                    args = {}
                    kargs = {'environ':environ}
                    #Commented out because of obscure purposes.
                    #if environ.has_key('gi.state'):
                    #    kargs['state'] = environ['gi.state']
                    for name in inspect.getargspec(self.badcookietemplate)[0]:
                        if kargs.has_key(name):
                            args[name] = kargs[name]
                    response = self.badcookietemplate(**args)
                    return [response]
                return bad_cookie_app(environ, start_response)
            elif not environ.get('authkit.cookie.error', False):
                environ['REMOTE_USER'] = userid
                if environ.get('REMOTE_USER_TOKENS'):
                    # We want to add tokens/roles to what's there:
                    tokens = environ['REMOTE_USER_TOKENS'] + tokens
                environ['REMOTE_USER_TOKENS'] = tokens
                environ['REMOTE_USER_DATA'] = user_data
                environ['AUTH_TYPE'] = 'cookie'
            # Remove REMOTE_USER set by any other application.
            elif environ.has_key('REMOTE_USER'):
                log.warning('Removing the existing REMOTE_USER key because of a bad cookie')
                del environ['REMOTE_USER']
        set_cookies = []
        log.debug(set_cookies)
        
        def set_user(userid, tokens='', user_data=''):
            set_cookies.extend(self.set_user_cookie(environ, userid, tokens, user_data))
        
        def logout_user():
            set_cookies.extend(self.logout_user_cookie(environ))
        
        environ['authkit.set_user'] = set_user
        environ['authkit.logout_user'] = logout_user
        if (self.logout_path and environ.get('PATH_INFO') == self.logout_path) \
            or environ.get('authkit.cookie.error', False):
            logout_user()
        
        def cookie_setting_start_response(status, headers, exc_info=None):
            headers.extend(set_cookies)
            # convert headers to string values if necessary, to ensure
            # WSGI 1.0 compat
            headers = [(k, str(v)) for (k, v) in headers]
            return start_response(status, headers, exc_info)
        return self.app(environ, cookie_setting_start_response)


    def get_cookies(self, environ):
        """
        *From Paste.request*
        
        Gets a cookie object (which is a dictionary-like object) from the
        request environment; caches this value in case get_cookies is
        called again for the same request.

        """
        header = environ.get('HTTP_COOKIE', '')
        if environ.has_key('paste.cookies'):
            cookies, check_header = environ['paste.cookies']
            if check_header == header:
                return cookies
        cookies = SimpleCookie()
        try:
            cookies.load(header)
        except CookieError:
            pass
        environ['paste.cookies'] = (cookies, header)
        return cookies

       #
# This method uses our new cookie
#

    def set_user_cookie(self, environ, userid, tokens, user_data):
        default_remote_addr = '0.0.0.0'
        
        if self.include_ip:
            # Provide a sane fallback if REMOTE_ADDR was not found in the 
            # environ dict.
            try:
                remote_addr = environ.get('HTTP_X_FORWARDED_FOR', environ['REMOTE_ADDR'])
                remote_addr = remote_addr.split(',')[0]
            except KeyError:
                remote_addr = default_remote_addr

        # Only these three lines change
        #~ if self.secure != self.cookie_params.get('secure', False) and asbool(self.cookie_params['secure']) or False:
            #~ raise Exception('The secure option has changed before '
                #~ 'we got here. This means the base class has changed '
                #~ 'since this class was written. %r %r'%self.secure, )
        ticket = self.ticket_class(self.secret, userid, remote_addr, 
                                   tokens=tokens, user_data=user_data, 
                                   cookie_name=self.cookie_name, 
                                   cookie_params=self.cookie_params, 
                                   nouserincookie=self.nouserincookie)
        
        # @@: Should we set REMOTE_USER etc in the current
        # environment right now as well?
        parts = str(ticket.cookie()).split(':')
        cookies = [(parts[0].strip(), ':'.join(parts[1:]).strip())]
        log.debug(cookies)
        if self.nouserincookie:
            if self.cookie_name == environ[self.session_middleware].key:
                raise AuthKitConfigError(
                    "The session cookie name %r is the same as the "
                    "AuthKit cookie name. Please change the session cookie "
                    "name."%(
                        environ[self.session_middleware].key
                    )
                )
            environ[self.session_middleware]['authkit.cookie.user'] = userid
            environ[self.session_middleware]['authkit.cookie.user_data'] = user_data
            
            #
            environ[self.session_middleware].save()
        
        return cookies
        
    def logout_user_cookie(self, environ):
        if self.nouserincookie:
            environ[self.session_middleware]['authkit.cookie.user'] = None
            del environ[self.session_middleware]['authkit.cookie.user']
            environ[self.session_middleware]['authkit.cookie.user_data'] = None
            del environ[self.session_middleware]['authkit.cookie.user_data']
            environ[self.session_middleware].save()
        domain = self.cookie_params.get('domain')
        path = self.cookie_params.get('path', '/')
        if not domain:
            cookies = [('Set-Cookie', '%s=""; Path=%s' % (self.cookie_name, 
                                                          path))]
        else:
            cookies = [('Set-Cookie', '%s=""; Path=%s; Domain=%s' % 
                       (self.cookie_name, path, domain))]
        return cookies

def _setup_cookie_conf(auth_conf, prefix='authkit.cookie.'):
    result = {}
    for k,v in auth_conf.items():
        if not (k.startswith(prefix) \
        or k.startswith('params.') \
        or k.startswith('badcookie.')):
            #print 'adding %r' % k
            result[k] = v
    return result

def load_cookie_config(
    app, 
    auth_conf, 
    app_conf=None, 
    global_conf=None, 
    prefix='authkit.cookie.'
    ):

    badcookie_conf = strip_base(auth_conf, 'badcookie.')
    template_conf = strip_base(badcookie_conf, 'template.')
    user_setter_params = {
        'params':  strip_base(auth_conf, 'params.'),
        'ticket_class':AuthKitTicket,
    }
    user_setter_params.update(_setup_cookie_conf(auth_conf, prefix))

    #if not 'secret' in user_setter_params:
    #    k = "%s" % (prefix+'secret')
    #    user_setter_params[k] = auth_conf[k]
    #    log.debug('fixed internal cookie secret bug!')
    #    raise AuthKitConfigError(
    #        'No cookie secret specified under %r'% (prefix+'secret')
    #    )
    if user_setter_params.has_key('signout'):
        raise AuthKitConfigError(
            'The authkit.cookie.signout option should now be named signoutpath'
        )
    return app, None, user_setter_params

def make_cookie_user_setter(
    app, 
    auth_conf, 
    app_conf=None, 
    global_conf=None, 
    prefix='authkit.cookie.'
    ):
    app, auth_handler_params, user_setter_params = load_cookie_config(
        app, 
        auth_conf, 
        app_conf=None, 
        global_conf=None, 
        prefix='authkit.cookie.'
    )
    params = _setup_cookie_conf(auth_conf, prefix='authkit.')
    #log.debug(params)
    return CookieUserSetter(app, **params)

# Backwards compatibility
make_cookie_handler = make_cookie_user_setter
AuthKitCookieMiddleware = CookieUserSetter

