from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.db import models
from django.http import QueryDict
from django.test import TestCase
from django.test.client import RequestFactory
from mock import Mock

from dendrite.oauth1 import OAuth1
from dendrite.oauth2 import OAuth2
from dendrite.views import *

from .models import TestProfile

import json

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

User = get_user_model()




class TestCallbackView(CallbackView):
    def get_remote_profile(self, request, token):
        return {'id': 'remote-id'}


##########
# OAuth1 #
##########

class OAuth1TestMixin(OAuth1Mixin):
    client_id         = 'test'
    client_secret     = 'test'
    authorization_url = 'https://example.com/oauth/authorize'
    request_token_url = 'https://example.com/oauth/request_token'    
    access_token_url  = 'https://example.com/oauth/access_token'

    profile_class     = TestProfile

class OAuth1TestConnectView(OAuth1TestMixin, OAuth1ConnectView):
    pass

class OAuth1TestCallbackView(OAuth1TestMixin, TestCallbackView, OAuth1CallbackView):
    pass


##########
# OAuth2 #
##########

class OAuth2TestMixin(OAuth2Mixin):
    client_id         = 'test'
    client_secret     = 'test'
    authorization_url = 'https://example.com/oauth/authorize' 
    access_token_url  = 'https://example.com/oauth/token'
    redirect_uri      = 'https://develop.local/callback'

    profile_class     = TestProfile

class OAuth2TestConnectView(OAuth2TestMixin, OAuth2ConnectView):
    pass 

class OAuth2TestCallbackView(OAuth2TestMixin, TestCallbackView, OAuth2CallbackView):
    pass


