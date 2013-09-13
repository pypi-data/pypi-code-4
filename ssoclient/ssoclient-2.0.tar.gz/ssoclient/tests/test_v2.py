# Copyright 2013 Canonical Ltd. This software is licensed under
# the GNU Affero General Public License version 3 (see the file
# LICENSE).
import json
import unittest

from datetime import datetime

from mock import (
    MagicMock,
    patch,
)
from requests.models import Response

from ssoclient.v2 import errors
from ssoclient.v2.http import (
    ERRORS,
    ApiSession,
    V2ApiClientResponse,
    process_response,
)
from ssoclient.v2.client import V2ApiClient, datetime_from_string


class DateTimeFromStringTestCase(unittest.TestCase):
    """Test for the datetime parser."""

    def test_parses_with_millis(self):
        result = datetime_from_string('2013-09-07T00:44:09.33')
        self.assertEqual(result, datetime(2013, 9, 7, 0, 44, 9, 330000))

    def test_parses_no_millis(self):
        result = datetime_from_string('2013-09-07T00:44:09')
        self.assertEqual(result, datetime(2013, 9, 7, 0, 44, 9))


class V2ApiClientResponseTestCase(unittest.TestCase):
    """Tests for the Response object returned on API calls."""

    def test_creation(self):
        content = object()
        response = V2ApiClientResponse(203, content)

        self.assertEqual(response.status_code, 203)
        self.assertIs(response.content, content)

    def test_always_ok(self):
        response = V2ApiClientResponse(500, '')
        self.assertTrue(response.ok)

    def test_json_is_content(self):
        content = object()
        response = V2ApiClientResponse(203, content)

        self.assertIs(response.json(), content)


class ApiSessionTestCase(unittest.TestCase):
    """Test for the session used during API calls."""

    @patch('ssoclient.v2.http.requests.Session.request')
    def test_api_session_post(self, mock_request):
        mock_request.return_value = MagicMock(status_code=200)

        api = ApiSession('http://foo.com')
        api.post('/foo', data=dict(x=1))
        mock_request.assert_called_one_with(
            'POST',
            'http://foo.com/foo',
            data={'x': 1}
        )

    @patch('ssoclient.v2.http.requests.Session.request')
    def test_api_session_get(self, mock_request):
        mock_request.return_value = MagicMock(status_code=200)

        api = ApiSession('http://foo.com')
        api.get('/foo', params=dict(x=1))
        mock_request.request.assert_called_one_with(
            'POST',
            'http://foo.com/foo',
            params={'x': 1}
        )


def mock_response(status_code=200, content=None, json_dump=True):
    response = Response()
    response.status_code = status_code
    if content is not None and json_dump:
        content = json.dumps(content)
    response._content = content
    return response


class ProcessResponseTestCase(unittest.TestCase):
    """Tests for the decorator "process_response"."""

    @process_response
    def do_test(self, response):
        return response

    def test_error_code_raises_correct_exception(self):
        for code, exc in ERRORS.iteritems():
            response = mock_response(exc.status_code, dict(code=code))
            with self.assertRaises(exc):
                self.do_test(response)

    def test_400_no_json_content_raises_client_error(self):
        response = mock_response(status_code=400)
        with self.assertRaises(errors.ClientError) as e:
            self.do_test(response)
            self.assertEqual(e.msg, "No error code in response")

    def test_500_no_json_content_raises_server_error(self):
        response = mock_response(status_code=500)
        with self.assertRaises(errors.ServerError) as e:
            self.do_test(response)
            self.assertEqual(e.msg, "No error code in response")

    def test_400_unknown_code_raises_client_error(self):
        response = mock_response(400, dict(code="UNKNOWN_CODE"))
        with self.assertRaises(errors.ClientError) as e:
            self.do_test(response)
            self.assertIn(e.msg, "UNKNOWN_CODE")

    def test_500_unknown_code_raises_server_error(self):
        response = mock_response(500, dict(code="UNKNOWN_CODE"))
        with self.assertRaises(errors.ServerError) as e:
            self.do_test(response)
            self.assertIn(e.msg, "UNKNOWN_CODE")

    def test_success_returns(self):
        expected = dict(foo='bar', zaraza=42)
        response = mock_response(status_code=200, content=expected)

        result = self.do_test(response)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content, expected)


