from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model, authenticate, login
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from requests.exceptions import ConnectionError, HTTPError
from hashlib import sha1

from .oauth1 import OAuth1
from .oauth2 import OAuth2

import logging, pretend, shortuuid, urllib, requests

User = get_user_model()

logger = logging.getLogger(__name__)

DENDRITE = pretend.stub(
    NEXT = getattr(settings, 'DENDRITE', {}).get('NEXT', 'next'),
    LOGIN_REDIRECT_URL = getattr(settings, 'DENDRITE', {}).get('LOGIN_REDIRECT_URL'),
    ERROR = 'ERROR',
)

ERRORS = pretend.stub(
    API_ERROR={
        'error': 1,
        'error_description': 'The connected API returned an error.'},            
    DIFFERENT_USER={'error': 2,
                    'error_description': 'Already logged in as a different user.'},
    CANNOT_CONNECT={'error': 3,
                    'error_description': 'Cannot connect with service.'},
    HTTP_ERROR={'error': 4,
                'error_description': 'Error while requesting data from remote server.'},
    EXPIRED={'error': 5,
             'error_description': 'Connection expired.'})

#########################
# Shared functionality  #
#########################

class SocialView(TemplateView):
    timeout = 86400
    template_name = 'dendrite/error.html'

    def cache_key(self, value):
        return 'dendrite:{}'.format(sha1(value.encode('utf-8')).hexdigest())

    def error(self, request, error=None, exception=None, status_code=400):
        return self.render_to_response({'error': error, 'exception': exception},
                                       status=status_code)


