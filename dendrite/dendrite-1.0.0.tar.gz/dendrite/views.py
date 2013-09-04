from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model, authenticate, login
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect
from requests.exceptions import ConnectionError, HTTPError

from .oauth2 import OAuth2

import logging, pretend, shortuuid, urllib

logger = logging.getLogger(__name__)

DENDRITE = pretend.stub(
    NEXT = getattr(settings, 'DENDRITE', {}).get('NEXT', 'next'),
    LOGIN_REDIRECT_URL = getattr(settings, 'DENDRITE', {}).get('LOGIN_REDIRECT_URL'),
    ERROR = 'ERROR',
)

User = get_user_model()


class OAuth2Mixin(object):
    _client = None
    client_class = OAuth2
    profile_class = None

    client_id = ''
    client_secret = ''
    site = ''
    authorization_url = ''
    token_url = ''
    redirect_uri = ''

    _login = lambda self, *args: login(*args)
    _authenticate = lambda self, **kwargs: authenticate(**kwargs)

    @property
    def client(self):
        self._client = self._client or self.client_class(
            self.client_id,
            self.client_secret,
            self.site,
            self.authorization_url,
            self.token_url,
            self.redirect_uri)

        return self._client

    def dispatch(self, *args, **kwargs):
        assert self._authenticate, "No authentication function set. Please provide " \
            "a `_authenticate` attribute on your mixin class."
        assert self._login, "No login function set. Please provide a `_login` attribute "\
            "on your mixin class."
        assert self.profile_class, "No profile class defined. Please provide a "\
            "`profile_class` attribute on your mixin class."
        
        return super(OAuth2Mixin, self).dispatch(*args, **kwargs)


class OAuth2ConnectView(View):
    """ Send a user off to the third party to connect """
    scope = "read"

    def get(self, request):
        url = self.client.authorize_url(self.scope,
                                         state=shortuuid.uuid(),
                                         response_type="code")
        return HttpResponseRedirect(url)


class OAuth2CallbackView(View):
    """ Receives a user from the third party """
    ERRORS = pretend.stub(
        API_ERROR={
            'error': 1,
            'error_description': 'The connected API returned an error'},            
        DIFFERENT_USER={'error': 2,
                        'error_description': 'Already logged in as a different user.'},
        CANNOT_CONNECT={'error': 3,
                        'error_description': 'Cannot connect with service.'},
        HTTP_ERROR={'error': 4,
                    'error_description': 'Error while requesting data from remote server.'})


    def error(self, request, error=None):
        request.session[DENDRITE.ERROR] = error
        return HttpResponseRedirect(reverse('dendrite:error'))
                          

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

        # We're already passing a `user` argument below. Can't have two.
        if 'user' in data:
            del data['user']
            
        profile = self.profile_class.objects.create(
            user = user, **data)

    def update_profile(self, request, user, profile, token):
        """ Override to customize profile updates """
        pass

    def authenticate(self, **kwargs):
        return self._authenticate(profile_class=self.profile_class, **kwargs)

    def login(self, request, user):
        return self._login(request, user)

    def get(self, request):
        code = request.GET.get('code')

        if 'error' in request.GET:
            return self.error(request, error=request.GET.get('error'))

        try:
            token = self.process_token(
                self.client.get_token(code, grant_type='authorization_code'))
        except (ConnectionError, HTTPError) as e:
            logger.exception(self.ERRORS.HTTP_ERROR['error_description'], e)
            return self.error(request, error=self.ERRORS.HTTP_ERROR)
        
        if 'error' in token:
            return self.error(request, error=token)

        profile = self.get_remote_profile(request, token)

        user = self.authenticate(**profile)

        if request.user.is_authenticated():
            if not request.user == user:
                return self.error(request, error=self.ERRORS.DIFFERENT_USER)

            if not user:
                self.create_profile(request, request.user, profile, token)
                self.update_profile(request, request.user, profile, token)
            else:
                self.update_profile(request, request.user, profile, token)
        else:
            if not user:
                user = self.create_user(request, profile, token)
                self.create_profile(request, user, profile, token)
                user = self.authenticate(**profile)
                self.login(request, user)
                self.update_profile(request, user, profile, token)
            else:
                self.login(request, user)
                self.update_profile(request, request.user, profile, token)

        redirect = (request.GET.get(DENDRITE.NEXT) or
                    getattr(request, 'session', request.COOKIES).get(DENDRITE.NEXT) or
                    DENDRITE.LOGIN_REDIRECT_URL or
                    settings.LOGIN_REDIRECT_URL)

        return HttpResponseRedirect(redirect)
            

class ErrorView(TemplateView):
    template_name = 'dendrite/error.html'

    def get(self, request):
        return self.render_to_response({'error': request.session[DENDRITE.ERROR]})