class V2ClientApiTestCase(unittest.TestCase):

    email = 'foo@foo.com'

    def setUp(self):
        super(V2ClientApiTestCase, self).setUp()
        self.client = V2ApiClient('http://foo.com')

        p = patch('ssoclient.v2.http.requests.Session.request')
        self.mock_request = p.start()
        self.addCleanup(p.stop)

        p = patch('ssoclient.v2.client.OAuth1')
        self.mock_oauth = p.start()
        self.addCleanup(p.stop)

        self.credentials = dict(
            consumer_key='consumer_key',
            consumer_secret='consumer_secret',
            token_key='token_key',
            token_secret='token_secret',
        )

    def unparsed_account_details(self, expand=False):
        """Unparsed account details as how parse_response returns them."""
        result = {
            'displayname': 'something',
            'email': self.email,
            'emails': [
                {'href': '/api/v2/emails/' + self.email, 'verified': False},
            ],
            'href': '/api/v2/accounts/FeAQLWE',
            'openid': 'FeAQLWE',
            'status': 'Active',
            'verified': False,
            'tokens': [
                {'href': '/api/v2/tokens/oauth/EqEnreoOFJPBOIbcKdwuqtCVZdJ',
                 'token_name': 'api test bis'},
                {'href': '/api/v2/tokens/oauth/TGHuvFlSSVrpqUVjpMBwzbEHfij',
                 'token_name': 'api test'}
            ],
        }
        if expand:
            result['emails'] = [{
                'email': self.email,
                'date_created': '2013-09-12T18:23:51.019',
                'href': '/api/v2/emails/' + self.email,
                'verified': False,
            }]
            result['tokens'] = [
                {'token_name': 'api test bis',
                 'date_updated': '2013-09-12T19:06:11.387',
                 'token_key': 'EqEnreoOFJPBOIbcKdwuqtCVZdJnh',
                 'consumer_secret': 'YuPUIQYYoqJHIUmoxvZvhODNwSYrvl',
                 'href': '/api/v2/tokens/oauth/EqEnreoOFJPBOIbcKdwuqtCVZdJnh',
                 'date_created': '2013-09-12T19:06:11.387',
                 'consumer_key': 'FeAQLWE',
                 'token_secret': 'CnITkuwuhKDBNOocTPICKAsuUZkOcDprgQQhZdXOZE'},
                {'token_name': 'api test',
                 'date_updated': '2013-09-12T18:31:19.468',
                 'token_key': 'TGHuvFlSSVrpqUVjpMBwzbEHfijTCw',
                 'consumer_secret': 'YuPUIQYYoqJHIUmoxvZvhODNwSYrvl',
                 'href': '/api/v2/tokens/oauth/TGHuvFlSSVrpqUVjpMBwzbEHfijTCw',
                 'date_created': '2013-09-12T18:28:17.816',
                 'consumer_key': 'FeAQLWE',
                 'token_secret': 'YcQgfuhpajCphDCnfNNceggfolHsXqdsXWSRufbzqe'},
            ]
        return result

    def unparsed_email_details(self):
        """Unparsed email details as how parse_response returns them."""
        return {
            'date_created': '2013-09-12T18:23:51.019',
            'href': '/api/v2/emails/' + self.email,
            'verified': False,
            'email': 'foo@a.com',
        }

    def unparsed_token_details(self):
        """Unparsed token details as how parse_response returns them."""
        return {
            'date_created': '2013-09-12T18:28:17.816',
            'date_updated': '2013-09-12T18:31:19.468',
            'consumer_key': 'FeAQLWE',
            'consumer_secret': 'YuPUIQYYoqJHIUmoxvZvhODNwSYrvl',
            'href': '/api/v2/tokens/oauth/TGHuvFlSSVrpqUVjpMBwzbEHfijTCwXtRi',
            'openid': 'FeAQLWE',
            'token_key': 'TGHuvFlSSVrpqUVjpMBwzbEHfijTCwXtRiGca',
            'token_name': 'api test',
            'token_secret': 'YcQgfuhpajCphDCnfNNceggfolHsXqdsXWSRufbzqeRJvEP',
        }

    def assert_unicode_credentials(self, credentials):
        self.mock_oauth.assert_called_once_with(
            credentials['consumer_key'], credentials['consumer_secret'],
            credentials['token_key'], credentials['token_secret'],
        )
        self.assertTrue(all(isinstance(val, unicode) for
                            val in self.mock_oauth.call_args[0]))


