# -*- coding: utf-8 -*-
"""This implementation is based on the ``wc.cookiecredentials`` package
from Philipp von Weitershausen.
"""

import base64
import urllib
import grokcore.component as grok
from dolmen.app.authentication import MF as _
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.pluggableauth.interfaces import ICredentialsPlugin
from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from zope.publisher.interfaces.http import IHTTPRequest


class ICookieCredentials(Interface):
    """A Credentials Plugin based on cookies.
    """
    cookie_name = ASCIILine(
        title=_(u'Cookie name'),
        description=_(u'Name of the cookie for storing credentials.'),
        required=True)


class CookiesCredentials(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.name('cookies')
    grok.provides(ICredentialsPlugin)
    grok.implements(ICredentialsPlugin, ICookieCredentials)

    # ILocation's information
    __parent__ = None

    # Required by zope.pluggableauth's IBrowserFormChallenger
    loginpagename = u'login'
    loginfield = u'login'
    passwordfield = u'password'

    # Required by zope.pluggableauth's ICredentialsPlugin
    challengeProtocol = None
    cookie_name = 'dolmen.authcookie'

    @staticmethod
    def make_cookie(login, password):
        credstr = u'%s:%s' % (login, password)
        val = base64.encodestring(credstr.encode('utf-8'))
        return urllib.quote(val)

    def extractCredentials(self, request):
        if not IHTTPRequest.providedBy(request):
            return

        login = request.get(self.loginfield, None)
        password = request.get(self.passwordfield, None)
        cookie = request.get(self.cookie_name, None)

        if login and password:
            cookie = self.make_cookie(login, password)
            request.response.setCookie(self.cookie_name, cookie, path='/')
        elif cookie:
            val = base64.decodestring(urllib.unquote(cookie)).decode('utf-8')
            login, password = val.split(':')
        else:
            return

        return {'login': login, 'password': password}

    def logout(self, request):
        if not IHTTPRequest.providedBy(request):
            return
        request.response.expireCookie(self.cookie_name, path='/')
