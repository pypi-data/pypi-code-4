# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging

from facepy import (
    FacepyError,
    get_application_access_token,
    GraphAPI,
    SignedRequest,
    )
from facepy.exceptions import SignedRequestError

from pyramid.decorator import reify
from pyramid.security import Allow

from pyramid_contextauth import get_authentication_policy

from pyramid_facebook.events import UserSignedRequestParsed

log = logging.getLogger(__name__)

RETRY_NB = 3

ViewCanvas = u'view_canvas'
Authenticate = u'authenticate'
UpdateSubscription = u'update_subscription'
NotifyRealTimeChanges = u'notify_real_time_changes'

FacebookUser = u'facebook-user'
RegisteredUser = u'registered-user'
AdminUser = u'admin-user'
# real time updates https://developers.facebook.com/docs/reference/api/realtime
XHubSigned = u'x-hub-signed'


def includeme(config):
    app_id = config.registry.settings['facebook.app_id']
    secret_key = config.registry.settings['facebook.secret_key']

    policy = get_authentication_policy(config)

    # by default, having a user id means that user is registered
    policy.callback = lambda user_id, request: [RegisteredUser]

    signed_request_policy = SignedRequestAuthenticationPolicy()
    access_token_policy = AccessTokenAuthenticationPolicy()
    real_time_policy = RealTimeNotifAuthenticationPolicy()
    admin_policy = AdminAuthenticationPolicy(app_id, secret_key)

    policy.register_context(SignedRequestContext, signed_request_policy)
    policy.register_context(FacebookCreditsContext, signed_request_policy)
    policy.register_context(AccessTokenContext, access_token_policy)
    policy.register_context(RealTimeNotificationContext,
                            real_time_policy)
    policy.register_context(AdminContext, admin_policy)


class SignedRequestContext(object):
    """Security context for facebook signed request routes.

    Attributes: *facebook_data* is information decoded from the signed
    request; *custom_data* can be set by authentication policies that
    build on top of pyramid-facebook to use a central database for users,
    for example.

    The properties *user* and *user_country* are shortcuts for fields
    in *facebook_data*
    """

    __acl__ = [
        (Allow, FacebookUser, Authenticate),
        (Allow, RegisteredUser, ViewCanvas),
        ]

    def __init__(self, request):
        self.request = request
        self.facebook_data = None
        self.custom_data = None

    @reify
    def user(self):
        return self.facebook_data['user']

    @reify
    def user_country(self):
        return self.facebook_data['user']['country']

    def __repr__(self):
        return '<%s facebook_data=%r>' % (
            self.__class__.__name__,
            self.facebook_data
            )


class FacebookCreditsContext(SignedRequestContext):
    "Context for facebook credits callback requests."

    @reify
    def order_details(self):
        """Order details received in `facebook credits callback for payment
        status updates <http://developers.facebook.com/docs/credits/callback/
        #payments_status_update>`_."""
        return json.loads(
            self.facebook_data['credits']['order_details']
            )

    @reify
    def order_info(self):
        """Order info being the order information passed when the `FB.ui method
        <http://developers.facebook.com/docs/reference/javascript/FB.ui/>`_
        is invoked."""
        return self.facebook_data["credits"]["order_info"]

    @reify
    def earned_currency_data(self):
        """Modified field received in `facebook credits callback for payment
        status update for earned app currency
        <http://developers.facebook.com/docs/credits/callback/
        #payments_status_update_earn_app_currency>`_."""
        data = self.item['data']
        if data:
            try:
                data = json.loads(data)
                data = data['modified'] if 'modified' in data else None
            except Exception:
                data = None
        return data

    @reify
    def item(self):
        """The item info as passed when `FB.ui method
        <http://developers.facebook.com/docs/reference/javascript/FB.ui/>`_
        is invoked."""
        return self.order_details['items'][0]


class AccessTokenContext(object):

    def __init__(self, request):
        self.request = request
        self._user_dict = {}
        self._user_id = None

    @property
    def user_dict(self):
        return self._user_dict

    @user_dict.setter
    def user_dict(self, value):
        self._user_dict = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value