class RegisterV2ClientApiTestCase(V2ClientApiTestCase):

    def assert_invalid_response(self, status_code, ExceptionClass):
        # Test the client can handle an error response that doesn't have
        # a json body - ideally our server will never send these
        response = mock_response(
            status_code=status_code, content='some error message',
            json_dump=False)

        self.mock_request.return_value = response
        with self.assertRaises(ExceptionClass) as ctx:
            self.client.login(email='blah')

        if status_code >= 500:
            self.assertIn('some error message', str(ctx.exception))

    def test_register_invalid_data(self):
        self.mock_request.return_value = mock_response(
            400, dict(code="INVALID_DATA"))
        with self.assertRaises(errors.InvalidData):
            self.client.register(email='blah')

    def test_register_captcha_required(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="CAPTCHA_REQUIRED"))
        with self.assertRaises(errors.CaptchaRequired):
            self.client.register(email='blah')

    def test_register_captcha_failed(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="CAPTCHA_FAILURE"))
        with self.assertRaises(errors.CaptchaFailure):
            self.client.register(email='blah')

    def test_register_captcha_error(self):
        self.mock_request.return_value = mock_response(
            502, dict(code="CAPTCHA_ERROR"))
        with self.assertRaises(errors.CaptchaError):
            self.client.register(email='blah')

    def test_register_already_registered(self):
        self.mock_request.return_value = mock_response(
            409, dict(code="ALREADY_REGISTERED"))
        with self.assertRaises(errors.AlreadyRegistered):
            self.client.register(email='blah')

    def test_register_success(self):
        content = self.unparsed_account_details()
        self.mock_request.return_value = mock_response(
            status_code=201, content=content)

        response = self.client.register(email='blah')

        self.assertEqual(response, content)

    def test_invalid_response_400(self):
        self.assert_invalid_response(400, errors.ClientError)

    def test_invalid_response_500(self):
        self.assert_invalid_response(500, errors.ServerError)


class LoginV2ClientApiTestCase(V2ClientApiTestCase):

    def test_login_invalid_data(self):
        self.mock_request.return_value = mock_response(
            400, dict(code="INVALID_DATA"))
        with self.assertRaises(errors.InvalidData):
            self.client.login(email='blah')

    def test_login_account_suspended(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="ACCOUNT_SUSPENDED"))
        with self.assertRaises(errors.AccountSuspended):
            self.client.login(email='blah')

    def test_login_account_deactivated(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="ACCOUNT_DEACTIVATED"))
        with self.assertRaises(errors.AccountDeactivated):
            self.client.login(email='blah')

    def test_login_invalid_credentials(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="INVALID_CREDENTIALS"))
        with self.assertRaises(errors.InvalidCredentials):
            self.client.login(email='blah')

    def test_login_password_policy_error(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="PASSWORD_POLICY_ERROR"))
        with self.assertRaises(errors.PasswordPolicyError):
            self.client.login(email='blah')

    def test_login_twofactor_required(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="TWOFACTOR_REQUIRED"))
        with self.assertRaises(errors.TwoFactorRequired):
            self.client.login(email='blah')

    def test_login_twofactor_failure(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="TWOFACTOR_FAILURE"))
        with self.assertRaises(errors.TwoFactorFailure):
            self.client.login(email='blah')

    def test_login_account_locked(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="ACCOUNT_LOCKED"))
        with self.assertRaises(errors.AccountLocked):
            self.client.login(email='blah')

    def test_login_email_invalidated(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="EMAIL_INVALIDATED"))
        with self.assertRaises(errors.EmailInvalidated):
            self.client.login(email='blah')

    def test_login_success(self):
        content = self.unparsed_token_details()
        self.mock_request.return_value = mock_response(
            status_code=200, content=content)
        response = self.client.login(email='blah', password='ble')

        expected = content.copy()
        expected['date_created'] = datetime(2013, 9, 12, 18, 28, 17, 816000)
        expected['date_updated'] = datetime(2013, 9, 12, 18, 31, 19, 468000)
        self.assertEqual(response, expected)


