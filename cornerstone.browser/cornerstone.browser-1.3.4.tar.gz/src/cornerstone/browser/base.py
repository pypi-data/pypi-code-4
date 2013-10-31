#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

import types
import urllib

from urlparse import urlsplit

from sets import Set

from zope.interface import implements
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError

from AccessControl import getSecurityManager

from Products.Five import BrowserView
from ZTUtils import make_query

from interfaces import REQUEST, COOKIE, SESSION
from interfaces import ICookiePrefix
from interfaces import IRequestMixin
from interfaces import IRequestDefaultValues
from interfaces import IAjaxMixin

from tmpl import HTMLRendererMixin

EMPTYMARKER = []

class CookiePrefix(object):

    implements(ICookiePrefix)

    def __init__(self, context):
        self.context = context

    @property
    def prefix(self):
        prefix = getSecurityManager().getUser().getId()
        if not prefix:
            prefix = 'anonymoususer'
        return prefix

class RequestMixin(object):
    """IRequestMixin implementation.
    """

    implements(IRequestMixin)

    nameprefix = None
    checkboxpostfix = 'cb'

    def writeFormData(self, additionals=None, ignores=None,
                      considerexisting=False, considerspecific=None,
                      nameprefix=False, checkboxes=[], writechain=(COOKIE,)):
        params = self._chaindata(additionals, ignores, considerexisting,
                                 considerspecific, nameprefix, chain=chain)
        # TODO

    def makeUrl(self, context=None, url=None, resource=None, query=None):
        if url and context:
            raise ValueError, 'Need either context or url, both was given.'
        if context:
            url = context.absolute_url()
        if not url:
            url = self.context.absolute_url()
        if resource:
            url = '%s/%s' % (url, resource)
        if query:
            url = '%s?%s' % (url, query)
        return url

    def makeQuery(self, additionals=None, ignores=None, considerexisting=False,
                  considerspecific=None, nameprefix=False, chain=(REQUEST,)):
        params = self._chaindata(additionals, ignores, considerexisting,
                                 considerspecific, nameprefix, chain=chain)
        return make_query(params)

    def formvalue(self, name, default=None, checkbox=False, nameprefix=False):
        if checkbox:
            value = self.formvalue(name, default, nameprefix=nameprefix)
            if value:
                if isinstance(value, basestring):
                    return urllib.unquote(value)
                return value
            cbname = '%s_%s' % (name, self.checkboxpostfix)
            cb = self.formvalue(cbname, default, nameprefix=nameprefix)
            if cb:
                return False
            return default
        value = self.request.form.get(self._name(name, nameprefix), default)
        if isinstance(value, basestring):
            return urllib.unquote(value)
        return value

    def cookievalue(self, name, default=None, nameprefix=False):
        return self.request.cookies.get(self._cookiename(name, nameprefix),
                                        default)

    def sessionvalue(self, name, default=None, nameprefix=False):
        session = self.context.session_data_manager.getSessionData(create=False)
        if not session:
            return default
        return session.get(self._name(name, nameprefix), default)

    def requestvalue(self, name, default=None, checkbox=False,
                     chain=(REQUEST, COOKIE), nameprefix=False):
        return self._valuefromchain(chain, name, nameprefix, default, checkbox)

    def xrequestvalue(self, name, default=None, checkbox=False,
                      chain=(REQUEST, COOKIE), nameprefix=False):
        value = self.requestvalue(name, EMPTYMARKER, checkbox,
                                  chain, nameprefix)
        if value is EMPTYMARKER:
            defaults = self._defaultvalues
            if defaults:
                value = defaults.get(self._name(name, nameprefix), EMPTYMARKER)
        if value is EMPTYMARKER:
            return default
        return value

    def selected(self, name, value, cookiewins=False, nameprefix=False):
        """selected() is deprecated, will be removed in version 2.0.
        """
        if cookiewins:
            requested = self.cookievalue(name, nameprefix=nameprefix)
            if not requested:
                requested = self.formvalue(name, nameprefix=nameprefix)
        else:
            requested = self.formvalue(name, nameprefix=nameprefix)
        return self._checkrequestedvalue(requested, value)

    def formselected(self, name, value, nameprefix=False):
        requested = self.formvalue(name, nameprefix=nameprefix)
        return self._checkrequestedvalue(requested, value)

    def cookieselected(self, name, value, nameprefix=False):
        requested = self.cookievalue(name, nameprefix=nameprefix)
        return self._checkrequestedvalue(requested, value)

    def sessionselected(self, name, value, nameprefix=False):
        session = self.context.session_data_manager.getSessionData(create=False)
        if not session:
            return False
        requested = session.get(self._name(name, nameprefix))
        return self._checkrequestedvalue(requested, value)

    def requestselected(self, name, value,
                        chain=(REQUEST, COOKIE),
                        nameprefix=False):
        requested = self._valuefromchain(chain, name, nameprefix)
        return self._checkrequestedvalue(requested, value)

    def xrequestselected(self, name, value,
                         chain=(REQUEST, COOKIE),
                         nameprefix=False):
        requested = self._valuefromchain(chain, name, nameprefix, EMPTYMARKER)
        if requested is EMPTYMARKER:
            defaults = self._defaultvalues
            if defaults:
                requested = defaults.get(self._name(name, nameprefix),
                                         EMPTYMARKER)
        if requested is EMPTYMARKER:
            return False
        return self._checkrequestedvalue(requested, value)

    def cookieset(self, name, value, path='/', nameprefix=False):
        self.request.response.setCookie(self._cookiename(name, nameprefix),
                                        value, path=path)

    def sessionset(self, name, value, nameprefix=False):
        session = self.context.session_data_manager.getSessionData(create=True)
        session[self._name(name, nameprefix)] = value

    def redirect(self, url):
        self.request.response.redirect(url)

    def _name(self, name, nameprefix=False):
        if nameprefix is False:
            nameprefix = self.nameprefix
        if nameprefix:
            return '%s.%s' % (nameprefix, name)
        return name

    def _cookiename(self, name, nameprefix):
        name = self._name(name, nameprefix)
        prefix = ICookiePrefix(self.context).prefix
        return '%s.%s' % (prefix, name)

    def _valuefromchain(self, chain, name, nameprefix,
                        default=None, checkbox=False):
        value = EMPTYMARKER
        for chained in chain:
            if chained == REQUEST:
                value = self.formvalue(name, EMPTYMARKER, checkbox, nameprefix)
                if value is not EMPTYMARKER:
                    break
            elif chained == COOKIE:
                value = self.cookievalue(name, EMPTYMARKER, nameprefix)
                if value is not EMPTYMARKER:
                    break
            elif chained == SESSION:
                value = self.sessionvalue(name, EMPTYMARKER, nameprefix)
                if value is not EMPTYMARKER:
                    break
        if value is EMPTYMARKER:
            return default
        if isinstance(value, basestring):
            return urllib.unquote(value)
        return value

    def _checkrequestedvalue(self, requested, value):
        if type(requested) == types.ListType:
            if value in requested:
                return True
        if value == requested:
            return True
        return False

    def _chainkeys(self, chain):
        chainkeys = Set()
        for chained in chain:
            if chained == REQUEST:
                keys = self.request.form.keys()
            elif chained == COOKIE:
                cookieprefix = ICookiePrefix(self.context).prefix
                keys = []
                for key in self.request.cookies.keys():
                    if key.startswith(cookieprefix):
                        keys.append(key[len(cookieprefix) + 1:])
                #keys = self.request.cookies.keys()
            elif chained == SESSION:
                sessiondatamanager = self.context.session_data_manager
                session = sessiondatamanager.getSessionData(create=False)
                if not session:
                    keys = []
                else:
                    keys = session.keys()
            for key in keys:
                ### TODO: chainedkeys not defined -> chainkeys??? write test case for this.
                chainedkeys.add(key)
        return chainedkeys

    def _chaindata(self, additionals=None, ignores=None, considerexisting=False,
                   considerspecific=None, nameprefix=False, chain=[]):
        params = {}
        if considerexisting:
            keys = self._chainkeys(chain)
            for key in keys:
                if ignores:
                    if key in ignores:
                        continue
                if key != '-C': # TODO: make global blacklist
                    value = self.requestvalue(key, chain=chain, nameprefix=None)
                    params[key] = value
        if considerspecific and not considerexisting:
            for param in considerspecific:
                value = self.requestvalue(param, chain=chain, nameprefix=None)
                if value:
                    params[param] = value
        if additionals:
            prefixedadditionals = dict()
            for key in additionals.keys():
                name = self._name(key, nameprefix)
                prefixedadditionals[name] = additionals[key]
            params.update(prefixedadditionals)
        return params

    @property
    def _defaultvalues(self):
        defaultvalues = None
        if self.nameprefix:
            try:
                defaultvalues = getAdapter(self.context, IRequestDefaultValues,
                                           name=self.nameprefix)
            except ComponentLookupError, e: pass
        try:
            defaultvalues = IRequestDefaultValues(self.context)
        except ComponentLookupError, e: pass
        return defaultvalues

class AjaxMixin(object):
    """IAjaxMixin implementation.
    """

    implements(IAjaxMixin)

    def initializeFormByHyperlink(self, href):
        href = href.replace('&#38;', '&') # safari stuff
        query = urlsplit(href)[3]
        parts = query.split('&')
        for part in parts:
            param, value = part.split('=')
            # XXX: improve by zopes parsing mechanisms e.g. ``int:foo=1``
            if param.find(':') != -1:
                param = param[:param.find(':')]
            self.request.form[param] = value
    
    def ajaxresponse(self, state=1, payload='', error=''):
        state = self._tag('span', str(state), class_='responsestate')
        payload = self._tag('span', payload, class_='responsepayload')
        error = self._tag('span', error, class_='responseerror')
        return self._tag('span', state, payload, error, class_='response')

class RequestTool(RequestMixin):
    """Derived from RequestMixin, it provides simply the required signature.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request


class XBrowserView(BrowserView, RequestMixin):
    """An extended BrowserView providing the RequestMixin functions.
    """

class AjaxBrowserView(XBrowserView, AjaxMixin):
    """Browser view to be used for ajax operations.
    """