class AdminContext(AccessTokenContext):
    """Context which defines principals as administrative roles user has on
    facebook.

    https://developers.facebook.com/docs/reference/api/application/#roles
    """

    def __init__(self, request):
        super(AdminContext, self).__init__(request)
        self.__acl__ = (
            (Allow, u'group:administrators', UpdateSubscription),
            )


class RealTimeNotificationContext(object):
    "Context for real-time changes notification route."

    __acl__ = (
        (Allow, XHubSigned, NotifyRealTimeChanges),
        )

    def __init__(self, request):
        self.request = request


class SignedRequestAuthenticationPolicy(object):

    def unauthenticated_userid(self, request):
        context = request.context
        if 'signed_request' not in request.params:
            return None
        context.facebook_data = None
        try:
            context.facebook_data = SignedRequest.parse(
                request.params[u'signed_request'],
                request.registry.settings[u'facebook.secret_key'],
                )
        except SignedRequestError:
            log.warn('SignedRequestError with signature: %s',
                     request.params['signed_request'], exc_info=True)
            return None
        try:
            user_id = int(context.facebook_data[u'user_id'])
        except KeyError:
            # user_id not in facebook_data => user has not authorized app
            log.debug('User has not authorized app.')
        except ValueError:
            log.warn('Invalid user id %r', context.facebook_data[u'user_id'])
        else:
            request.registry.notify(
                UserSignedRequestParsed(request.context, request)
                )
            return user_id
        return None

    def effective_principals(self, request):
        try:
            if request.context.facebook_data['user_id']:
                return [FacebookUser]
        except Exception:
            return []


class AccessTokenAuthenticationPolicy(object):

    def unauthenticated_userid(self, request):
        try:
            access_token = request.params['access_token']
        except KeyError:
            return None
        request.context.access_token = access_token
        api = GraphAPI(access_token)
        try:
            request.context.user_dict = api.get('me', retry=RETRY_NB)
        except FacepyError:
            log.warn('Authentication failed', exc_info=True)
        try:
            request.context.user_id = long(request.context.user_dict['id'])
            return request.context.user_id
        except KeyError:
            return None
        except ValueError:
            log.warn('Malformated Facebook response', exc_info=True)
        return None

    def effective_principals(self, request):
        p = []
        if request.context.user_id:
            p.append(FacebookUser)
        return p


class RealTimeNotifAuthenticationPolicy(object):

    def effective_principals(self, request):
        # route predicates already check presence of X-Hub-Signature header
        sig = request.headers[u'X-Hub-Signature']
        verif = hmac.new(
            request.registry.settings['facebook.secret_key'],
            request.body,
            hashlib.sha1
            ).hexdigest()
        if sig == ('sha1=%s' % verif):
            return [XHubSigned]
        else:
            log.warn('X-Hub-Signature invalid - expected %s, received %s',
                     verif, sig)
        return []


class AdminAuthenticationPolicy(AccessTokenAuthenticationPolicy):
    """Check from on facebook what role the user has on the application via its
    access_token. Role the user should assume, one of 'group:administrators',
    'group:developers', 'group:testers' or 'group:insights users'

    https://developers.facebook.com/docs/reference/api/application/#roles
    """
    def __init__(self, app_id, secret_key):
        self.app_id = app_id
        self.secret_key = secret_key
        self.app_token = get_application_access_token(self.app_id,
                                                      self.secret_key)

    def effective_principals(self, request):
        p = super(AdminAuthenticationPolicy,
                  self).effective_principals(request)

        api = GraphAPI(self.app_token)
        try:
            roles = api.get('%s/roles' % self.app_id, retry=RETRY_NB)
        except FacepyError:
            log.warn('Get roles failed', exc_info=True)
            return p
        for role in roles['data']:
            if request.context.user_id == long(role['user']):
                p.append('group:' + role['role'])
        return p