class CallbackView(SocialView):
    _login = lambda self, *args: login(*args)
    _authenticate = lambda self, **kwargs: authenticate(**kwargs)

    def dispatch(self, *args, **kwargs):
        assert self._authenticate, "No authentication function set. Please provide " \
            "a `_authenticate` attribute on your mixin class."
        assert self._login, "No login function set. Please provide a `_login` attribute "\
            "on your mixin class."
        assert self.profile_class, "No profile class defined. Please provide a "\
            "`profile_class` attribute on your mixin class."
        
        return super(CallbackView, self).dispatch(*args, **kwargs)


    def process_token(self, token):
        """ Some services do weird things to the returned access
        token. Use this to un-weird it. """
        return token


    def get_remote_profile(self, request, token):
        """ Only method that needs implementing if everything is
        following convention. Ideally, the OAuth2 service returns
        profile information with the access token, but some don't."""

        raise NotImplementedError("You must define `get_remote_profile` method")


    def create_user(self, request, profile, token):
        """ Override to customize user creation """
        return User.objects.create(username = shortuuid.uuid())
        

    def create_profile(self, request, user, profile, token):
        """ Override to customize profile creation """
        data = profile.copy()
        data.update(token.copy())

        # We're already passing a `user` argument below. Can't have
        # two. Some services return a 'user' key in the token data
        if 'user' in data:
            del data['user']
            
        profile = self.profile_class.objects.create(
            user = user, **data)

        return profile

    def update_profile(self, request, user, profile, token):
        """ Override to customize profile updates """
        pass


    def authenticate(self, **kwargs):
        return self._authenticate(profile_class=self.profile_class, **kwargs)


    def login(self, request, user):
        return self._login(request, user)

    def connect(self, request, token):
        profile = self.get_remote_profile(request, token)

        user = self.authenticate(**profile)

        if request.user.is_authenticated():
            if user and not request.user == user:
                # Logged in, current user doesn't match the profile user
                return self.error(request, error=ERRORS.DIFFERENT_USER, status_code=403)

            if not user:
                # Logged in, new profile
                self.create_profile(request, request.user, profile, token)
                self.update_profile(request, request.user, profile, token)
            else:
                # Logged in, old profile
                self.update_profile(request, request.user, profile, token)
        else:
            if not user:
                # Logged out, new user, new profile
                user = self.create_user(request, profile, token)
                self.create_profile(request, user, profile, token)
                user = self.authenticate(**profile)
                self.login(request, user)
                self.update_profile(request, user, profile, token)
            else:
                # Logged out, old user, old profile
                self.login(request, user)
                self.update_profile(request, request.user, profile, token)


    def redirect(self, request):
        redirect = (request.GET.get(DENDRITE.NEXT) or
                    getattr(request, 'session', request.COOKIES).get(DENDRITE.NEXT) or
                    DENDRITE.LOGIN_REDIRECT_URL or
                    settings.LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(redirect)


###########
# OAuth1  #
###########

class OAuth1Mixin(object):
    client_id         = '' 
    client_secret     = ''

    authorization_url = ''
    access_token_url  = ''
    request_token_url = ''    

    profile_class     = None

    client_class      = OAuth1

    oauth_token       = {}

    verifier          = None

    signature_type    = None

    requests = requests 

    @property
    def client(self):
        return self.client_class(
            client_id=self.client_id,
            client_secret=self.client_secret,
            verifier=self.verifier,
            request_token_url=self.request_token_url,
            authorization_url=self.authorization_url,
            access_token_url=self.access_token_url, 
            signature_type=self.signature_type,
            requests=self.requests,
            **self.oauth_token)


class OAuth1ConnectView(SocialView):
    def get(self, request):
        try:
            self.oauth_token = self.client.get_request_token()

        except (ConnectionError, HTTPError) as e:
            logger.exception(e)
            return self.error(request, ERRORS.HTTP_ERROR, exception=e)

        except AssertionError as e:
            logger.exception(e)
            return self.error(request, ERRORS.CANNOT_CONNECT, exception=e)
            
        cache.set(self.cache_key(self.oauth_token['oauth_token']),
                  self.oauth_token,
                  self.timeout)

        url = self.client.get_authorization_url()

        return HttpResponseRedirect(url)


class OAuth1CallbackView(CallbackView):
    def get(self, request):
        oauth_token, verifier = (
            request.GET.get('oauth_token'), request.GET.get('oauth_verifier'))

        oauth_token = request.GET.get('oauth_token')

        self.verifier = request.GET.get('oauth_verifier')

        self.oauth_token = cache.get(self.cache_key(oauth_token))

        if not self.oauth_token:
            return self.error(request, ERRORS.EXPIRED)

        try:
            self.oauth_token = self.process_token(
                self.client.get_access_token())

        except (ConnectionError, HTTPError) as e:
            logger.exception(e)
            return self.error(request, ERRORS.HTTP_ERROR)

        except AssertionError as e:
            logger.exception(e)
            return self.error(request, ERRORS.CANNOT_CONNECT)
        
        return self.connect(request, self.oauth_token) or self.redirect(request)

###########
# OAuth 2 #
###########

class OAuth2Mixin(object):
    client_id         = '' 
    client_secret     = ''

    authorization_url = ''
    access_token_url  = ''
    redirect_uri      = ''

    profile_class     = None

    client_class      = OAuth2

    requests          = requests

    @property
    def client(self):
        return self.client_class(
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorization_url=self.authorization_url,
            access_token_url=self.access_token_url,
            redirect_uri=self.redirect_uri,
            requests=self.requests)


class OAuth2ConnectView(SocialView):
    scope = "read"

    def get(self, request):
        state = shortuuid.uuid()

        cache.set(self.cache_key(state), True, self.timeout)

        url = self.client.get_authorization_url(
            self.scope, state=state, response_type='code')

        return HttpResponseRedirect(url)


class OAuth2CallbackView(CallbackView):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        if 'error' in request.GET:
            return self.error(request, error=request.GET.get('error'))

        if not cache.get(self.cache_key(state)):
            return self.error(request, error=ERRORS.EXPIRED)

        try:
            token = self.client.get_access_token(code, grant_type='authorization_code')

            if 'error' in token:
                return self.error(request, error=token)

            self.oauth_token = self.process_token(token)

        except (ConnectionError, HTTPError) as e:
            logger.exception(ERRORS.HTTP_ERROR['error_description'], e)
            return self.error(request, error=ERRORS.HTTP_ERROR, exception=e)
        
        if 'error' in self.oauth_token:
            return self.error(request, self.oauth_token, exception=e)

        return self.connect(request, self.oauth_token) or self.redirect(request)
            
