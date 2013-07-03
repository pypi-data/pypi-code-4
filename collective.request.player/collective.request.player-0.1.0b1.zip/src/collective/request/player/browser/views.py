""" The module is dedicated to plone requests """

import sha
import hmac
import binascii
from urlparse import urljoin
from itertools import chain, starmap

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName, getUtility

from zope.component import getMultiAdapter
from plone.session import tktauth
from plone.keyring.interfaces import IKeyManager

import requests
from collective.request.player.utils import load, dict_to_pyobject, str_to_pyobject
from collective.request.player.config import ALLOWED_INPUT_PARAMS


def get_authenticator(user):
    """ Get authenticator for request """
    manager = getUtility(IKeyManager)
    secret = manager.secret()
    auth = hmac.new(secret, user, sha).hexdigest()
    return  auth


def add_conversion_markers(params):
    def add_marker(key, value):
        # This trick is dedicated to zope publisher.
        # Details: http://docs.zope.org/zope2/zdgbook/ObjectPublishing.html#argument-conversion
        # However, it does not work for all options.
        # __iter__ works on sequence types, but it would fail on strings
        if hasattr(value, '__iter__'):
            class_name = type(value).__name__
            return key + ':' + class_name, value

        return key, value

    request_data = str_to_pyobject(params)
    return dict(starmap(add_marker, request_data.iteritems()))


def requests_filter(request):
    """ Filter parameters according to requests package.
        config.py has more details.
    """
    return dict((key, value)
                for key, value in request.iteritems()
                if key in ALLOWED_INPUT_PARAMS)


class RequestsPlayer(BrowserView):
    """ It replays requests. """
    def getHeaders(self):
        headers = list(set(chain.from_iterable(self.requests)))
        headers.sort()
        return headers

    def sendRequest(self, method, data, path_info, **kwargs):
        """ It sends request using requests package """
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )
        url = urljoin(portal_state.navigation_root_url(), path_info)
        if method == 'GET':
            response = requests.get(url, params=data, ** requests_filter(kwargs))
        elif method == 'POST':
            response = requests.post(url, data=data, ** requests_filter(kwargs))

        # Maybe this code will be useful in the future.
        # # get a previous(old) response status
        # old_status = kwargs.get('status_code', '')
        # # compare it with a new one
        # if old_status.isdigit() and response.status_code != int(old_status):
        #     print 'Status code mismatch %s/%s for "%s" (%s)' % (
        #         old_status, response.status_code, url, kwargs.get('user'))

        # # get a previous(old) content length
        # old_length = kwargs.get('content_length')
        # # compare it with a new one
        # new_length = response.headers.get('content_length')
        # if new_length != old_length:
        #     print 'Size mismatch %s/%s for "%s" (%s)' % (
        #         new_length, old_length, url, kwargs.get('user'))
        try:
            return response.content
        finally:
            response.close()

    def getAuthCookie(self, userid):
        """ It fakes the cookie (__ac) """
        acl_users = getToolByName(self.context, 'acl_users')
        cookie = tktauth.createTicket(
            secret=acl_users.session._getSigningSecret(),
            userid=userid,
            mod_auth_tkt=False,
            encoding='utf-8',
        )
        cookie = binascii.b2a_base64(cookie).rstrip()
        return {'__ac': cookie}

    def playRequests(self):
        """ It replays checked request """
        requests = self.request.form.get('requests')
        # TODO: you can play only one request at a time.
        # The better solution: replay a list of requests.
        for request in requests:
            # take the first request and replay it
            if request.get('checked_request'):
                data = request.get('data')
                # add publisher markers
                params = add_conversion_markers(data)
                # create cookies
                acl_users = getToolByName(self.context, 'acl_users')
                user = request.get('user')
                cookies = self.request.cookies.copy()
                # If user is not a plone user,
                # get current an authenticated user for replaying.
                if acl_users.getUserById(user):
                    cookies.update(self.getAuthCookie(user))
                # fake authenticator
                if '_authenticator' in params:
                    params['_authenticator'] = get_authenticator(user)
                # Copy for safety.
                # Also, request cannot be modified if it is not copied.
                rqst = dict(request)
                # convert dictionary values (strings) to python objects
                rqst = dict_to_pyobject(rqst)
                # setup data for request (GET and POST)
                rqst['data'] = params
                # cookies can be added by the html form
                if 'cookies' in rqst:
                    rqst['cookies'].update(cookies)
                else:
                    rqst['cookies'] = cookies
                return self.sendRequest(**rqst)

    def setup(self):
        # Import requests.
        if hasattr(self.request, 'datafile'):
            self.requests = load(self.request.datafile)
        # But sometimes we do not want to import http requests.
        else:
            # The 'list' is used due to a compatibility with the 'load' function.
            self.requests = [ALLOWED_INPUT_PARAMS]

    def __call__(self):
        if 'form.submitted' not in self.request.form:
            self.setup()
            return self.index()

        return self.playRequests()