class PasswordResetV2ClientApiTestCase(V2ClientApiTestCase):

    def test_request_password_reset(self):
        content = {'email': self.email}
        self.mock_request.return_value = mock_response(
            status_code=201, content=content)

        response = self.client.request_password_reset(self.email)

        self.assertEqual(response, content)
        self.mock_request.assert_called_once_with(
            'POST', 'http://foo.com/tokens/password',
            headers={'Content-Type': 'application/json'},
            data='{"token": null, "email": "%s"}' % self.email,
        )

    def test_request_password_reset_without_email(self):
        self.mock_request.return_value = mock_response(
            400, dict(code="INVALID_DATA"))
        with self.assertRaises(errors.InvalidData):
            self.client.request_password_reset(None)

    def test_request_password_reset_with_empty_email(self):
        self.mock_request.return_value = mock_response(
            400, dict(code="INVALID_DATA"))
        with self.assertRaises(errors.InvalidData):
            self.client.request_password_reset('')

    def test_request_password_reset_with_token(self):
        content = {'email': self.email}
        self.mock_request.return_value = mock_response(
            status_code=201, content=content)
        response = self.client.request_password_reset(
            self.email, 'token1234')

        self.assertEqual(response, content)
        self.assertEqual(self.mock_request.call_args, [
            ('POST', 'http://foo.com/tokens/password'),
            {'headers': {'Content-Type': 'application/json'},
             'data': '{"token": "token1234", "email": "%s"}' % self.email},
        ])

    def test_request_password_reset_for_suspended_account(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="ACCOUNT_SUSPENDED"))
        with self.assertRaises(errors.AccountSuspended):
            self.client.request_password_reset(self.email)

    def test_request_password_reset_for_deactivated_account(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="ACCOUNT_DEACTIVATED"))
        with self.assertRaises(errors.AccountDeactivated):
            self.client.request_password_reset(self.email)

    def test_request_password_reset_with_invalid_email(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="RESOURCE_NOT_FOUND"))
        with self.assertRaises(errors.ResourceNotFound):
            self.client.request_password_reset(self.email)

    def test_request_password_reset_not_allowed(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="CAN_NOT_RESET_PASSWORD"))
        with self.assertRaises(errors.CanNotResetPassword):
            self.client.request_password_reset(self.email)

    def test_request_password_reset_with_invalidated_email(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="EMAIL_INVALIDATED"))
        with self.assertRaises(errors.EmailInvalidated):
            self.client.request_password_reset(self.email)

    def test_request_password_reset_with_too_many_tokens(self):
        self.mock_request.return_value = mock_response(
            403, dict(code="TOO_MANY_TOKENS"))
        with self.assertRaises(errors.TooManyTokens):
            self.client.request_password_reset(self.email)


class AccountDetailsV2ClientApiTestCase(V2ClientApiTestCase):

    def test_account_details(self):
        content = self.unparsed_account_details()
        self.mock_request.return_value = mock_response(
            status_code=200, content=content)
        response = self.client.account_details('some_openid', self.credentials)
        self.assert_unicode_credentials(self.credentials)

        oauth1 = self.mock_oauth.return_value
        self.mock_request.assert_called_once_with(
            'GET', 'http://foo.com/accounts/some_openid?expand=false',
            auth=oauth1, headers={}, allow_redirects=True,
        )

        self.assertEqual(response, content)

    def test_account_details_expanded(self):
        content = self.unparsed_account_details(expand=True)
        self.mock_request.return_value = mock_response(
            status_code=200, content=content)
        response = self.client.account_details(
            'some_openid', self.credentials, expand=True)
        self.assert_unicode_credentials(self.credentials)

        oauth1 = self.mock_oauth.return_value
        self.mock_request.assert_called_once_with(
            'GET', 'http://foo.com/accounts/some_openid?expand=true',
            auth=oauth1, headers={}, allow_redirects=True,
        )

        expected = content.copy()
        # dates are parsed
        t = expected['tokens'][0]
        t['date_updated'] = datetime(2013, 9, 12, 19, 6, 11, 387000)
        t['date_created'] = datetime(2013, 9, 12, 19, 6, 11, 387000)

        t = expected['tokens'][1]
        t['date_updated'] = datetime(2013, 9, 12, 18, 31, 19, 468000)
        t['date_created'] = datetime(2013, 9, 12, 18, 28, 17, 816000)

        e = expected['emails'][0]
        e['date_created'] = datetime(2013, 9, 12, 18, 23, 51, 19000)

        self.assertEqual(response, expected)

    def test_account_details_anonymous(self):
        content = {
            'href': '/api/v2/accounts/FeAQLWE',
            'openid': 'FeAQLWE',
            'verified': False,
        }
        self.mock_request.return_value = mock_response(
            status_code=200, content=content)
        response = self.client.account_details('some_openid')
        self.mock_request.assert_called_once_with(
            'GET', 'http://foo.com/accounts/some_openid?expand=false',
            auth=None, headers={}, allow_redirects=True,
        )
        self.assertEqual(response, content)


