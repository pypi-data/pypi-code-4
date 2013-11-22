from pyramid.security import remember, forget, unauthenticated_userid
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPFound

import odesk


class BaseHandler(object):
    """Base handler with ACL management.

    Inherit and define the desired methods,
    then register views and set permissions.

    """

    def __init__(self, request):
        self.request = request

    def __call__(self):
        """Dispatch the request."""
        method = self.request.method
        try:
            return getattr(self, method.lower())()
        except NotImplementedError:
            raise HTTPMethodNotAllowed(method)

    def get(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def put(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


def _get_odesk_client(request, **attrs):
    """Construct an oDesk client.

    *Parameters:*
      :attrs:   keyword arguments that will be
                attached to the ``client.auth`` as attributes
                (``request_token``, etc.)
    """
    client_kwargs = {
        'oauth_access_token': attrs.pop('oauth_access_token', None),
        'oauth_access_token_secret': attrs.pop(
            'oauth_access_token_secret', None)

    }

    settings = request.registry.settings
    client = odesk.Client(settings['odesk.api.key'],
                          settings['odesk.api.secret'], **client_kwargs)

    for key, value in attrs.items():
        setattr(client.auth, key, value)

    return client


def login(request):
    """The login view performs following actions:

    - Redirects user to oDesk. If user is logged in, callback url
      is invoked, otherwise user is asked to login to oDesk.

    """
    client = _get_odesk_client(request)
    authorize_url = client.auth.get_authorize_url()
    # Save request tokens in the session
    request.session['odesk_request_token'] = client.auth.request_token
    request.session['odesk_request_token_secret'] = \
        client.auth.request_token_secret

    redirect_url = '{0}&callback_url={1}'.format(
        authorize_url,
        request.route_url('oauth_callback',
                          _query={'next': request.GET.get('next', '/')})
    )
    return HTTPFound(location=redirect_url)


def logout(request):
    # Forget user
    forget(request)
    request.session.invalidate()
    return HTTPFound('/')


def oauth_callback(request):
    verifier = request.GET.get('oauth_verifier')
    next_url = request.GET.get('next', '/')

    request_token = request.session.pop('odesk_request_token', None)
    request_token_secret = request.session.pop(
        'odesk_request_token_secret', None)

    if verifier:
        client = _get_odesk_client(request, request_token=request_token,
                                   request_token_secret=request_token_secret)
        oauth_access_token, oauth_access_token_secret = \
            client.auth.get_access_token(verifier)

        client = _get_odesk_client(
            request,
            oauth_access_token=oauth_access_token,
            oauth_access_token_secret=oauth_access_token_secret)

        # Get user info
        user_info = client.auth.get_info()
        user_uid = user_info['auth_user']['uid']

        # Store the user in session
        remember(request, user_uid)
        # Store oauth access token in session
        request.session['auth.access_token'] = oauth_access_token
        request.session['auth.access_token_secret'] = oauth_access_token_secret

        # Redirect to ``next`` url
        return HTTPFound(location=next_url)


def forbidden(request):
    if unauthenticated_userid(request):
        # User is authenticated, but not authorized,
        # show logout link instead of login link
        return {'authenticated': True}
    return {'authenticated': False}
