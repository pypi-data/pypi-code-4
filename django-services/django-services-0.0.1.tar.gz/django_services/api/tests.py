from django.test import TestCase, Client
from .auth import KeystoneAuthentication
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.compat import patterns
from rest_framework import status
from email.Utils import formatdate
import hmac
import base64
import hashlib


class MockView(APIView):

    def get(self, request):
        return HttpResponse({'a': 1, 'b': 2, 'c': 3})
    post = get
    put = get


urlpatterns = patterns(
    '',
    (r'^keystone-test/$', MockView.as_view(authentication_classes=[KeystoneAuthentication])),
)


class KeystoneAuthenticationIntegrationTests(TestCase):
    urls = __name__

    def setUp(self):
        self.client = Client()
        self.access_key = '3115891eb7254482a30275c7b7bf132d'
        self.secret_key = '5426e3666c6b40a89e159ce6df36d327'
        self.server_string = 'http://localhost:8001'

    def hmac_sha1(self, string_to_sign):
        m = hmac.new(self.secret_key, digestmod=hashlib.sha1)
        m.update(string_to_sign.encode('utf-8'))
        signature = base64.b64encode(m.digest())
        return signature

    def authorization_header(self, method, path, content, content_type, date=None):
        date = date or formatdate()
        string_to_sign = "\n".join((method, content, content_type, date, path))
        signature = self.hmac_sha1(string_to_sign)
        return 'AWS %s:%s' % (self.access_key, signature)

    def test_request_without_authorization_headers_returns_unauthorized(self):
        response = self.client.get('/keystone-test/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_with_authorization_headers_without_aws_returns_unauthorized(self):
        response = self.client.get('/keystone-test/', HTTP_AUTHORIZATION='BANANA')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_without_date_header_returns_unauthorized(self):
        response = self.client.get('/keystone-test/', HTTP_AUTHORIZATION='AWS dd:ddd')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_signed_returns_authorized(self):
        from plugins.keystone.service import KeystoneService

        def validate_rest_request(*args, **kwargs):
            from django.contrib.auth.models import User
            return User(), 'admin'
        KeystoneService.validate_rest_request = validate_rest_request

        date = formatdate()
        string_to_sign = '\n'.join(('GET', '/keystone-test/', '', '', date))
        auth = 'AWS %s:%s' % (self.access_key, self.hmac_sha1(string_to_sign))
        response = self.client.get('/keystone-test/', HTTP_AUTHORIZATION=auth, HTTP_DATE=date)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_invalid_signature_returns_unauthorized(self):
        string_to_sign = '\n'.join(('GET', '/keystone-test/', '', '', formatdate()))
        auth = 'AWS %s:%s' % ('invalid accesskey', self.hmac_sha1(string_to_sign))
        response = self.client.get('/keystone-test/', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