class EmailsV2ClientApiTestCase(V2ClientApiTestCase):

    def test_details(self):
        content = self.unparsed_email_details()
        self.mock_request.return_value = mock_response(
            status_code=200, content=content)

        response = self.client.email_details('email', self.credentials)
        self.assert_unicode_credentials(self.credentials)

        oauth1 = self.mock_oauth.return_value
        self.mock_request.assert_called_once_with(
            'GET', 'http://foo.com/emails/email', auth=oauth1,
            headers={}, allow_redirects=True,
        )

        expected = content.copy()
        expected['date_created'] = datetime(2013, 9, 12, 18, 23, 51, 19000)
        self.assertEqual(response, expected)

    def test_details_invalid_credentials(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="INVALID_CREDENTIALS"))
        with self.assertRaises(errors.InvalidCredentials):
            self.client.email_details('blah', {})

    def test_details_not_found(self):
        self.mock_request.return_value = mock_response(
            404, dict(code="RESOURCE_NOT_FOUND"))
        with self.assertRaises(errors.ResourceNotFound):
            self.client.email_details('blah', {})

    def test_delete(self):
        self.mock_request.return_value = mock_response(
            status_code=204, content='')

        response = self.client.email_delete('email', self.credentials)
        self.assert_unicode_credentials(self.credentials)

        oauth1 = self.mock_oauth.return_value
        self.mock_request.assert_called_once_with(
            'DELETE', 'http://foo.com/emails/email', auth=oauth1,
            headers={},
        )

        self.assertEqual(response, True)

    def test_delete_invalid_credentials(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="INVALID_CREDENTIALS"))
        with self.assertRaises(errors.InvalidCredentials):
            self.client.email_delete('blah', {})

    def test_delete_not_found(self):
        self.mock_request.return_value = mock_response(
            404, dict(code="RESOURCE_NOT_FOUND"))
        with self.assertRaises(errors.ResourceNotFound):
            self.client.email_delete('blah', {})


class TokensV2ClientApiTestCase(V2ClientApiTestCase):

    def test_details(self):
        content = self.unparsed_token_details()
        self.mock_request.return_value = mock_response(
            status_code=200, content=content)

        response = self.client.token_details('token_key', self.credentials)
        self.assert_unicode_credentials(self.credentials)

        oauth1 = self.mock_oauth.return_value
        self.mock_request.assert_called_once_with(
            'GET', 'http://foo.com/tokens/oauth/token_key', auth=oauth1,
            headers={}, allow_redirects=True,
        )

        expected = content.copy()
        expected['date_updated'] = datetime(2013, 9, 12, 18, 31, 19, 468000)
        expected['date_created'] = datetime(2013, 9, 12, 18, 28, 17, 816000)
        self.assertEqual(response, expected)

    def test_details_invalid_credentials(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="INVALID_CREDENTIALS"))
        with self.assertRaises(errors.InvalidCredentials):
            self.client.token_details('blah', {})

    def test_details_not_found(self):
        self.mock_request.return_value = mock_response(
            404, dict(code="RESOURCE_NOT_FOUND"))
        with self.assertRaises(errors.ResourceNotFound):
            self.client.token_details('blah', {})

    def test_delete(self):
        self.mock_request.return_value = mock_response(
            status_code=204, content='')

        response = self.client.token_delete('token_key', self.credentials)
        self.assert_unicode_credentials(self.credentials)

        oauth1 = self.mock_oauth.return_value
        self.mock_request.assert_called_once_with(
            'DELETE', 'http://foo.com/tokens/oauth/token_key', auth=oauth1,
            headers={},
        )

        self.assertEqual(response, True)

    def test_delete_invalid_credentials(self):
        self.mock_request.return_value = mock_response(
            401, dict(code="INVALID_CREDENTIALS"))
        with self.assertRaises(errors.InvalidCredentials):
            self.client.token_delete('blah', {})

    def test_delete_not_found(self):
        self.mock_request.return_value = mock_response(
            404, dict(code="RESOURCE_NOT_FOUND"))
        with self.assertRaises(errors.ResourceNotFound):
            self.client.token_delete('blah', {})


class ValidateRequestV2ClientApiTestCase(V2ClientApiTestCase):

    def test_valid_request(self):
        self.mock_request.return_value = mock_response(200, dict(is_valid=True))
        result = self.client.validate_request(
            http_url='foo', http_method='GET', authorization='123456789')

        self.assertEqual(result, {'is_valid': True})

    def test_invalid_request(self):
        self.mock_request.return_value = mock_response(200, dict(is_valid=False))
        result = self.client.validate_request(
            http_url='foo', http_method='GET', authorization='123456789')

        self.assertEqual(result, {'is_valid': False})