class DendriteTest(TestCase):
    rf = RequestFactory()

    def setUp(self):
        self.remote_profile = {'id': 'remote-id'}
        self.access_token = {'oauth_token': 'test',
                             'oauth_token_secret': 'test'}        
        self.callback_view = TestCallbackView(profile_class=TestProfile)

        self.oauth1_response = Mock(**{
                'status_code': 200,
                'content': urlencode(self.access_token)})

        self.oauth1_requests  = Mock(**{'post.return_value': self.oauth1_response})

        self.oauth2_requests = requests = Mock(**{
                'post.return_value.content': json.dumps({'oauth_token': "Test"})})


    def get(self, url, **kwargs):
        return self.rf.get(url, **kwargs)

    def session(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        middleware = AuthenticationMiddleware()
        middleware.process_request(request)
        return request

    def test_callback_view(self):
        request = self.rf.get('')

        # Create user 
        user = self.callback_view.create_user(request, self.remote_profile, self.access_token)
        self.assertIsNotNone(user)

        # Create profile 
        profile = self.callback_view.create_profile(request, user, self.remote_profile, self.access_token)
        self.assertIsNotNone(profile)


    def test_callback_view_logged_in_doesnt_match_profile_user(self):
        request = self.session(self.get(''))
        request.user = AnonymousUser()

        view = TestCallbackView(profile_class=TestProfile)
        view.request = request

        user = User.objects.create(username='test')
        profile = TestProfile.objects.create(id = self.remote_profile['id'], user=user)

        imposter = User.objects.create(username='imposter')
        imposter.set_password('imposter')
        imposter.save()

        imposter = view.authenticate(username='imposter', password='imposter')
        view.login(request, imposter)

        request.user = imposter

        self.assertEqual(2, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

        resp = view.connect(request, self.access_token)
        self.assertEqual(403, resp.status_code)

        self.assertEqual(2, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())


    def test_callback_view_logged_in_new_profile(self):
        request = self.session(self.get(''))
        request.user = AnonymousUser()

        view = TestCallbackView(profile_class=TestProfile)
        view.request = request

        user = User.objects.create(username='test')
        user.set_password('test')
        user.save()

        user = view.authenticate(username='test', password='test')
        view.login(request, user)

        request.user = user

        self.assertEqual(1, User.objects.count())
        self.assertEqual(0, TestProfile.objects.count())

        view.connect(request, self.access_token)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())
        
    def test_callback_view_logged_in_old_profile(self):
        request = self.session(self.get(''))
        request.user = AnonymousUser()

        view = TestCallbackView(profile_class=TestProfile)
        view.request = request

        user = User.objects.create(username='test')
        user.set_password('test')
        user.save()

        profile = TestProfile.objects.create(id=self.remote_profile['id'],
                                             user=user)

        user = view.authenticate(username='test', password='test')
        view.login(request, user)

        request.user = user

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

        view.connect(request, self.access_token)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

    def test_callback_view_new_user_new_profile(self):
        request = self.session(self.get(''))
        request.user = AnonymousUser()

        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, TestProfile.objects.count())

        self.callback_view.connect(request, self.access_token)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

    def test_callback_view_old_user_old_profile(self):
        request = self.session(self.get(''))
        user = User.objects.create(username='test')
        profile = TestProfile.objects.create(id = self.remote_profile['id'], user=user)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

        self.callback_view.connect(request, self.access_token)

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

    def test_oauth1_object(self):
        kwargs = {
            'client_id': 'test',
            'client_secret': 'test',
            'request_token_url': 'https://valid',
            'authorization_url': 'https://valid',
            'access_token_url': 'https://valid',
            'requests': self.oauth1_requests
            }

        client = OAuth1(**kwargs)

        request_token = client.get_request_token()

        self.assertEqual(request_token['oauth_token'], self.access_token['oauth_token'])
        self.assertEqual(request_token['oauth_token_secret'], self.access_token['oauth_token_secret'])

        kwargs.update(request_token)

        client = OAuth1(**kwargs)
        access_token = client.get_access_token()
        
        self.assertEqual(request_token['oauth_token'], self.access_token['oauth_token'])
        self.assertEqual(request_token['oauth_token_secret'], self.access_token['oauth_token_secret'])


    def test_oauth1_redirect_view(self):
        view = OAuth1TestConnectView.as_view(requests=self.oauth1_requests)
        resp = view(self.rf.get(''))

        self.assertEqual(302, resp.status_code)
        self.assertTrue(resp['Location'].startswith('https://example.com/oauth/authorize'))

    def test_oauth1_callback_view(self):
        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, TestProfile.objects.count())

        view = OAuth1TestConnectView.as_view(requests=self.oauth1_requests)
        resp = view(self.rf.get(''))

        self.assertEqual(302, resp.status_code)

        view = OAuth1TestCallbackView.as_view(requests=self.oauth1_requests)

        request = self.session(self.rf.get('/?{}'.format(urlencode({
                        'oauth_token': self.access_token['oauth_token'],
                        'verifier': 'test'}))))
        request.user = AnonymousUser()

        resp = view(request)


        self.assertEqual(302, resp.status_code)
        self.assertTrue(request.user.is_authenticated())
        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())

    def test_oauth2_object(self):
        obj = OAuth2(client_id='valid',
                     client_secret='valid',
                     authorization_url='https://valid',
                     access_token_url='https://valid',
                     redirect_uri='valid',
                     requests=self.oauth2_requests)

        self.assertTrue(obj)

        url = obj.get_authorization_url(scope = 'read write')
        self.assertTrue(url)

        token = obj.get_token('Test')

        # Re-using OAuth1 data
        self.assertTrue('oauth_token' in token)

    def test_oauth2_redirect_view(self):
        view = OAuth2TestConnectView.as_view()

        resp = view(self.rf.get(''))

        self.assertEqual(302, resp.status_code)
        self.assertTrue(resp['Location'].startswith('https://example.com/oauth/authorize'))
        
    def test_oauth2_callback_view(self):
        self.assertEqual(0, User.objects.count())
        self.assertEqual(0, TestProfile.objects.count())

        view = OAuth2TestConnectView.as_view(requests=self.oauth2_requests)
        resp = view(self.rf.get(''))

        self.assertEqual(302, resp.status_code)

        state = QueryDict(resp['Location'])['state']

        view = OAuth2TestCallbackView.as_view(requests=self.oauth2_requests)

        request = self.session(self.rf.get('/?{}'.format(urlencode({
                        'code': 'test',
                        'state': state
                        }))))
        request.user = AnonymousUser()

        resp = view(request)

        self.assertEqual(302, resp.status_code)
        self.assertTrue(request.user.is_authenticated())
        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, TestProfile.objects.count())
