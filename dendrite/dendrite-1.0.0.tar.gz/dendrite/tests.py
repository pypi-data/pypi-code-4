from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.test.client import RequestFactory
from mock import Mock

from .oauth2 import OAuth2
from .views import OAuth2Mixin, OAuth2ConnectView, OAuth2CallbackView

import json

User = get_user_model()

class TestMixin(OAuth2Mixin):
    _authenticate     = True
    _login            = True
    profile_class     = True
    client_id         = True
    client_secret     = True
    site              = 'https://example.com'
    authorization_url = 'https://example.com/oauth/authorize' 
    token_url         = 'https://example.com/oauth/token'
    redirect_uri      = 'https://develop.local/callback'

class TestConnectView(TestMixin, OAuth2ConnectView):
    pass 

class DendriteTest(TestCase):
    rf = RequestFactory()

    def session(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        middleware = AuthenticationMiddleware()
        middleware.process_request(request)
        return request

    def get(self, url, **kwargs):
        return self.session(self.rf.get(url, **kwargs))
        
    def test_redirect_view(self):
        view = TestConnectView.as_view()

        resp = view(self.rf.get(''))

        self.assertEqual(302, resp.status_code)
        self.assertTrue(resp['Location'].startswith('https://example.com/oauth/authorize'))
        
    def test_oauth2_object(self):
        self.assertRaises(AssertionError, OAuth2,
                          client_id=None, # Invalid client id
                          client_secret='valid',
                          site='https://valid',
                          authorization_url='https://valid',
                          token_url='https://valid',
                          redirect_uri='valid')

        self.assertRaises(AssertionError, OAuth2,
                          client_id='valid',
                          client_secret=None, # Invalid secret
                          site='https://valid',
                          authorization_url='https://valid',
                          token_url='https://valid',
                          redirect_uri='valid')

        self.assertRaises(AssertionError, OAuth2,
                          client_id='valid',
                          client_secret='valid',
                          site='http://invalid', # No TLS
                          authorization_url='https://valid',
                          token_url='https://valid',
                          redirect_uri='valid')

        self.assertRaises(AssertionError, OAuth2,
                          client_id='valid',
                          client_secret='valid',
                          site='https://valid',
                          authorization_url='http://', # No TLS
                          token_url='https://valid',
                          redirect_uri='valid')

        self.assertRaises(AssertionError, OAuth2,
                          client_id='valid',
                          client_secret='valid',
                          site='https://valid',
                          authorization_url='https://valid',
                          token_url='http://invalid', # No TLS
                          redirect_uri='valid')

        self.assertRaises(AssertionError, OAuth2,
                          client_id='valid',
                          client_secret='valid',
                          site='https://valid',
                          authorization_url='https://valid',
                          token_url='https://valid',
                          redirect_uri='') # Invalid


        obj = OAuth2(client_id='valid',
                     client_secret='valid',
                     site='https://valid',
                     authorization_url='https://valid',
                     token_url='https://valid',
                     redirect_uri='valid',
                     requests = Mock(**{
                    'post.return_value.content': json.dumps({'access_token': "Test"})}))

        self.assertTrue(obj)

        url = obj.authorize_url(scope = 'read write')
        self.assertTrue(url)

        token = obj.get_token('Test')
        self.assertTrue('access_token' in token)

        
        




